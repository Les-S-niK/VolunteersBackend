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


def read_queries_line_by_line(filepath: str):
    """
    Генератор, построчно читающий файл и возвращающий непустые строки (запросы).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            query = line.strip()
            if query:
                yield query


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

    analyzer = NarcoticsLinkAnalyzer()
    total_queries = 0
    total_saved = 0
    total_errors = 0

    # Построчная обработка запросов
    for query in read_queries_line_by_line(filepath):
        total_queries += 1
        print(f"\n[INFO] Обработка запроса #{total_queries}: '{query}'")

        # Поиск ссылок для текущего запроса
        queries_links = search_queries([query], limit=limit, max_workers=1)
        links = queries_links.get(query, [])

        if not links:
            print(
                f"[WARN] Для запроса '{query}' не найдено ни одной ссылки. Пропускаем."
            )
            continue

        print(f"[INFO] Найдено ссылок: {len(links)}")

        # Анализ найденных ссылок
        results = analyzer.analyze_urls_batch(links)
        analyzer.save_results(results)
        print(
            f"[INFO] Анализ завершён для запроса '{query}'. Получено результатов: {len(results)}"
        )

        # Сохранение в БД подходящих ссылок
        for res in results:
            url_raw: str | None = res.get("normalized_url")
            priority: int | None = res.get("total_score")
            if not url_raw or priority is None or priority < 3:
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

    # Итоговая статистика
    print("\n[INFO] === ИТОГОВАЯ СТАТИСТИКА ===")
    print(f"Обработано запросов: {total_queries}")
    print(f"Успешно сохранено записей в БД: {total_saved}")
    print(f"Ошибок при сохранении: {total_errors}")
    print("[INFO] Программа завершена.")


if __name__ == "__main__":
    asyncio.run(main())
