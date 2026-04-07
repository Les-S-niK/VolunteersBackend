import sys
import asyncio
from os import path

from sqlalchemy.exc import SQLAlchemyError

from core.links_parser.search import search_queries
from core.links_parser.validator import NarcoticsLinkAnalyzer
from core.database.sqlalchemy.models import Link
from core.database.sqlalchemy.db import CRUD


async def main():
    """Основная функция"""
    filename: str = "links.txt"
    print(
        f'Для работы программы необходимо наличие файла "{filename}" в текущей директории. '
        "В нём все запросы перечислены через \\n ( Символ новой строки. ) "
        "Первым аргуметом программы указывается количество ссылок для парсинга. "
    )
    limit: int = int(sys.argv[1])
    print(f"Количество ссылок: {limit}")

    filepath: str = path.join(path.dirname(__file__), filename)
    if not path.exists(filepath):
        print(f"Файл {filename} не найден.")
        return None

    test_queries: list[str] = []
    with open(filepath, "r") as file:
        test_queries = file.readlines()

    if not test_queries:
        print(f"В файле {filename} не найдено ссылок.")
        return None

    queries_links: dict[str, list[str]] = search_queries(
        test_queries, limit=limit, max_workers=10
    )

    for links in queries_links.values():
        analyzer = NarcoticsLinkAnalyzer()
        urls: list[str] = [url for url in links if url.strip()]

        results = analyzer.analyze_urls_batch(urls)
        analyzer.save_results(results)

        for res in results:
            url: str | None = res.get("normalized_url")
            priority: int | None = res.get("total_score")
            if not url or priority is None:
                print(f"Url or Priority is None: Url: {url}, Priority: {priority}")
                continue

            link: Link = Link(
                link=url,
                is_prohibited=None,
                priority=priority,
                user_id=None,
            )
            try:
                await CRUD.add(link).execute()
            except SQLAlchemyError as e:
                print(e)


if __name__ == "__main__":
    asyncio.run(main())
