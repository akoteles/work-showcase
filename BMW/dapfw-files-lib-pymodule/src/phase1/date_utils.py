import re
from datetime import datetime


def try_parsing_date(text, date_format="%Y-%m-%d"):
    for fmt in (date_format, "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError("No valid date format found inside last_ingest_partition file")


def get_pattern_mask(mask):
    mask_elements = [
        mask[i + 1]
        for i in range(len(mask))
        if mask.startswith("%", i) and i < len(mask) - 1
    ]
    separator = [
        mask[i - 1]
        for i in range(1, len(mask))
        if mask.startswith("%", i) and i < len(mask) - 1
    ]
    separator = [
        "" if x in ("Y", "m", "d", "y", "H", "M", "S", "I", "f", "b", "B") else x
        for x in separator
    ]

    fmt = []
    nb_digits = []

    for i in mask_elements:
        if i == "Y":
            nb_digits.append("4")
            fmt.append("d")
        elif i in ("y", "H", "M", "S", "I"):
            nb_digits.append("2")
            fmt.append("d")
        elif i in ("m", "d"):
            nb_digits.append("1,2")
            fmt.append("d")
        elif i == "f":
            nb_digits.append("6")
            fmt.append("d")
        elif i in ("b", "B"):
            nb_digits.append("3,10")
            fmt.append("D")
        else:
            raise Exception("Mask not found")

    result = ""
    for i in range(len(nb_digits)):
        if i < len(separator):
            result = result + "\\" + fmt[i] + "{" + nb_digits[i] + "}" + separator[i]
        else:
            result = result + "\\" + fmt[i] + "{" + nb_digits[i] + "}"

    return result


def date_search(text, mask):
    str_pattern = get_pattern_mask(mask)
    date_pattern = re.search(str_pattern, text)
    if date_pattern is not None and date_pattern != "None":
        try:
            date_result = datetime.strptime(date_pattern.group(), mask)
            return date_result
        except Exception:
            return None
    else:
        return None
