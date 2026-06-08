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


def is_tutor_request(text: str) -> bool:
    for keyword in KEYWORDS:
        if keyword in text.lower():
            return True
    return False
