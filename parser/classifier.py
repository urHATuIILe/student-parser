KEYWORDS = [
    "ищу репетитора",
    "нужен репетитор",
    "репетитор",
    "занятия",
    "дополнительные занятия",
    "подготовка к экзамену",
    "экзамен",
    "подготовка к егэ",
    "егэ",
    "подготовка к огэ",
    "огэ",
]


def is_tutor_request(text: str | None) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    for keyword in KEYWORDS:
        if keyword in text_lower:
            return True
    return False