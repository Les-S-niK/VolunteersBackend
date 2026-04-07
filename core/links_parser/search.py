from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import Iterable

from ddgs import DDGS


def _search_single_query(
    query: str,
    limit: int = 10,
    region: str = "ru-RU",
    backend: str = "auto",
    delay: float = 5.0,
    timeout: int = 20,
) -> tuple[str, list[str]]:
    """
    Run a DuckDuckGo search for a single query.

    Args:
        query: Search term.
        limit: Maximum number of result URLs.
        region: DuckDuckGo region code.
        backend: DDGS backend selection.
        delay: Delay between page requests (seconds).
        timeout: DDGS timeout in seconds.

    Returns:
        Tuple of (query, list of URLs).
    """
    found: list[str] = []
    seen: set[str] = set()
    page = 1

    while len(found) < limit:
        with DDGS(timeout=timeout) as ddgs:
            try:
                page_results = list(
                    ddgs.text(
                        query,
                        max_results=limit,
                        page=page,
                        region=region,
                        backend=backend,
                    )
                )
            except Exception as e:
                print(f"[ERROR] Query '{query}' failed: {e}")
                break
            if not page_results:
                break

            for r in page_results:
                href = r.get("href")
                if href and href not in seen:
                    seen.add(href)
                    found.append(href)

            page += 1

            if len(found) < limit:
                sleep(delay)

    if len(found) > limit:
        found = found[:limit]

    return query, found


def search_queries(
    queries: Iterable[str],
    limit: int = 10,
    region: str = "ru-RU",
    backend: str = "auto",
    delay: float = 5.0,
    timeout: int = 20,
    max_workers: int = 5,
) -> dict[str, list[str]]:
    """
    Run DuckDuckGo search for multiple queries using multithreading.

    Args:
        queries: Iterable of search terms.
        limit: Maximum number of result URLs per query.
        region: DuckDuckGo region code.
        backend: DDGS backend selection.
        delay: Delay between page requests (seconds).
        timeout: DDGS timeout in seconds.
        max_workers: Maximum number of threads to use (default: 5).

    Returns:
        Dictionary where key = query, value = list of URLs.
    """
    results: dict[str, list[str]] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _search_single_query,
                query,
                limit=limit,
                region=region,
                backend=backend,
                delay=delay,
                timeout=timeout,
            ): query
            for query in queries
        }

        for future in futures:
            try:
                query, found = future.result()
                results[query] = found
            except Exception as e:
                query = futures[future]
                print(f"[ERROR] Processing query '{query}' failed: {e}")
                results[query] = []

    return results

