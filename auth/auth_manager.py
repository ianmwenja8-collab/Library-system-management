"""Small JSON-backed authentication manager."""

import hashlib
import json
import os
import secrets

from models.user import User


class AuthManager:
    def __init__(self, filepath="users.json"):
        self.filepath = filepath
        self.users = self._load_users()
        self.current_user = None

    def _load_users(self):
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return []
        return [User(
            item["name"], item["email"], item["username"],
            item["password_hash"], item.get("role", "member"),
            item.get("id", item.get("user_id")),
        ) for item in data]

    def _save_users(self):
        folder = os.path.dirname(self.filepath)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump([user.to_dict() for user in self.users], file, indent=2)

    @staticmethod
    def _hash_password(password, salt=None):
        if not isinstance(password, str) or not password:
            raise ValueError("Password cannot be empty.")
        salt = salt if salt is not None else secrets.token_hex(16)
        result = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 100000
        ).hex()
        return f"{salt}${result}"

    @classmethod
    def _check_password(cls, password, stored):
        try:
            salt, saved_hash = stored.split("$", 1)
        except ValueError:
            return False
        return cls._hash_password(password, salt) == stored

    def register(self, name, email, username, password, role="member"):
        if any(user.username == username for user in self.users):
            raise ValueError("Username is already registered.")
        next_id = max((user.id for user in self.users if user.id is not None), default=0) + 1
        user = User(name, email, username, self._hash_password(password), role, next_id)
        self.users.append(user)
        self._save_users()
        return user

    def login(self, username, password):
        for user in self.users:
            if user.username == username:
                if not self._check_password(password, user.password_hash):
                    raise ValueError("Incorrect username or password.")
                self.current_user = user
                return user
        raise ValueError("Incorrect username or password.")

    def logout(self):
        self.current_user = None

    def is_authenticated(self):
        return self.current_user is not None