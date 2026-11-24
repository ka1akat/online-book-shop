"""Проверка текста обращения в поддержку ДО того, как оно сохранится в базу.

check_support_message(text) возвращает None, если текст нормальный, или короткое объяснение
для покупателя, если его нужно переписать. Обращение с ошибкой в базу не попадает.

Это базовый фильтр: он ловит самое очевидное (мат, оскорбления, ссылки, набор букв).
Список слов можно расширять: достаточно дописать основу слова в BAD_STEMS ниже.
"""

import re
from collections import Counter

# --- Что пишем покупателю ---
MIN_LENGTH = 10  # минимум символов после удаления пробелов по краям
MSG_EMPTY = "Please describe your problem: the message is empty."
MSG_SHORT = f"The message is too short. Please write at least {MIN_LENGTH} characters so we can understand the problem."
MSG_NONSENSE = "Please describe the problem in words, not only with digits or symbols."
MSG_LINKS = "Links are not allowed in a support request. Please remove the link and describe the problem in words."
MSG_RUDE = "Please remove rude words or insults. We will gladly help if you describe the problem politely."
MSG_SPAM = "The message looks like spam (repeated characters or words). Please write a normal description of the problem."

# --- Основы нехороших слов (русский, казахский, английский) ---
# Проверяется начало слова, перед ним допускается приставка (вы-, за-, на- ...).
# Короткие и спорные основы специально написаны с границей слова, чтобы не ловить обычные слова.
BAD_STEMS = [
    # русский
    r"ху[йеяию]\w*", r"хуе\w*", r"пизд\w*", r"еб[ауоилыё]\w*", r"ёб\w*", r"бл[яе]д\w*", r"блят\w*",
    r"муда[кч]\w*", r"гондон\w*", r"залуп\w*", r"пид[оа]р\w*", r"сук[аиуео]\b", r"сукин\w*",
    r"шлюх\w*", r"дроч\w*", r"манда\b", r"говн\w*", r"дерьм\w*", r"жоп[аыуе]\b",
    r"идиот\w*", r"дебил\w*", r"кретин\w*", r"урод\w*", r"мраз\w*", r"тварь\b", r"сволоч\w*",
    r"ублюд\w*", r"мудил\w*", r"гандон\w*", r"гавн\w*", r"долбо[её]б\w*", r"сучк[аеу]\b",
    # казахский
    r"қотақ\w*", r"котак\w*", r"сиктир\w*", r"сікті\w*", r"амсыз\w*", r"ақымақ\w*",
    # английский
    r"fuck\w*", r"shit\w*", r"bitch\w*", r"asshole\w*", r"cunt\w*", r"bastard\w*",
    r"motherfuck\w*", r"whore\w*", r"slut\w*", r"idiot\w*", r"moron\w*", r"dumbass\w*", r"retard\w*",
]
PREFIXES = r"(?:вы|за|на|по|до|об|от|при|раз|рас|с|у|под|съ|пере|недо|ни)?"
BAD_WORD = re.compile(r"(?<![а-яa-zқәіңғүұһө])" + PREFIXES + r"(?:" + "|".join(BAD_STEMS) + r")")

# Латинские и цифровые «двойники», которыми обходят фильтр: м@т, х у й, fuсk
LOOKALIKE_TO_CYRILLIC = str.maketrans(
    {"a": "а", "e": "е", "o": "о", "p": "р", "c": "с", "x": "х", "y": "у", "k": "к",
     "m": "м", "t": "т", "h": "н", "b": "в", "0": "о", "3": "з", "4": "ч", "6": "б", "@": "а"}
)
LOOKALIKE_TO_LATIN = str.maketrans(
    {"@": "a", "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "$": "s", "!": "i", "|": "i",
     "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "у": "y", "к": "k"}
)

LINK = re.compile(r"(https?://|www\.|t\.me/|wa\.me/|\b[\w-]+\.(?:com|ru|kz|net|org|info|xyz|me|io|ly)\b)", re.I)
LETTERS = re.compile(r"[a-zа-яёәіңғүұқөһ]", re.I)
SAME_CHAR_REPEATED = re.compile(r"(.)\1{5,}")  # одна и та же буква 6+ раз подряд: «аааааааа»


WORD = re.compile(r"[^\W\d_]+")  # слова из букв (любой язык)


def _repeats_one_word(text):
    """Одно и то же слово составляет больше половины текста: «buy buy buy buy buy now»."""
    words = WORD.findall(text.lower())
    if len(words) < 5:
        return False
    _, count = Counter(words).most_common(1)[0]
    return count >= 5 and count / len(words) >= 0.5


def _collapse(text):
    """Убирает растянутые буквы: «хууууй» -> «хуй» (три и более одинаковых подряд сводятся к одной)."""
    return re.sub(r"(.)\1{2,}", r"\1", text)


def _words_variants(text):
    """Несколько вариантов текста, в которых мат, спрятанный хитростями, становится видимым."""
    base = _collapse(text.lower().replace("ё", "е"))
    variants = {base, base.translate(LOOKALIKE_TO_CYRILLIC), base.translate(LOOKALIKE_TO_LATIN)}
    # «х у й» и «х.у.й»: одиночные буквы через пробел или точку склеиваем в одно слово
    glued = re.sub(r"\b(?:[а-яa-z][\s.\-_*]+){2,}[а-яa-z]\b", lambda m: re.sub(r"[\s.\-_*]", "", m.group(0)), base)
    variants.add(glued)
    variants.add(glued.translate(LOOKALIKE_TO_CYRILLIC))
    variants.add(glued.translate(LOOKALIKE_TO_LATIN))
    return variants


def check_support_message(text):
    """None, если текст нормальный, иначе короткое объяснение для покупателя."""
    text = (text or "").strip()

    if not text:
        return MSG_EMPTY
    if len(text) < MIN_LENGTH:
        return MSG_SHORT
    letters = len(LETTERS.findall(text))
    if letters < 3 or letters / len(text) < 0.5:
        return MSG_NONSENSE  # цифры, смайлики или знаки без слов
    if LINK.search(text):
        return MSG_LINKS
    for variant in _words_variants(text):
        if BAD_WORD.search(variant):
            return MSG_RUDE
    if SAME_CHAR_REPEATED.search(text) or _repeats_one_word(text):
        return MSG_SPAM
    return None
