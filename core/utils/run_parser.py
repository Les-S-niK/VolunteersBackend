import sys
import asyncio
from os import path
from urllib.parse import urlparse, urlunparse

from sqlalchemy.exc import SQLAlchemyError

from core.links_parser.search import search_queries
from core.links_parser.validator import NarcoticsLinkAnalyzer
from core.database.sqlalchemy.models import Link
from core.database.sqlalchemy.db import CRUD


def normalize_url(url: str) -> str:
    """Удаляет явный стандартный порт (80, 443) и приводит URL к каноническому виду."""
    if not url:
        return ""
    parsed = urlparse(url)
    if (parsed.scheme == "http" and parsed.port == 80) or (
        parsed.scheme == "https" and parsed.port == 443
    ):
        parsed = parsed._replace(netloc=parsed.hostname)
    if not parsed.path:
        parsed = parsed._replace(path="/")
    return urlunparse(parsed)


async def main():
    filename: str = "links.txt"
    print("[INFO] Запуск программы.")
    print(
        f"[INFO] Необходим файл '{filename}' в текущей директории с запросами (по одному на строку)."
    )

    if len(sys.argv) < 2:
        print(
            "[ERROR] Не указано количество ссылок. Использование: python script.py <limit>"
        )
        return

    try:
        limit: int = int(sys.argv[1])
    except ValueError:
        print("[ERROR] Количество ссылок должно быть целым числом.")
        return

    print(f"[INFO] Лимит ссылок на один запрос: {limit}")

    filepath: str = path.join(path.dirname(__file__), filename)
    if not path.exists(filepath):
        print(f"[ERROR] Файл {filename} не найден по пути {filepath}.")
        return

    with open(filepath, "r") as file:
        test_queries = [line.strip() for line in file.readlines() if line.strip()]

    if not test_queries:
        print(f"[WARN] Файл {filename} не содержит ни одного непустого запроса.")
        return

    print(f"[INFO] Загружено {len(test_queries)} запросов из файла.")

    print("[INFO] Начинается поиск ссылок через DuckDuckGo...")
    queries_links: dict[str, list[str]] = search_queries(
        test_queries, limit=limit, max_workers=10
    )

    total_found = sum(len(links) for links in queries_links.values())
    print(f"[INFO] Поиск завершён. Всего найдено уникальных ссылок: {total_found}")

    analyzer = NarcoticsLinkAnalyzer()
    total_saved = 0
    total_errors = 0

    for query, links in queries_links.items():
        if not links:
            print(
                f"[WARN] Для запроса '{query}' не найдено ни одной ссылки. Пропускаем."
            )
            continue

        print(f"[INFO] Обработка запроса '{query}': получено {len(links)} ссылок.")

        urls: list[str] = [url for url in links if url.strip()]
        print(f"[INFO] Запуск анализа для {len(urls)} URL (validator)...")
        results = analyzer.analyze_urls_batch(urls)
        print(f"[INFO] Анализ завершён. Получено результатов: {len(results)}")

        analyzer.save_results(results)
        print("[INFO] Результаты анализа сохранены в файлы (если настроено).")

        for res in results:
            url_raw: str | None = res.get("normalized_url")
            priority: int | None = res.get("total_score")
            if not url_raw or priority is None:
                print(f"[WARN] Пропуск: normalized_url={url_raw}, priority={priority}")
                continue

            normalized_link = normalize_url(url_raw)
            link = Link(
                link=normalized_link,
                is_prohibited=None,
                priority=priority,
                user_id=None,
            )
            try:
                await CRUD.add(link).execute()
                total_saved += 1
                print(
                    f"[OK] Сохранена ссылка: {normalized_link} (приоритет {priority})"
                )
            except SQLAlchemyError as e:
                total_errors += 1
                print(f"[ERROR] Не удалось сохранить ссылку {normalized_link}: {e}")

    print("\n[INFO] === ИТОГОВАЯ СТАТИСТИКА ===")
    print(f"Обработано запросов: {len(queries_links)}")
    print(f"Успешно сохранено записей в БД: {total_saved}")
    print(f"Ошибок при сохранении: {total_errors}")
    print("[INFO] Программа завершена.")


if __name__ == "__main__":
    asyncio.run(main())
