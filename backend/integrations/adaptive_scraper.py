"""
Adaptive Web Scraper
====================

A resilient fetch-and-extract helper inspired by the "self-adjusting scraper"
tools (Scrapling, browser-use): instead of breaking the moment a page's markup
changes, it fetches with retries/backoff and extracts content through a
*cascade* of strategies, returning whatever the most capable available layer
can produce.

Extraction cascade (best available wins, all optional except the last):
1. **Scrapling** — if installed, used directly (adaptive selectors, anti-bot).
2. **BeautifulSoup** — if installed, structured text + links + title.
3. **stdlib HTML parser** — always available; strips tags, pulls <title> and
   <a href>. This guarantees the scraper degrades gracefully on a bare box.

Everything is wrapped so a network error, missing dependency, or malformed page
yields a structured error dict rather than raising. Network access itself is
attempted with ``urllib`` (stdlib) when ``requests`` isn't present.
"""

from __future__ import annotations

import time
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional
from urllib import request as urllib_request
from urllib.error import URLError

try:
    from .base import BaseIntegration
except ImportError:  # pragma: no cover
    from base import BaseIntegration  # type: ignore

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


class _TextExtractor(HTMLParser):
    """Minimal stdlib extractor: title, visible text, and links."""

    _SKIP = {"script", "style", "noscript", "head"}

    def __init__(self) -> None:
        super().__init__()
        self.title: str = ""
        self._in_title = False
        self._skip_depth = 0
        self.text_parts: List[str] = []
        self.links: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Any]) -> None:
        if tag == "title":
            self._in_title = True
        if tag in self._SKIP:
            self._skip_depth += 1
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.links.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in self._SKIP and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data.strip()
        elif self._skip_depth == 0:
            text = data.strip()
            if text:
                self.text_parts.append(text)


def _fetch(url: str, timeout: float, headers: Dict[str, str]) -> str:
    """Fetch raw HTML using requests if available, else urllib."""
    try:
        import requests  # type: ignore

        resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        return resp.text
    except ImportError:
        req = urllib_request.Request(url, headers=headers)
        with urllib_request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (trusted dev use)
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")


def _extract(html: str) -> Dict[str, Any]:
    """Run the extraction cascade and return structured content."""
    # 1) Scrapling, if available.
    try:
        from scrapling import Adaptor  # type: ignore

        page = Adaptor(html)
        text = page.get_all_text() if hasattr(page, "get_all_text") else page.text
        return {"engine": "scrapling", "title": getattr(page, "title", "") or "", "text": text, "links": []}
    except Exception:
        pass

    # 2) BeautifulSoup, if available.
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = soup.title.get_text(strip=True) if soup.title else ""
        text = "\n".join(line for line in (t.strip() for t in soup.get_text().splitlines()) if line)
        links = [a["href"] for a in soup.find_all("a", href=True)]
        return {"engine": "beautifulsoup", "title": title, "text": text, "links": links}
    except ImportError:
        pass

    # 3) stdlib fallback -- always works.
    parser = _TextExtractor()
    parser.feed(html)
    return {
        "engine": "stdlib",
        "title": parser.title,
        "text": "\n".join(parser.text_parts),
        "links": parser.links,
    }


class AdaptiveScraper(BaseIntegration):
    """Fetch + extract with retries and a graceful extraction cascade."""

    def __init__(self, retries: int = 3, timeout: float = 15.0, backoff: float = 1.5):
        super().__init__(name="AdaptiveScraper")
        self.retries = retries
        self.timeout = timeout
        self.backoff = backoff

    def can_handle(self, intent: str) -> bool:
        return any(k in intent.lower() for k in ("scrape", "extract", "fetch page"))

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action in ("scrape", "fetch"):
            return self.scrape(params["url"], max_chars=params.get("max_chars", 5000))
        return {"status": "error", "error": f"Unknown scraper action: {action}"}

    def scrape(self, url: str, max_chars: int = 5000, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Fetch ``url`` and return extracted title/text/links, with retries."""
        if not url.startswith(("http://", "https://")):
            return {"status": "error", "error": "URL must start with http:// or https://"}

        merged_headers = dict(_DEFAULT_HEADERS)
        if headers:
            merged_headers.update(headers)

        last_error = ""
        for attempt in range(1, self.retries + 1):
            try:
                html = _fetch(url, self.timeout, merged_headers)
            except (URLError, OSError, Exception) as exc:  # noqa: BLE001 - degrade gracefully
                last_error = str(exc)
                if attempt < self.retries:
                    time.sleep(self.backoff ** attempt)
                continue

            extracted = _extract(html)
            text = extracted.get("text", "") or ""
            self.log_to_memory(f"Scraped {url}", {"engine": extracted.get("engine"), "url": url})
            return {
                "status": "ok",
                "url": url,
                "engine": extracted.get("engine"),
                "title": extracted.get("title", ""),
                "text": text[:max_chars],
                "truncated": len(text) > max_chars,
                "links": extracted.get("links", [])[:50],
                "attempts": attempt,
            }

        return {"status": "error", "url": url, "error": f"Failed after {self.retries} attempts: {last_error}"}


# Module-level singleton.
adaptive_scraper = AdaptiveScraper()
