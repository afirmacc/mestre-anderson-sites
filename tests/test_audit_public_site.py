"""Casos de regressão do auditor, sem serviços externos."""

import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
from pathlib import Path
import subprocess
import sys
import threading
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_public_site.py"
spec = importlib.util.spec_from_file_location("audit_public_site", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        root = f"http://localhost:{self.server.server_port}"
        if self.path == "/sitemap.xml":
            body = ("<urlset><url><loc>" + root + "/boa</loc></url>"
                    "<url><loc>" + root + "/acentuação</loc></url>"
                    "<url><loc>" + root + "/incompleta</loc></url>"
                    "<url><loc>http://[x</loc></url></urlset>").encode()
            kind = "application/xml"
        elif self.path == "/sitemap.xml.gz":
            body = gzip.compress(("<urlset><url><loc>" + root +
                                  "/boa</loc></url></urlset>").encode())
            kind = "application/gzip"
        elif self.path == "/sitemap-dtd.xml":
            body = b'<!DOCTYPE urlset [<!ENTITY x "test">]><urlset></urlset>'
            kind = "application/xml"
        elif self.path == "/sitemap-dtd-utf16.xml":
            body = '<!DOCTYPE urlset [<!ENTITY x "test">]><urlset></urlset>'.encode("utf-16")
            kind = "application/xml"
        elif self.path == "/boa":
            body = ("<html lang=pt-BR><head><svg><title>Ícone</title></svg>"
                    "<title>Página boa</title><meta name=description content=Resumo>"
                    "<link rel=canonical href=/boa></head><body><h1>Título</h1></body></html>").encode()
            kind = "text/html; charset=utf-8"
        elif self.path == "/incompleta":
            body = ("<html lang=pt-BR><head><title>Incompleta</title>"
                    "<meta name><link rel href=/x></head><body><h1>Oi</h1></body></html>").encode()
            kind = "text/html"
        elif self.path == "/acentua%C3%A7%C3%A3o":
            body = ("<html lang=pt-BR><head><title>Português</title>"
                    "<meta name=description content=Resumo>"
                    "<link rel=canonical href=/acentuação></head>"
                    "<body><h1>Configuração</h1></body></html>").encode("utf-8")
            kind = "text/html; charset=utf-8"
        elif self.path in ("/canonica-ruim", "/canonica-vazia"):
            href = "http://[x" if self.path.endswith("ruim") else ""
            body = ("<html lang=pt-BR><head><title>Canônica</title>"
                    "<meta name=description content=Resumo>"
                    f'<link rel=canonical href="{href}"></head>'
                    "<body><h1>Título</h1></body></html>").encode()
            kind = "text/html"
        elif self.path == "/fora":
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{self.server.server_port}/boa")
            self.end_headers()
            return
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("localhost", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.root = f"http://localhost:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_dominios_equivalentes_e_canonica_relativa(self):
        self.assertEqual(audit.site_key("https://www.Example.com:443/a"),
                         audit.site_key("https://example.com/a"))
        page = audit.inspect(self.root + "/boa", audit.site_key(self.root))
        self.assertEqual(page["title"], "Página boa")
        self.assertEqual(page["issues"], [])

    def test_uma_url_ruim_nao_derruba_a_auditoria(self):
        urls, _, invalid = audit.sitemap_urls(self.root + "/sitemap.xml", audit.site_key(self.root))
        self.assertEqual(len(urls), 3)
        self.assertEqual(invalid, ["http://[x"])
        pages = [audit.inspect(url, audit.site_key(self.root)) for url in urls]
        self.assertEqual(pages[0]["issues"], [])
        self.assertEqual(pages[1]["issues"], [])
        self.assertIn("sem descrição", pages[2]["issues"])

    def test_gzip_dtd_e_redirecionamento(self):
        urls, _, _ = audit.sitemap_urls(self.root + "/sitemap.xml.gz", audit.site_key(self.root))
        self.assertEqual(urls, [self.root + "/boa"])
        for path in ("/sitemap-dtd.xml", "/sitemap-dtd-utf16.xml"):
            with self.assertRaisesRegex(ValueError, "DTD"):
                audit.sitemap_urls(self.root + path, audit.site_key(self.root))
        page = audit.inspect(self.root + "/fora", audit.site_key(self.root))
        self.assertIn("redirecionamento fora do site", page["issues"][0])

    def test_canonicas_invalidas_sao_reportadas(self):
        for path in ("/canonica-ruim", "/canonica-vazia"):
            page = audit.inspect(self.root + path, audit.site_key(self.root))
            self.assertTrue(any(issue.startswith("canônica") for issue in page["issues"]))

    def test_saida_json_e_codigo_de_falha(self):
        command = [sys.executable, str(SCRIPT), self.root, "--json", "--fail-on-issues"]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn('"audited_urls": 3', result.stdout)
        self.assertIn('"invalid_urls": [', result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
