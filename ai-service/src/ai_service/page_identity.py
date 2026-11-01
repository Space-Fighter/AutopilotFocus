"""Two ways to identify a page before asking the LLM about it.

  content_key(page)  EXACT identity: "youtube:<video id>" or the normalized URL. Checked first.
  page_text(page)    The page's own words, embedded into the PAGE VECTOR that FAISS searches
                     to find SIMILAR pages already described.

Board: full board frame 14, steps 2-3.
"""

from urllib.parse import urlsplit

from .schemas import PageData


# YOU TYPE #7
def content_key(page: PageData) -> str:
    """Return a stable key for this exact content.

    YouTube video -> "youtube:<video_id>".
    Any other page -> host (lowercase, no "www.") + path (no trailing "/") + the query string
    without tracking parameters (utm_*, fbclid, gclid). The #fragment is dropped.
    e.g. "https://www.Example.com/item/?id=7&utm_source=x#top" -> "example.com/item?id=7"
    """
    raise NotImplementedError("YOU TYPE #7")


def page_text(page: PageData) -> str:
    """The page's own text, joined into one string to embed (no LLM involved)."""
    parts = [page.title, page.meta_description, *page.headings[:3]]
    if page.youtube:
        parts += [page.youtube.channel, page.youtube.category, ", ".join(page.youtube.tags[:10])]
    cleaned = [p.strip().rstrip(".") for p in parts if p and p.strip()]
    return ". ".join(cleaned) or urlsplit(page.url).netloc
