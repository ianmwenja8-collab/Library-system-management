import os
import tempfile

from auth.auth_manager import AuthManager


def make_auth():
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp.close()
    os.remove(tmp.name)
    return AuthManager(filepath=tmp.name)


def test_register_and_login():
    auth = make_auth()
    auth.register("Vic", "vic@example.com", "vic", "hunter2", role="member")
    user = auth.login("vic", "hunter2")
    assert user.username == "vic"
    assert user.role == "member"


def test_login_wrong_password_raises():
    auth = make_auth()
    auth.register("Vic", "vic@example.com", "vic", "hunter2")
    try:
        auth.login("vic", "wrong")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_duplicate_username_raises():
    auth = make_auth()
    auth.register("Vic", "vic@example.com", "vic", "hunter2")
    try:
        auth.register("Vic2", "vic2@example.com", "vic", "other")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_password_is_hashed_not_stored_plain():
    auth = make_auth()
    user = auth.register("Vic", "vic@example.com", "vic", "hunter2")
    assert user.to_dict()["password_hash"] != "hunter2"
