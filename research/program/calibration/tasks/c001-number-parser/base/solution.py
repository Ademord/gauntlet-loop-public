"""Parse extracted numeric values without propagating invalid values."""


def parse_number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(" ", "").replace("'", "")
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None
