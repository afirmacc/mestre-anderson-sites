#!/usr/bin/env python3
"""Audita metadados e respostas de páginas públicas listadas em um sitemap XML."""

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree


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

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang", "")
        elif tag == "title":
            self.current = "title"
        elif tag == "h1":
            self.headings.append("")
            self.current = "h1"
        elif tag == "meta":
            name = attrs.get("name", "").lower()
            if name == "description":
                self.description = attrs.get("content", "")
            elif name == "robots":
                self.robots = attrs.get("content", "")
        elif tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonicals.append(attrs.get("href", ""))
        elif tag == "img" and "alt" not in attrs:
            self.images_without_alt.append(attrs.get("src", "(sem src)"))

    def handle_endtag(self, tag):
        if tag in ("title", "h1"):
            self.current = None

    def handle_data(self, text):
        if self.current == "title":
            self.title += text
        elif self.current == "h1":
            self.headings[-1] += text


def fetch(url):
    try:
        request = Request(url, headers={"User-Agent": "PublicSiteAudit/1.0"})
        with urlopen(request, timeout=20) as response:
            return response.status, response.geturl(), response.read(2_000_001)
    except (HTTPError, URLError, TimeoutError) as error:
        return getattr(error, "code", 0), url, str(error).encode()


def inspect(url):
    status, final_url, data = fetch(url)
    page = Page()
    if status == 200 and len(data) <= 2_000_000:
        page.feed(data.decode("utf-8", "replace"))
    issues = []
    if status != 200:
        issues.append(f"HTTP {status}")
    if len(data) > 2_000_000:
        issues.append("HTML acima do limite de 2 MB")
    if final_url != url:
        issues.append(f"redireciona para {final_url}")
    if status == 200:
        if not page.title.strip():
            issues.append("sem título")
        if not page.description.strip():
            issues.append("sem descrição")
        if len(page.headings) != 1:
            issues.append(f"{len(page.headings)} H1")
        if page.canonicals != [url]:
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


def sitemap_urls(url, host, seen=None):
    seen = set() if seen is None else seen
    if url in seen or len(seen) >= 100:
        return [], []
    seen.add(url)
    status, _, data = fetch(url)
    if status != 200:
        raise ValueError(f"sitemap não respondeu 200: {url} (HTTP {status})")
    try:
        sitemap = ElementTree.fromstring(data)
    except ElementTree.ParseError as error:
        raise ValueError(f"sitemap XML inválido em {url}: {error}") from error
    kind = sitemap.tag.rsplit("}", 1)[-1]
    locations = [urljoin(url, node.text.strip()) for node in sitemap.iter()
                 if node.tag.rsplit("}", 1)[-1] == "loc" and node.text]
    external = [item for item in locations if urlsplit(item).netloc != host]
    local = [item for item in locations if urlsplit(item).netloc == host]
    if kind == "urlset":
        return local, external
    if kind != "sitemapindex":
        raise ValueError(f"raiz XML não é urlset nem sitemapindex: {url}")
    pages = []
    for child in local:
        child_pages, child_external = sitemap_urls(child, host, seen)
        pages.extend(child_pages)
        external.extend(child_external)
    return pages, external


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="URL inicial do site público, por exemplo https://example.com")
    parser.add_argument("--sitemap", help="URL do sitemap (padrão: /sitemap.xml)")
    parser.add_argument("--max-pages", type=int, default=200)
    parser.add_argument("--json", action="store_true", help="Saída JSON para análise posterior")
    args = parser.parse_args()
    if args.max_pages < 1:
        parser.error("--max-pages deve ser positivo")
    base = args.base_url.rstrip("/")
    if urlsplit(base).scheme not in ("http", "https"):
        parser.error("base_url precisa começar com http:// ou https://")
    sitemap_url = args.sitemap or base + "/sitemap.xml"
    try:
        found, external = sitemap_urls(sitemap_url, urlsplit(base).netloc)
    except ValueError as error:
        parser.error(str(error))
    urls = list(dict.fromkeys(found))
    truncated = len(urls) > args.max_pages
    urls = urls[: args.max_pages]
    with ThreadPoolExecutor(max_workers=6) as pool:
        pages = list(pool.map(inspect, urls))
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
        "truncated": truncated,
        "duplicates": duplicates,
        "pages": pages,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        problems = [(page["url"], issue) for page in pages for issue in page["issues"]]
        print(f"Sitemap: {sitemap_url} | listadas: {len(found)} | auditadas: {len(pages)}")
        print(f"Problemas por página: {len(problems)} | URLs externas: {len(external)} | corte aplicado: {truncated}")
        for url, issue in problems:
            print(f"- {url}: {issue}")
        for field, groups in duplicates.items():
            for links in groups:
                print(f"- {field} duplicado: {', '.join(links)}")


if __name__ == "__main__":
    main()
