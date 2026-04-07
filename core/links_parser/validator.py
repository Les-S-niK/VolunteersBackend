import requests
import re
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional
import concurrent.futures
from datetime import datetime


class NarcoticsLinkAnalyzer:
    def __init__(self):
        self.dictionaries = {
            "suspicious_tlds": [
                ".onion",
                ".cc",
                ".shop",
                ".biz",
                ".xyz",
                ".top",
                ".club",
                ".site",
                ".online",
                ".store",
                ".fun",
                ".pro",
            ],
            "suspicious_domain_words": [
                "shop",
                "store",
                "market",
                "magazin",
                "маркет",
                "шоп",
                "drug",
                "pharm",
                "med",
                "pill",
                "tablet",
                "хим",
                "нарк",
                "dark",
                "deep",
                "hidden",
                "secret",
                "private",
                "заклад",
                "legal",
                "rc",
                "research",
                "chems",
                "botan",
                "smart",
            ],
            "suspicious_content_words": [
                "нарко",
                "drug",
                "марихуана",
                "гашиш",
                "кокаин",
                "героин",
                "амфетамин",
                "ЛСД",
                "экстази",
                "мефедрон",
                "MDMA",
                "псилоцибин",
                "закладк",
                "приход",
                "легал",
                "микродоз",
                "шишки",
                "бошки",
                "кристал",
                "порошок",
                "соль",
                "спайс",
                "микс",
                "реагент",
                "химка",
                "скорость",
                "колеса",
                "таблы",
                "марки",
                "грамм",
                "заказать",
                "доставка",
                "оплата",
                "биткоин",
                "крипто",
                "btc",
                "отзывы",
                "гарант",
                "аноним",
                "шифр",
                "PGP",
                "телеграм",
                "telegram",
                "тг",
                "@",
                "бот",
                "курьер",
                "кладмен",
            ],
            "legit_domain_words": [
                "apteka",
                "аптека",
                "gorapteka",
                "eapteka",
                "zdravcity",
                "wildberries",
                "ozon",
                "aliexpress",
                "yandex",
                "google",
                "vk.com",
                "facebook",
                "instagram",
                "youtube",
                "twitter",
                "gov.",
                "police",
                "мвд",
                "фсб",
                "роскомнадзор",
                "minzdrav",
            ],
            "shop_indicators": [
                "магазин",
                "shop",
                "store",
                "каталог",
                "catalog",
                "корзина",
                "cart",
                "купить",
                "buy",
                "цена",
                "price",
                "товар",
                "product",
                "категории",
                "categories",
                "доставк",
                "delivery",
                "оплат",
                "payment",
                "заказ",
                "order",
            ],
        }

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

        # Кэш результатов
        self.cache = {}

    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Валидация URL"""
        url = url.strip()
        if not url:
            return False, "Пустой URL"

        # Проверка формата
        if not re.match(r"^https?://", url, re.IGNORECASE):
            url = "https://" + url

        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False, "Отсутствует доменное имя"
            if not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", parsed.netloc):
                return False, "Неверный формат домена"
            return True, url + "/"
        except:
            return False, "Некорректный URL"

    def extract_root_domain(self, url: str) -> str:
        """Извлечение корневого домена"""
        parsed = urlparse(url)
        domain = parsed.netloc

        # Удаляем www.
        if domain.startswith("www."):
            domain = domain[4:]

        return f"{parsed.scheme}://{domain}/"

    def check_http_status(self, url: str) -> Dict:
        """Проверка HTTP статуса"""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return {
                "status_code": response.status_code,
                "final_url": response.url,
                "headers": dict(response.headers),
                "accessible": response.status_code < 400,
            }
        except requests.exceptions.Timeout:
            return {"status_code": 0, "error": "timeout", "accessible": False}
        except requests.exceptions.ConnectionError:
            return {"status_code": 0, "error": "connection_error", "accessible": False}
        except Exception as e:
            return {"status_code": 0, "error": str(e), "accessible": False}

    def analyze_tld(self, url: str) -> Dict:
        """Анализ доменной зоны"""
        parsed = urlparse(url)
        domain = parsed.netloc

        score = 0
        flags = []

        # Проверка подозрительных TLD
        for tld in self.dictionaries["suspicious_tlds"]:
            if domain.endswith(tld):
                score += 1
                flags.append(f"suspicious_tld:{tld}")
                break

        # Проверка на .ru/.com (меньше подозрений)
        if domain.endswith(".ru") or domain.endswith(".com"):
            score -= 1
            flags.append("common_tld")

        return {"score": score, "flags": flags}

    def analyze_domain_name(self, url: str) -> Dict:
        """Анализ имени домена"""
        parsed = urlparse(url)
        domain = parsed.netloc

        score = 0
        flags = []

        # Проверяем подозрительные слова в домене
        for word in self.dictionaries["suspicious_domain_words"]:
            if word.lower() in domain.lower():
                score += 1
                flags.append(f"suspicious_word_in_domain:{word}")

        # Проверяем легальные слова
        for word in self.dictionaries["legit_domain_words"]:
            if word.lower() in domain.lower():
                score -= 2
                flags.append(f"legit_word_in_domain:{word}")

        return {"score": score, "flags": flags}

    def fetch_content(self, url: str) -> Optional[str]:
        """Получение контента страницы"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text.lower()
        except:
            return None

    def analyze_content(self, url: str) -> Dict:
        """Анализ контента страницы"""
        content = self.fetch_content(url)

        if not content:
            return {
                "score": 0,
                "flags": ["content_unavailable"],
                "keywords_found": [],
                "keywords_count": 0,
            }

        score = 0
        flags = []
        found_keywords = []

        # Проверка ключевых слов
        for keyword in self.dictionaries["suspicious_content_words"]:
            if keyword.lower() in content:
                score += 1
                found_keywords.append(keyword)
                flags.append(f"keyword:{keyword}")

        # Дополнительные проверки
        payment_indicators = ["bitcoin", "крипто", "crypto"]
        if any(word in content for word in payment_indicators):
            score += 1
            flags.append("crypto_payment")

        delivery_indicators = ["доставк", "delivery", "курьер"]
        if any(word in content for word in delivery_indicators):
            score += 1
            flags.append("delivery_mentioned")

        anonymity_indicators = ["аноним", "anonymous", "шифр", "pgp"]
        if any(word in content for word in anonymity_indicators):
            score += 1
            flags.append("anonymity")

        # Проверка признаков магазина
        shop_score = 0
        for indicator in self.dictionaries["shop_indicators"]:
            if indicator in content:
                shop_score += 1

        if shop_score >= 3:  # Если найдено достаточно признаков магазина
            score += 1
            flags.append("shop_detected")

        return {
            "score": score,
            "flags": flags,
            "keywords_found": found_keywords[:10],  # Ограничиваем список
            "keywords_count": len(found_keywords),
            "content_available": True,
        }

    def analyze_url(self, url: str) -> Dict:
        """Полный анализ одной ссылки"""
        # Проверяем кэш
        if url in self.cache:
            return self.cache[url]

        print(f"🔍 Анализируем: {url[:50]}...")

        try:
            # Валидируем URL
            is_valid, normalized_url = self.validate_url(url)
            if not is_valid:
                result = {
                    "url": url,
                    "total_score": 10,
                    "danger_level": "НЕВАЛИДНЫЙ",
                    "category": "invalid",
                    "error": normalized_url,  # Здесь хранится сообщение об ошибке
                    "accessible": False,
                    "keywords_count": 0,
                }
                self.cache[url] = result
                return result

            # Собираем анализы
            analysis_results = {
                "http_status": self.check_http_status(normalized_url),
                "tld_analysis": self.analyze_tld(normalized_url),
                "domain_analysis": self.analyze_domain_name(normalized_url),
            }

            # Анализ контента (только если доступен)
            if analysis_results["http_status"]["accessible"]:
                analysis_results["content_analysis"] = self.analyze_content(
                    normalized_url
                )
            else:
                analysis_results["content_analysis"] = {
                    "score": 0,
                    "flags": ["content_unavailable"],
                    "keywords_found": [],
                    "keywords_count": 0,
                    "content_available": False,
                }

            # Рассчитываем итоговый результат
            result = self.calculate_total_score(url, analysis_results)

            # Сохраняем в кэш
            self.cache[url] = result

            return result

        except Exception as e:
            print(f"❌ Неожиданная ошибка при анализе {url}: {e}")
            result = {
                "url": url,
                "total_score": 10,
                "danger_level": "ERROR",
                "category": "error",
                "error": str(e),
                "accessible": False,
                "keywords_count": 0,
            }
            self.cache[url] = result
            return result

    def calculate_total_score(self, url: str, analysis_results: Dict) -> Dict:
        """Расчет общего рейтинга подозрительности (0-10, 0 - безопасно, 10 - опасно)"""
        total_score = 0.0  # используем float для промежуточных вычислений
        all_flags = []

        # 1. HTTP статус (вклад от -1 до +1)
        http_info = analysis_results["http_status"]
        if http_info["accessible"]:
            if http_info["status_code"] == 200:
                total_score += 1.0
                all_flags.append("accessible_200")
            else:
                total_score += 0.5  # доступен, но не 200 (например, редирект)
        else:
            total_score -= 1.0  # было -3, теперь -1
            all_flags.append("inaccessible")

        # 2. Анализ TLD (от -1 до +1)
        tld_analysis = analysis_results["tld_analysis"]
        total_score += tld_analysis["score"]
        all_flags.extend(tld_analysis["flags"])

        # 3. Анализ имени домена (ограничиваем вклад 2 баллами)
        domain_score = analysis_results["domain_analysis"]["score"]
        domain_score = max(
            -2, min(2, domain_score)
        )  # не даём уйти в сильный минус или плюс
        total_score += domain_score
        all_flags.extend(analysis_results["domain_analysis"]["flags"])

        # 4. Анализ контента (с ограничениями)
        content = analysis_results["content_analysis"]
        content_score = 0.0

        # ключевые слова: учитываем только первые 5, каждое даёт +1
        kw_count = min(content.get("keywords_count", 0), 5)
        content_score += kw_count

        # дополнительные индикаторы (каждый даёт 0.5 балла)
        extra_flags = []
        if "crypto_payment" in content["flags"]:
            content_score += 0.5
            extra_flags.append("crypto_payment")
        if "delivery_mentioned" in content["flags"]:
            content_score += 0.5
            extra_flags.append("delivery_mentioned")
        if "anonymity" in content["flags"]:
            content_score += 0.5
            extra_flags.append("anonymity")
        if "shop_detected" in content["flags"]:
            content_score += 0.5
            extra_flags.append("shop_detected")

        # Ограничиваем максимальный вклад контента 5 баллами
        content_score = min(content_score, 5.0)
        total_score += content_score
        all_flags.extend(content["flags"])
        all_flags.extend(extra_flags)

        # Преобразуем в целое (отбрасываем дробную часть) и ограничиваем 0..10
        total_score = int(total_score)
        total_score = max(0, min(10, total_score))

        # Определяем уровень опасности (пороги можно оставить прежними)
        if total_score >= 8:
            danger_level = "ВЫСОКИЙ РИСК"
            category = "narcoshop"
        elif total_score >= 6:
            danger_level = "СРЕДНИЙ РИСК"
            category = "suspicious"
        elif total_score >= 4:
            danger_level = "НИЗКИЙ РИСК"
            category = "clean"
        else:
            danger_level = "БЕЗОПАСНЫЙ"
            category = "safe"

        return {
            "url": url,
            "normalized_url": http_info.get("final_url", url),
            "total_score": total_score,
            "danger_level": danger_level,
            "category": category,
            "all_flags": list(set(all_flags)),
            "detailed_scores": {
                "tld": tld_analysis["score"],
                "domain": analysis_results["domain_analysis"]["score"],
                "content": content_score,  # сохранённое ограниченное значение
            },
            "keywords_found": content.get("keywords_found", []),
            "keywords_count": content.get("keywords_count", 0),
            "accessible": http_info["accessible"],
            "status_code": http_info.get("status_code", 0),
            "timestamp": datetime.now().isoformat(),
        }

    def analyze_urls_batch(self, urls: List[str], max_workers: int = 5) -> List[Dict]:
        """Пакетный анализ ссылок"""
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.analyze_url, url): url for url in urls
            }

            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)

                    # Вывод прогресса
                    risk_color = {
                        "ВЫСОКИЙ РИСК": "🔴",
                        "СРЕДНИЙ РИСК": "🟡",
                        "НИЗКИЙ РИСК": "🟢",
                        "БЕЗОПАСНЫЙ": "⚪",
                        "НЕВАЛИДНЫЙ": "⚫",
                    }.get(result["danger_level"], "⚪")

                    print(
                        f"{risk_color} {url[:40]:40} | Оценка: {result['total_score']:3} | {result['danger_level']}"
                    )

                except Exception as e:
                    print(f"❌ Ошибка при анализе {url}: {e}")
                    results.append(
                        {
                            "url": url,
                            "total_score": 10,
                            "danger_level": "ERROR",
                            "category": "error",
                            "error": str(e),
                            "accessible": False,
                            "keywords_count": 0,
                        }
                    )

        # Сортировка по уровню подозрительности
        results.sort(
            key=lambda x: (x.get("total_score", 10), x.get("keywords_count", 0)),
            reverse=True,
        )

        return results

    def save_results(self, results: List[Dict], filename: str = "analysis_report.txt"):
        """Сохранение результатов в файл"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("ОТЧЕТ АНАЛИЗА ССЫЛОК\n")
            f.write(f"Время анализа: {timestamp}\n")
            f.write(f"Проанализировано: {len(results)}\n")
            f.write("=" * 80 + "\n\n")

            # Группируем по категориям
            categories = {}
            for result in results:
                cat = result.get("category", "unknown")
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(result)

            # Вывод по категориям в порядке убывания риска
            for category_name in [
                "narcoshop",
                "suspicious",
                "clean",
                "safe",
                "invalid",
                "error",
            ]:
                if category_name in categories:
                    cat_results = categories[category_name]

                    f.write(f"\n{'=' * 40}\n")
                    f.write(
                        f"КАТЕГОРИЯ: {category_name.upper()} ({len(cat_results)} шт.)\n"
                    )
                    f.write(f"{'=' * 40}\n\n")

                    for i, result in enumerate(cat_results, 1):
                        f.write(
                            f"{i:3}. Оценка: {result['total_score']:3} | {result['danger_level']}\n"
                        )
                        f.write(f"    URL: {result['url']}\n")

                        if result.get("keywords_found"):
                            keywords = result["keywords_found"][:5]
                            f.write(
                                f"    Найдено слов: {result.get('keywords_count', 0)} | Примеры: {', '.join(keywords)}\n"
                            )

                        if "error" in result:
                            f.write(f"    Ошибка: {result['error']}\n")

                        if result.get("accessible"):
                            f.write(
                                f"    Статус: {result.get('status_code', 'N/A')} | Доступен\n"
                            )
                        else:
                            f.write(
                                f"    Статус: {result.get('status_code', 'N/A')} | Недоступен\n"
                            )

                        f.write("\n")

            # Статистика
            f.write("\n" + "=" * 80 + "\n")
            f.write("СТАТИСТИКА:\n")
            f.write("=" * 80 + "\n")

            for cat in ["narcoshop", "suspicious", "clean", "safe", "invalid", "error"]:
                count = len(categories.get(cat, []))
                if count > 0:
                    percentage = (count / len(results)) * 100
                    f.write(f"{cat:12}: {count:4} ({percentage:.1f}%)\n")

        print(f"\n✅ Отчет сохранен: {filename}")
