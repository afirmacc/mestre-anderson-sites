#!/usr/bin/env python3
"""Audita metadados e respostas de páginas públicas listadas em um sitemap XML."""

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import gzip
from html.parser import HTMLParser
from io import BytesIO
import json
import sys
from urllib.error import HTTPError
from urllib.parse import quote, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

MAX_HTML = 2_000_000
MAX_SITEMAP = 50_000_000
MAX_SITEMAPS = 100


def site_key(url):
    """Iguala www e portas padrão, mas mantém portas não padrão separadas."""
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError(f"URL HTTP(S) inválida: {url}")
    host = parsed.hostname.lower().removeprefix("www.")
    port = parsed.port
    if (parsed.scheme, port) in (("http", 80), ("https", 443)):
        port = None
    return host, port


def request_url(url):
    """Converte o caminho e a consulta de uma IRI para uma URL HTTP válida."""
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc,
                       quote(parsed.path, safe="/%:@!$&'()*+,;=-._~"),
                       quote(parsed.query, safe="/%?:@!$&'()*+,;=-._~"), ""))


class SiteRedirects(HTTPRedirectHandler):
    def __init__(self, allowed_site):
        self.allowed_site = allowed_site

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        try:
            permitted = site_key(newurl) == self.allowed_site
            secure = not (urlsplit(request.full_url).scheme == "https" and
                          urlsplit(newurl).scheme == "http")
        except ValueError:
            permitted, secure = False, False
        if not (permitted and secure):
            raise HTTPError(request.full_url, code,
                            f"redirecionamento fora do site ou para HTTP: {newurl}",
                            headers, fp)
        return super().redirect_request(request, fp, code, msg, headers, newurl)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.headings = []
        self.description = ""
        self.canonicals = []
        self.images_without_alt = []
        self.robots = ""
        self.lang = ""
        self.current = None
        self.svg_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "svg":
            self.svg_depth += 1
        if self.svg_depth:
            return
        if tag == "html":
            self.lang = attrs.get("lang") or ""
        elif tag == "title":
            self.current = "title"
        elif tag == "h1":
            self.headings.append("")
            self.current = "h1"
        elif tag == "meta":
            name = (attrs.get("name") or "").lower()
            if name == "description":
                self.description = attrs.get("content") or ""
            elif name == "robots":
                self.robots = attrs.get("content") or ""
        elif tag == "link" and "canonical" in (attrs.get("rel") or "").lower().split():
            self.canonicals.append(attrs.get("href") or "")
        elif tag == "img" and "alt" not in attrs:
            self.images_without_alt.append(attrs.get("src", "(sem src)"))

    def handle_endtag(self, tag):
        if tag == "svg" and self.svg_depth:
            self.svg_depth -= 1
        if self.svg_depth:
            return
        if tag in ("title", "h1"):
            self.current = None

    def handle_data(self, text):
        if self.svg_depth:
            return
        if self.current == "title":
            self.title += text
        elif self.current == "h1":
            self.headings[-1] += text


def fetch(url, allowed_site, limit):
    try:
        if site_key(url) != allowed_site:
            raise ValueError("URL fora do site informado")
        request = Request(request_url(url), headers={"User-Agent": "PublicSiteAudit/1.0"})
        with build_opener(SiteRedirects(allowed_site)).open(request, timeout=20) as response:
            return (response.status, response.geturl(), response.read(limit + 1),
                    response.headers.get_content_charset() or "utf-8", "")
    except Exception as error:
        return getattr(error, "code", 0), url, b"", "utf-8", f"{type(error).__name__}: {error}"


def inspect(url, allowed_site):
    status, final_url, data, charset, error = fetch(url, allowed_site, MAX_HTML)
    page = Page()
    issues = []
    if status != 200:
        issues.append(f"HTTP {status}: {error}" if error else f"HTTP {status}")
    if len(data) > MAX_HTML:
        issues.append("HTML acima do limite de 2 MB")
    if final_url != request_url(url):
        issues.append(f"redireciona para {final_url}")
    if status == 200 and len(data) <= MAX_HTML:
        try:
            page.feed(data.decode(charset, "replace"))
        except Exception as parse_error:
            issues.append(f"HTML não pôde ser lido: {parse_error}")
    if status == 200 and len(data) <= MAX_HTML and not any(
            issue.startswith("HTML não pôde") for issue in issues):
        if not page.title.strip():
            issues.append("sem título")
        if not page.description.strip():
            issues.append("sem descrição")
        if len(page.headings) != 1:
            issues.append(f"{len(page.headings)} H1")
        try:
            canonical_urls = [request_url(urljoin(final_url, item))
                              for item in page.canonicals if item]
        except ValueError as canonical_error:
            canonical_urls = []
            issues.append(f"canônica inválida: {canonical_error}")
        if len(page.canonicals) != 1 or not page.canonicals[0] or canonical_urls != [final_url]:
            issues.append(f"canônica {page.canonicals!r}")
        if page.images_without_alt:
            issues.append(f"{len(page.images_without_alt)} imagem(ns) sem alt")
        if "noindex" in page.robots.lower():
            issues.append("noindex em URL do sitemap")
        if not page.lang:
            issues.append("sem idioma no HTML")
    return {
        "url": url,
        "status": status,
        "title": page.title.strip(),
        "description": page.description.strip(),
        "h1": [x.strip() for x in page.headings],
        "canonical": page.canonicals,
        "lang": page.lang,
        "issues": issues,
    }


