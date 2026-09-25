"""
tools/web_search.py
────────────────────
DuckDuckGo search wrapper (matches duckduckgo-search in requirements.txt).
Fails soft so a rate-limit or network hiccup doesn't crash the whole graph.
"""


def web_search(query: str, max_results: int = 3):
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        return [
            {
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            }
            for r in results
        ]
    except Exception as e:
        return [{"title": "Web search unavailable", "snippet": str(e), "url": ""}]
