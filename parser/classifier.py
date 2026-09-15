import re

# Достаточно корней слов — подстрочное совпадение само покрывает падежи и число
# ("репетитор" находит и "репетитора", и "репетиторов").
KEYWORDS = [
    "репетитор",
    "преподавател",
    "учител",
    "занят",
    "уроки по",
    "подтян",
    "экзамен",
    "егэ",
    "огэ",
    "домашк",
    "домашнее задание",
]

_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(k) for k in KEYWORDS) + r")",
    re.IGNORECASE,
)


def is_tutor_request(text: str | None) -> bool:
    if not text:
        return False
    return bool(_PATTERN.search(text))