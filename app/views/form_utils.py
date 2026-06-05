from datetime import datetime


def parse_value(value, field_type):
    value = value.strip()
    if value == "":
        return None
    if field_type == "int":
        return int(value)
    if field_type == "float":
        return float(value)
    if field_type == "date":
        return datetime.strptime(value, "%Y-%m-%d").date()
    return value
