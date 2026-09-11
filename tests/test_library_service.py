import os
import tempfile
from datetime import date, timedelta

from auth.auth_manager import AuthManager
from services.library_service import LibraryService


def make_service():
    paths = []
    for _ in range(4):
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        tmp.close()
        os.remove(tmp.name)
        paths.append(tmp.name)
    users_path, books_path, copies_path, loans_path = paths
    waitlists_path = books_path + ".waitlists"
    auth = AuthManager(filepath=users_path)
    service = LibraryService(
        auth, books_path=books_path, copies_path=copies_path,
        loans_path=loans_path, waitlists_path=waitlists_path,
    )
    return auth, service


def setup_librarian_and_member(auth):
    auth.register("Lib", "lib@example.com", "lib", "pw", role="librarian")
    auth.register("Mem", "mem@example.com", "mem", "pw", role="member")


# ---------- catalog / RBAC ----------

def test_member_cannot_add_book():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("mem", "pw")
    result = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 2)
    assert result is None
    assert service.list_books() == []


def test_librarian_can_add_book_creates_copies():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 3)
    assert book.title == "Dune"
    assert service.available_count(book.id) == 3


def test_search_filters_by_title_author_category():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("lib", "pw")
    service.add_book("Dune", "Frank Herbert", "111", "Sci-Fi", 1)
    service.add_book("1984", "George Orwell", "222", "Dystopian", 1)

    assert len(service.search_books(title="dune")) == 1
    assert len(service.search_books(author="orwell")) == 1
    assert len(service.search_books(category="sci-fi")) == 1
    assert len(service.search_books(title="nonexistent")) == 0


def test_remove_book_blocked_while_copy_borrowed():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 1)
    auth.login("mem", "pw")
    service.checkout_book(book.id)
    auth.login("lib", "pw")
    try:
        service.remove_book(book.id)
        assert False, "expected ValueError"
    except ValueError:
        pass


# ---------- borrowing ----------

def test_checkout_requires_login():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 1)
    auth.logout()
    result = service.checkout_book(book.id)
    assert result is None


def test_checkout_with_no_copies_raises():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 1)
    auth.login("mem", "pw")
    service.checkout_book(book.id)
    try:
        service.checkout_book(book.id)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_checkout_and_return_flow_no_fine_when_on_time():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 1)
    auth.login("mem", "pw")
    loan = service.checkout_book(book.id)
    assert service.available_count(book.id) == 0

    returned = service.return_book(loan.id)
    assert returned.fine_amount == 0.0
    assert service.available_count(book.id) == 1


# ---------- fines ----------

def test_fine_calculated_when_overdue_and_capped():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 1)
    auth.login("mem", "pw")
    loan = service.checkout_book(book.id)

    # Force the loan far enough overdue that the fine hits the member cap ($10 @ $0.50/day).
    loan.due_date = (date.today() - timedelta(days=40)).isoformat()
    returned = service.return_book(loan.id)
    assert returned.fine_amount == service.FINE_CAP["member"]


def test_member_sees_own_fines_only():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.register("Mem2", "mem2@example.com", "mem2", "pw", role="member")

    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 2)

    auth.login("mem", "pw")
    loan1 = service.checkout_book(book.id)
    loan1.due_date = (date.today() - timedelta(days=5)).isoformat()
    service.return_book(loan1.id)

    auth.login("mem2", "pw")
    loan2 = service.checkout_book(book.id)
    loan2.due_date = (date.today() - timedelta(days=3)).isoformat()
    service.return_book(loan2.id)

    auth.login("mem", "pw")
    my_fines = service.my_fines()
    assert len(my_fines) == 1
    assert my_fines[0].member_id == auth.current_user.id


def test_librarian_can_waive_fine():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 1)
    auth.login("mem", "pw")
    loan = service.checkout_book(book.id)
    loan.due_date = (date.today() - timedelta(days=5)).isoformat()
    returned = service.return_book(loan.id)
    assert returned.fine_amount > 0

    auth.login("lib", "pw")
    waived = service.waive_fine(loan.id)
    assert waived.fine_amount == 0.0


def test_member_cannot_waive_fine():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 1)
    auth.login("mem", "pw")
    loan = service.checkout_book(book.id)
    loan.due_date = (date.today() - timedelta(days=5)).isoformat()
    service.return_book(loan.id)
    result = service.waive_fine(loan.id)
    assert result is None


# ---------- waitlist ----------

def test_join_waitlist_blocked_when_copies_available():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 1)
    auth.login("mem", "pw")
    try:
        service.join_waitlist(book.id)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_waitlist_reserves_next_copy_on_return():
    auth, service = make_service()
    setup_librarian_and_member(auth)
    auth.register("Mem2", "mem2@example.com", "mem2", "pw", role="member")

    auth.login("lib", "pw")
    book = service.add_book("Dune", "Herbert", "111", "Sci-Fi", 1)

    auth.login("mem", "pw")
    loan = service.checkout_book(book.id)  # takes the only copy

    auth.login("mem2", "pw")
    service.join_waitlist(book.id)
    waiting_member_id = auth.current_user.id
    # mem2 can't check out yet — no copies free, so this raises (not a
    # permission failure, so it's not the login_required/role_required
    # "print and return None" path — it's a genuine business-rule error).
    try:
        service.checkout_book(book.id)
        assert False, "expected ValueError"
    except ValueError:
        pass

    auth.login("mem", "pw")
    service.return_book(loan.id)

    # The returned copy should now be reserved for mem2, not generally available.
    assert service.available_count(book.id) == 0

    auth.login("mem2", "pw")
    new_loan = service.checkout_book(book.id)
    assert new_loan is not None
    assert new_loan.member_id == waiting_member_id
