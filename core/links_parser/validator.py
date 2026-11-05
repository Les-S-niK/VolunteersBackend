import requests
import re
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional
import concurrent.futures
from datetime import datetime


class NarcoticsLinkAnalyzer:
    def __init__(self):
        self.dictionaries = {
            "extreme_words": [
    "Базхар",
    "джемаа ислам",
    "Фансар",
    "джихад",
    "мушрик",
    "набхан",
    "Тарифин",
    "джихал",
    "вадуд",
    "динамит",
    "насир",
    "довля",
    "салахед",
    "дунья",
    "такф",
    "дуния",
    "хамас",
    "докумар",
    "Коритре",
    "закладк",
    "аббак",
    "заложен",
    "Адена-Абъх",
    "заложил",
    "ΑΚΑΠ",
    "заложни",
    "аллах",
    "акбар",
    "аллоха",
    "запал",
    "альсансар",
    "заряд",
    "альтах",
    "имарат",
    "Ал Бад",
    "аль-давахири",
    "Аль-канд",
    "альтеой",
    "амал",
    "Инша",
    "иншаалах",
    "Имарат Кавказ",
    "Иншаалла",
    "напалм",
    "невеста Аллаха",
    "неофашисты",
    "неофит",
    "никаб",
    "носить хиджаб",
    "НОФЕ",
    "нурджул",
    "паластин",
    "панкие",
    "пластид",
    "поборник сун",
    "подорв",
    "подрыв",
    "порох",
    "принял ислам",
    "принял смерть",
    "пут аллаха",
    "Аль-Шишани",
    "нишааллах",
    "ислам движ",
    "амният",
    "аманат",
    "амонат",
    "аммонал",
    "аммонит",
    "амонит",
    "ислами",
    "пут ислама",
    "исламист",
    "пути ислама",
    "путь ислама",
    "исламская армия",
    "резать",
    "исламская партия",
    "резня",
    "исламская революция",
    "резню",
    "исламский союз",
    "зарезать",
    "атака",
    "исламский фронт",
    "вырезать",
    "ахи",
    "ухти",
    "истишхад",
    "головорез",
    "Ахметский",
    "иштихала",
    "головорезы",
    "Багдади",
    "иштихад",
    "рубить",
    "бадр",
    "ичкер",
    "отрубить",
    "байки",
    "каббал джам",
    "зарубить",
    "бангасамо",
    "кавказский фронт",
    "салаф",
    "блиндаж",
    "катиб",
    "боевик",
    "кафер",
    "СГПБ",
    "бомба",
    "кафир",
    "братья мусульмане",
    "кафир",
    "ваххаб",
    "вахаб",
    "кафер",
    "велоглу",
    "кашмир",
    "взора",
    "взрыв",
    "взрыватель",
    "взрывник",
    "кибертер",
    "коктейль Молотова",
    "кумпул",
    "лагербоев",
    "взрывчатка",
    "куфр Куштанашвил",
    "вооруженная группировка",
    "газават",
    "лахор",
    "гремуч",
    "грохнуть",
    "грузовик",
    "давить",
    "задавить",
    "сбить",
    "сбивать",
    "дауля",
    "детанатор",
    "лашкар",
    "деворадикалы",
    "уйти в лес",
    "лесная",
    "лесные",
    "маджахед",
    "мазар",
    "селитр",
    "сепах сах",
    "cepa",
    "силитр",
    "сирийск чеч",
    "сменил веру",
    "смертник",
    "смерь шахид",
    "стал ислам",
    "стал исламист",
    "стал масульман",
    "стингер",
    "сунки",
    "сурик",
    "схрон",
    "таблиг",
    "таблиг джамаат",
    "таухид",
    "Макдиси",
    "таймер",
    "Маргошвили",
    "такфир",
    "детонатор",
    "муджахед",
    "талиб",
    "детонатор",
    "мула",
    "Тамими",
    "джамарму",
    "мунафик",
    "танзим",
    "джимаат",
    "мунафик",
    "Теракт",
    "джаннат",
    "муртад",
    "терарист",
    "джем баам",
    "мухим комар",
    "терорист",
    "терракт",
    "террарист",
    "террор",
    "террорист",
    "TOC",
    "триперекись ацетона",
    "тротил",
    "узргм",
    "улей",
    "устроить",
    "Ферзандан",
    "Фетил",
    "Фирдаус",
    "фитил",
    "фугаз",
    "Аднан Исмаил",
    "Наджим Абдел",
    "Дула",
    "Ими",
    "Аднаи хадж Алиалавит",
    "Али Ахмад Эид",
    "Аль Хардак",
    "Аль Мурабитун",
    "Аль Фатих",
    "Аль Шаам",
    "Анас Хасан Хаттаб",
    "Антакь",
    "Армия Ислама",
    "Армия исламского халифата",
    "Армия переселенцев сторонников",
    "Абвер",
    "Адольф",
    "A308",
    "Азовсталь",
    "Айдар",
    "аммонал",
    "аммонит",
    "амонат",
    "монит",
    "Аптечка",
    "атака",
    "Бандера",
    "Бачка",
    "Батькивщина",
    "Берлихиген",
    "Билецкий",
    "фугас",
    "x361",
    "Ахмад Шаляби",
    "Ахрар Шам",
    "хакин",
    "Ахрар Сурия",
    "Халиф",
    "Ахфад Расул",
    "Хангошвил",
    "Карака",
    "харам",
    "хиджаб",
    "хизб",
    "хизбул",
    "часовой",
    "пояс",
    "чатр шиб",
    "шарна",
    "шахид",
    "шахидка",
    "шашка",
    "шейх ясин",
    "ширас",
    "ЭДА",
    "здника",
    "эдешка",
    "эльгама эмир",
    "эмират яхуд",
    "Священая война",
    "Шейх Али Абдел Сакл",
    "Абдел Фарис Тайара",
    "Абдельазиз Салам",
    "Абдель Маджид",
    "Аззам",
    "Абдуллуштун",
    "Аби Мааз",
    "Абу Абдельазиз",
    "Абу Муслим",
    "Абу Абдеррахман Биляуй",
    "Абу Абдул Хамауп Абу Анас",
    "Абу Анасаш Шами",
    "Абу Анас Сахаба",
    "Абу Бакр Хусейн Курейши Багдади",
    "Абу Джисем Сауди",
    "Абу Зубейр",
    "Абу Ислам Шишани",
    "Абу Мусаб",
    "Батальон Фарук",
    "Батырашвили Гархан Теймуразо",
    "Башар Зуби",
    "Бригада булгар",
    "Бригада единобожия",
    "Бригада мучеников Ярмука",
    "Бригада переселенцев",
    "Бригада повстанцев Хомса",
    "Бригада Нурейн",
    "Бригада Халида Валида",
    "Бригада Хамза",
    "Брятья мусульмане",
    "Булгарски",
    "Вазиристан",
    "Василь Шимали Вахда",
    "Внуки пророка Давлат",
    "Исламия",
    "Ирак Шам ДАИШ",
    "Дауд Руси",
    "Джабхат Нусра",
    "Джабхат исламия",
    "Джабхат",
    "Джебх",
    "джамаат Абу Банната",
    "джамаат Абу Тальхи",
    "джамаат",
    "Абу Ханифы джамаат",
    "Дауда джамаат Собира",
    "Джамала Маароф",
    "Джебель Завия Сурия",
    "Джейш Ислам",
    "Джейш Мухаджирин Ансар",
    "Джейш Халяфа Исламия",
    "Джейш Хур",
    "Доуля",
    "Захран Аллюш",
    "Зейн Абидин Сарур",
    "Абдулатиф",
    "Зияд Шахин",
    "Ибрагим Аввад",
    "Ибрагим Бадри",
    "блиндаж",
    "боевик",
    "Болелы",
    "бомба",
    "БТРО",
    "Валлония",
    "Вальгалла",
    "Вандервафе",
    "Ваффен",
    "Вессель",
    "взорв",
    "взрыв",
    "взрыватель",
    "взрывник",
    "взрывчатка",
    "Вольна",
    "Волынь",
    "вооруженная группировка",
    "вырезать",
    "Галиция",
    "Галичина",
    "Гебельс",
    "Геринг",
    "Гесс",
    "Гимлер",
    "Гитлер",
    "Гитлерюгенд",
    "Горынь",
    "гремуч",
    "грохнуть",
    "Дас райх",
    "детонатор",
    "Дивизия СС",
    "Дирлевангер",
    "Днепр-1",
    "Днепр-2",
    "ДНР",
    "Донбасс",
    "Абу Мухаал Джулан",
    "Жид",
    "Абу Омар Багдади",
    "игил",
    "Игиш",
    "Забивы",
    "Абу Омар Крымский",
    "Абу Сайах",
    "Исламский фронт",
    "задавить",
    "Исламский фронт освобождения",
    "закладк",
    "Абу Сайяф",
    "заложен",
    "Абу Самир",
    "заложил",
    "Абу Сулейман Насер Лидинулла",
    "Исламский Фронт Хомса",
    "заложник",
    "Исламское государство Ирака",
    "запал",
    "Абу УмарШишани",
    "Абу Усама Джулани",
    "Абу Хазим Хавальда",
    "Абу Халед Сури",
    "Абу Ханифа",
    "Абу Хусейн Сауди",
    "Абу Юсуф",
    "Абуль Муатасем",
    "Исламское движение свободныхъл гајей",
    "Шама ИФОС",
    "Ияд Назми Халиль",
    "1488",
    "Калына",
    "Кальтенбруннер",
    "Карпатская сечь",
    "Карстьегер",
    "Карстьегер",
    "зарезать",
    "заряд",
    "Исламское государство Ирака",
    "Збручь",
    "кибертер",
    "коктейль Молотова",
    "Кракен",
    "Кривбасс",
    "Лангемарк",
    "Ландсторм",
    "ЛНР",
    "Лютцов",
    "Люфтвафе",
    "Люфтваффе",
    "Майн Кампф",
    "Мертвая голова",
    "Москаль",
    "Мюллер",
    "Нацбат",
    "Наци",
    "Нацкорпус",
    "подорв",
    "подрыв",
    "порох",
    "Правые",
    "Правый",
    "Правый Сектор",
    "Рагнарек",
    "Рагнарёк",
    "Рагнарок",
    "резать",
    "резню",
    "резня",
    "Peйx",
    "Риббентроп",
    "POA",
    "Розенберг",
    "POHA",
    "Рух опору",
    "Санаторий Русь",
    "Селитра",
    "Скандербег",
    "СНАУ",
    "СС викинг",
    "Тероборона",
    "терракт",
    "террарист",
    "Территориальная оборона",
    "Терроборона",
    "террор",
    "террорист",
    "Торнадо",
    "Тотенкопф",
    "Тризуб",
    "триперекись ацетона",
    "тротил",
    "узргм",
    "Украина",
    "национальная Украинская ассамблея",
    "Украинская национальная самооборона",
    "УНА-УНСO",
    "УНСO",
    "фитил",
    "Флориан Гайер",
    "Фрайкор",
    "фугаз",
    "фугас",
    "Ханджар",
    "Харьків-1",
    "Хель",
    "Хорст Вессель",
    "Хортица",
    "Хохлы",
    "Хуньяди",
    "Хоэнцштауфен",
    "Забивы",
    "часовой",
    "Околофутбол",
    "Правые",
    "Чернигов-1",
    "Чернигов-2",
    "Шарлемань",
    "шашка",
    "Шейх Мансур",
    "Колумбайн",
    "Маньяки Культ Убийств",
    "Касем Абу Усман Ахмад Джадани",
    "Касем Саад Дин",
    "Катаиб Мухаджирин",
    "Катаиб Фарук",
    "Катаиб Бухари",
    "Лива Ислам",
    "Лива Фатх",
    "Лива Таухид",
    "Лива Асыфат Шамаль",
    "Лукман Хасан Хусейн",
    "Львы Шама",
    "Марван Хусейн Али",
    "Мейсар Али Муса Абдел Джабури",
    "Мейсар Али Муса Джабурц",
    "Моджахеды Кавказа Сирии",
    "Мохаммад Зобан Абу Хамид",
    "Мохаммед Али Махер Нуами",
    "Муджахидин Кауказ Шам",
    "Мустафа Абделла Салех",
    "Мухаммадом Аднан Араур",
    "Мухаммед Ахмад Духи",
    "Отряд мученников Сирии",
    "панкисский джамат",
    "Рабах Раджех",
    "Саид Кутб",
    "Салах Ктайш",
    "Сап ахутдин Имарат",
    "Салех Муса Шабайта",
    "Сапман Булrapeкий",
    "Свободная сирийская армия",
    "Северная Буря",
    "Сейфулла Шишани",
    "сектор КБК",
    "Сирийский исламский фронт",
    "Соколы Шама",
    "Союз повстанцев Хомса",
    "Сукур Шам",
    "Таухид Джихад",
    "Усама Шабаху",
    "Усама Окайди",
    "Усуд Шам",
    "Фадель Ахмад Абделла Хаяли",
    "Фатх Ислам",
    "Фронт Аль Гута",
    "Фронт Ахль Шам",
    "Фронт Шамаль",
    "Фронт развития реформы",
    "Харакат Ахрар Шам Исламия",
    "Шаам",
    "Хасан Аббуд",
    "Шам",
    "Шарх сунна",
    "Шейх Абу Талх Ансари",
    "Шейх СулеПман",
    "Эйд Шумари Сауди",
    "Эмир Муам инин",
    "Ясин Сури",
    "Болелы",
    "Кузьмичи"
],
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
                "islam",
                "jamaat",
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
                "оплата",
                "биткоин",
                "крипто",
                "btc",
                "отзывы",
                "гарант",
                "аноним",
                "кладмен",
                "веществ",
                "химия",
                "пыль",
                "спиды",
                "фен",
                "кокс",
                "кислота",
                "acid",
                "стимулятор",
                "dope",
                "трав",
                "weed",
                "herb",
                "анаш",
                "каннабис",
                "cannabis",
                "кетамин",
                "дезоморфин",
                "первитин",
                "габапентин",
                "прегабалин",
                "баклофен",
                "фенобарбитал",
                "метадон",
                "сульфокамфокаин",
                "кодеин",
                "фентанил",
                "промедол",
                "декстрометорфан",
                "тропикамид",
                "морфин",
                "мусцимол",
                "мускарин",
                "беоцистин",
                "фенилэтиламин",
                "прикоп",
            ],
            "legit_domain_words": [
                "sushi",
                "japan",
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
                "library",
                "pedia",
                "wiki",
                "bigenc.ru",
                "rusneb.ru",
                "rsl.ru",
                "dzen.ru",
                "government",
                "archive.org",
                "scholar",
                "indicator.ru",
                "science",
                "clinic",
                "rehab",
                "ne-zavisimost.ru",
                "piter-bez-narkotikov.ru",
                "stop-zavisimost.ru",
                "garmonia-clinica.ru",
                "vperemen.com",
                "centr-12shagov.ru",
                "rosa.clinic",
                "mcmk.ru",
                "ugodie.ru",
                "inpramed.ru",
                "rehabfamily.com",
                "medtehnika-1.ru",
                "arma-rehab.ru",
                "narcology.clinic",
                "ru.wikipedia.org",
                "premium-practice.ru",
                "vielclinic.ru",
                "spb-spas.ru",
                "kas.clinic",
                "rastashop.ru",
                "alcoclinic.ru",
                "labmed-market.ru",
                "ekb.narko-centra.ru",
                "msdmanuals.com",
                "radugakamnya.ru",
                "czm-fond.ru",
                "avito.ru",
                "npistanbul.com",
                "detmir.ru",
                "adm-kush.ru",
                "neva-clinic.ru",
                "cdz-alter.ru",
                "ecrystal.ru",
                "kamnevedy.ru",
                "stilnaya.com",
                "kopirka.ru",
                "gorod-kamyshlov.ru",
                "mineralmarket.ru",
                "syntheticdrugs.unodc.org",
                "marshak.ru",
                "greenbird.ru",
                "luciastonesspb.ru",
                "kpk-parfum.ru",
                "leonardo.ru",
                "adm-grsk.gosuslugi.ru",
                "interfax.ru",
                "lasertaglsd.su",
                "ttshop.ru",
                "quarz.store",
                "gp66dzm.ru",
                "respublica.ru",
                "lmbd.ru",
                "magniart.ru",
                "burdastyle.ru",
                "kinopoisk.ru",
                "iledebeaute.ru",
                "ekzotika.com",
                "inteltoys.ru",
                "transylvania.ru",
                "pet-yes.com",
                "kinpet.ru",
                "moskva.gde.ru",
                "tbank.ru",
                "vkupiprodai.ru",
                "vsezverushki.ru",
                "sochi.gde.ru",
                "zooya.ru",
                "tvspb.ru",
                "flaticon.com",
                "taksa.store",
                "chillingeffects.org",
                "gesundheit.bremen.de",
                "narko.ee",
                "maa-ukraine.com.ua",
                "lumendatabase.org",
                "svoboda.org",
                "livemaster.ru",
                "birdinflight.com",
                "petglobals.com",
                "krasniykarandash.ru",
                "gramota.ru",
                "farpost.ru",
                "wildberries.ru",
                "ozon.ru",
                "youtube.com",
                "na-russia.org",
                "tochno.st",
                "tgl.ru",
                "audiomed.ru",
                "vc.ru",
                "pink-house.ru",
                "filtorg.ru",
                "ijevsk.narko-centra.ru",
                "allureparfum.ru",
                "sovstamps.ru",
                "zetika.ru",
                "telegid.me",
                "hot-head.ru",
                "rbc.ru",
                "uraycgb.ru",
                "qyzyljartv.kz",
                "advokatoleshko.ru",
                "rusmarka.ru",
                "kommersant.ru",
                "nyjbrc.com",
                "gov.kz",
                "klimat26.ru",
                "obozrevatel.com",
                "tass.ru",
                "dw.com",
                "aliexpress.ru"
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

        # Проверка на .ru (меньше подозрений)
        if domain.endswith(".ru"):
            score -= 2
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

        # Extreme detection
        for keyword in self.dictionaries["extreme_words"]:
            if keyword.lower() in content:
                score += 2
                found_keywords.append(keyword)
                flags.append(f"keyword:{keyword}")

        # Дополнительные проверки
        payment_indicators = ["bitcoin", "крипто", "crypto"]
        if any(word in content for word in payment_indicators):
            score += 1
            flags.append("crypto_payment")

        delivery_indicators = ["доставк", "delivery", "курьер"]
        if any(word in content for word in delivery_indicators):
            score += 0
            flags.append("delivery_mentioned")

        anonymity_indicators = ["аноним", "anonymous", "шифр", "tor", "onion"]
        if any(word in content for word in anonymity_indicators):
            score += 1
            flags.append("anonymity")

        # Проверка признаков магазина
        shop_score = 0
        for indicator in self.dictionaries["shop_indicators"]:
            if indicator in content:
                shop_score += 1

        if shop_score >= 2:  # Если найдено достаточно признаков магазина
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

        # ключевые слова: учитываем только первые 10, каждое даёт +1
        kw_count = min(content.get("keywords_count", 0), 10)
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

        # Ограничиваем максимальный вклад контента 7 баллами
        content_score = min(content_score, 7.0)
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
