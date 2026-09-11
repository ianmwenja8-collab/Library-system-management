import logging

import pytest

from auth.auth_manager import AuthManager
from auth.decorators import login_required, log_action, role_required


class DemoActions:
    @login_required
    def logged_in_action(self, auth=None):
        return "done"

    @role_required("librarian")
    def librarian_action(self, auth=None):
        return "librarian done"

    @log_action
    def recorded_action(self, auth=None):
        return "recorded"


def make_auth(tmp_path):
    return AuthManager(filepath=str(tmp_path / "users.json"))


def test_login_required_rejects_logged_out_user(tmp_path):
    auth = make_auth(tmp_path)
    with pytest.raises(PermissionError):
        DemoActions().logged_in_action(auth=auth)


def test_login_required_allows_logged_in_user(tmp_path):
    auth = make_auth(tmp_path)
    auth.register("Vic", "vic@example.com", "vic", "pw")
    auth.login("vic", "pw")
    assert DemoActions().logged_in_action(auth=auth) == "done"


def test_role_required_rejects_wrong_role(tmp_path):
    auth = make_auth(tmp_path)
    auth.register("Member", "member@example.com", "member", "pw", role="member")
    auth.login("member", "pw")
    with pytest.raises(PermissionError):
        DemoActions().librarian_action(auth=auth)


def test_role_required_allows_correct_role(tmp_path):
    auth = make_auth(tmp_path)
    auth.register("Lib", "lib@example.com", "lib", "pw", role="librarian")
    auth.login("lib", "pw")
    assert DemoActions().librarian_action(auth=auth) == "librarian done"


def test_log_action_calls_function_and_logs_user(tmp_path, caplog):
    auth = make_auth(tmp_path)
    auth.register("Vic", "vic@example.com", "vic", "pw")
    auth.login("vic", "pw")
    with caplog.at_level(logging.INFO, logger="library-cli"):
        result = DemoActions().recorded_action(auth=auth)
    assert result == "recorded"
    assert "vic" in caplog.text
    assert "recorded_action" in caplog.text