def sitemap_urls(url, allowed_site, seen=None):
    seen = set() if seen is None else seen
    if url in seen:
        return [], [], []
    if len(seen) >= MAX_SITEMAPS:
        raise ValueError(f"limite de {MAX_SITEMAPS} sitemaps atingido")
    seen.add(url)
    status, _, data, _, error = fetch(url, allowed_site, MAX_SITEMAP)
    if status != 200:
        raise ValueError(f"sitemap não respondeu 200: {url} (HTTP {status}: {error})")
    if len(data) > MAX_SITEMAP:
        raise ValueError(f"sitemap acima do limite de {MAX_SITEMAP} bytes: {url}")
    if url.endswith(".gz") or data.startswith(b"\x1f\x8b"):
        try:
            with gzip.GzipFile(fileobj=BytesIO(data)) as compressed:
                data = compressed.read(MAX_SITEMAP + 1)
        except (OSError, EOFError) as compression_error:
            raise ValueError(f"sitemap gzip inválido em {url}: {compression_error}") from compression_error
        if len(data) > MAX_SITEMAP:
            raise ValueError(f"sitemap descompactado acima de {MAX_SITEMAP} bytes: {url}")
    xml_markup = data.replace(b"\x00", b"").upper()
    if b"<!DOCTYPE" in xml_markup or b"<!ENTITY" in xml_markup:
        raise ValueError(f"sitemap com DTD ou entidade não permitido: {url}")
    try:
        sitemap = ElementTree.fromstring(data)
    except ElementTree.ParseError as error:
        raise ValueError(f"sitemap XML inválido em {url}: {error}") from error
    kind = sitemap.tag.rsplit("}", 1)[-1]
    locations, invalid = [], []
    for node in sitemap.iter():
        if node.tag.rsplit("}", 1)[-1] == "loc" and node.text:
            raw = node.text.strip()
            try:
                locations.append(urljoin(url, raw))
            except ValueError:
                invalid.append(raw)

    def local_url(item):
        try:
            return site_key(item) == allowed_site
        except ValueError:
            return False

    external = [item for item in locations if not local_url(item)]
    local = [item for item in locations if local_url(item)]
    if kind == "urlset":
        return local, external, invalid
    if kind != "sitemapindex":
        raise ValueError(f"raiz XML não é urlset nem sitemapindex: {url}")
    pages = []
    for child in local:
        child_pages, child_external, child_invalid = sitemap_urls(child, allowed_site, seen)
        pages.extend(child_pages)
        external.extend(child_external)
        invalid.extend(child_invalid)
    return pages, external, invalid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="URL inicial do site público, por exemplo https://example.com")
    parser.add_argument("--sitemap", help="URL do sitemap (padrão: /sitemap.xml)")
    parser.add_argument("--max-pages", type=int, default=200)
    parser.add_argument("--json", action="store_true", help="Saída JSON para análise posterior")
    parser.add_argument("--fail-on-issues", action="store_true",
                        help="Retorna código 1 quando houver problemas ou duplicados")
    args = parser.parse_args()
    if args.max_pages < 1:
        parser.error("--max-pages deve ser positivo")
    base = args.base_url.rstrip("/")
    try:
        allowed_site = site_key(base)
    except ValueError as error:
        parser.error(str(error))
    sitemap_url = args.sitemap or base + "/sitemap.xml"
    try:
        found, external, invalid = sitemap_urls(sitemap_url, allowed_site)
    except ValueError as error:
        parser.error(str(error))
    if not found:
        parser.error("nenhuma URL do site foi encontrada no sitemap; confira domínio, www e porta")
    urls = list(dict.fromkeys(found))
    truncated = len(urls) > args.max_pages
    urls = urls[: args.max_pages]
    with ThreadPoolExecutor(max_workers=6) as pool:
        pages = list(pool.map(lambda url: inspect(url, allowed_site), urls))
    duplicates = defaultdict(list)
    for field in ("title", "description"):
        values = defaultdict(list)
        for page in pages:
            if page[field]:
                values[page[field]].append(page["url"])
        duplicates[field] = [links for links in values.values() if len(links) > 1]
    result = {
        "sitemap": sitemap_url,
        "listed_urls": len(found),
        "audited_urls": len(pages),
        "external_urls": external,
        "invalid_urls": invalid,
        "truncated": truncated,
        "duplicates": duplicates,
        "pages": pages,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        problems = [(page["url"], issue) for page in pages for issue in page["issues"]]
        print(f"Sitemap: {sitemap_url} | listadas: {len(found)} | auditadas: {len(pages)}")
        print(f"Problemas por página: {len(problems)} | URLs externas: {len(external)} | URLs inválidas: {len(invalid)} | corte aplicado: {truncated}")
        for item in invalid:
            print(f"- URL inválida no sitemap: {item}")
        for url, issue in problems:
            print(f"- {url}: {issue}")
        for field, groups in duplicates.items():
            for links in groups:
                print(f"- {field} duplicado: {', '.join(links)}")
    if args.fail_on_issues and (invalid or any(page["issues"] for page in pages) or
                                any(duplicates.values())):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
