"""Decorators for login checks, roles, and action logging."""

import functools
import logging

logger = logging.getLogger("library-cli")


def login_required(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        auth = kwargs.get("auth")
        if auth is None:
            raise ValueError("An AuthManager must be passed as auth=.")
        if not auth.is_authenticated():
            raise PermissionError("You must be logged in.")
        return function(*args, **kwargs)
    return wrapper


def role_required(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            auth = kwargs.get("auth")
            if auth is None:
                raise ValueError("An AuthManager must be passed as auth=.")
            if not auth.is_authenticated():
                raise PermissionError("You must be logged in.")
            if auth.current_user.role not in allowed_roles:
                raise PermissionError("You do not have permission.")
            return function(*args, **kwargs)
        return wrapper
    return decorator


def log_action(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        auth = kwargs.get("auth")
        if auth is not None and auth.current_user is not None:
            logger.info("User %s performed %s", auth.current_user.username, function.__name__)
        else:
            logger.info("Unauthenticated action: %s", function.__name__)
        return function(*args, **kwargs)
    return wrapper
