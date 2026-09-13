def require_non_empty(value, field_name):
    if not value or not str(value).strip():
        raise ValueError(f"{field_name} cannot be empty.")
    return value.strip()


def require_positive_int(value, field_name):
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a whole number.")
    if n <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return n
