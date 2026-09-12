def require_non_empty(value, field_name):
    """Make sure text was entered."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")

    return value.strip()


def require_positive_int(value, field_name):
    """Make sure the value is a positive whole number."""
    try:
        number = int(value)
    except ValueError as error:
        raise ValueError(
            f"{field_name} must be a whole number."
        ) from error

    if number <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return number
