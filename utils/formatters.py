def parse_amount(text):
    """Парсинг сумм (1000, 5k, 1кк)"""
    text = str(text).strip().lower().replace(" ", "").replace("k", "к")
    k_count = 0
    while text.endswith("к"):
        k_count += 1
        text = text[:-1]
    if not text:
        raise ValueError("Пустая строка")
    base = float(text)
    result = int(base * (1000 ** k_count))
    if result <= 0:
        raise ValueError("Сумма должна быть больше 0")
    return result


def fmt_amount(n):
    """Форматирование чисел (10 000, 1.5кк)"""
    try:
        formatted = f"{n:,}".replace(",", " ")
        if n >= 1_000_000_000_000:
            short = f"{round(n/1_000_000_000_000, 2)}кккк"
        elif n >= 1_000_000_000:
            short = f"{round(n/1_000_000_000, 2)}ккк"
        elif n >= 1_000_000:
            short = f"{round(n/1_000_000, 2)}кк"
        elif n >= 1_000:
            short = f"{round(n/1_000, 2)}к"
        else:
            return formatted
        return f"{formatted} [{short}]"
    except:
        return str(n)
