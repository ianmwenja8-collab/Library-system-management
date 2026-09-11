"""People and user accounts for the library system."""

class Person:
    def __init__(self, name, email):
        self.name = self._text(name, "Name")
        self.email = self._email(email)

    @staticmethod
    def _text(value, label):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} cannot be empty.")
        return value.strip()

    @staticmethod
    def _email(value):
        if not isinstance(value, str):
            raise ValueError("Email must be a string.")
        value = value.strip().lower()
        if not value or "@" not in value:
            raise ValueError("Please provide a valid email address.")
        return value

    def to_dict(self):
        return {"name": self.name, "email": self.email}

    def __str__(self):
        return f"{self.name} ({self.email})"


class User(Person):
    VALID_ROLES = {"member", "librarian"}

    def __init__(self, name, email, username, password_hash,
                 role="member", user_id=None):
        super().__init__(name, email)
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username cannot be empty.")
        if role not in self.VALID_ROLES:
            raise ValueError("Role must be member or librarian.")
        self.id = user_id
        self.username = username.strip()
        self.password_hash = password_hash
        self.role = role

    @property
    def user_id(self):
        return self.id

    @user_id.setter
    def user_id(self, value):
        self.id = value

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "id": self.id,
            "user_id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role,
        })
        return data

    def __repr__(self):
        return f"User(id={self.id!r}, username={self.username!r}, role={self.role!r})"


class Member(User):
    def __init__(self, *args, **kwargs):
        kwargs["role"] = "member"
        super().__init__(*args, **kwargs)


class Librarian(User):
    def __init__(self, *args, **kwargs):
        kwargs["role"] = "librarian"
        super().__init__(*args, **kwargs)
