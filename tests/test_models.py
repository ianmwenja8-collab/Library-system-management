from models.book import Book
from models.copy import Copy
from models.loan import Loan
from models.person import Person
from models.waitlist import Waitlist


def test_person_rejects_empty_name():
    try:
        Person("", "a@b.com")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_person_rejects_bad_email():
    try:
        Person("Vic", "not-an-email")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_book_round_trip_dict():
    book = Book("Dune", "Frank Herbert", "111", category="Sci-Fi", book_id=42)
    restored = Book.from_dict(book.to_dict())
    assert restored.id == 42
    assert restored.title == "Dune"
    assert restored.category == "Sci-Fi"


def test_copy_claimable_by_available():
    copy = Copy(book_id=1, status="available")
    assert copy.is_claimable_by(member_id=7) is True


def test_copy_reserved_only_claimable_by_holder():
    copy = Copy(book_id=1, status="reserved", reserved_for=7)
    assert copy.is_claimable_by(member_id=7) is True
    assert copy.is_claimable_by(member_id=8) is False


def test_copy_borrowed_not_claimable():
    copy = Copy(book_id=1, status="borrowed")
    assert copy.is_claimable_by(member_id=7) is False


def test_copy_round_trip_dict():
    copy = Copy(book_id=5, status="reserved", reserved_for=3, copy_id=9)
    restored = Copy.from_dict(copy.to_dict())
    assert restored.book_id == 5
    assert restored.status == "reserved"
    assert restored.reserved_for == 3


def test_loan_round_trip_dict():
    loan = Loan(member_id=1, book_id=2, copy_id=10)
    restored = Loan.from_dict(loan.to_dict())
    assert restored.member_id == 1
    assert restored.book_id == 2
    assert restored.copy_id == 10
    assert restored.is_returned is False
    assert restored.fine_amount == 0.0


def test_waitlist_fifo_order():
    wl = Waitlist(book_id=1)
    wl.add_member(10)
    wl.add_member(20)
    assert wl.pop_next() == 10
    assert wl.pop_next() == 20
    assert wl.pop_next() is None


def test_waitlist_rejects_duplicate_member():
    wl = Waitlist(book_id=1)
    wl.add_member(10)
    try:
        wl.add_member(10)
        assert False, "expected ValueError"
    except ValueError:
        pass
