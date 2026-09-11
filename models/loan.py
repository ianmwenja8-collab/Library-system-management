"""A borrowing transaction between a member and the library."""

from datetime import date, datetime, timedelta

class Loan:
    LOAN_PERIOD_DAYS = 14

    def __init__(self, member_id, book_id, copy_id, loan_id=None,
                 borrowed_at=None, due_date=None, returned_at=None,
                 fine_amount=0.0):
        self.id = loan_id
        self.member_id = member_id
        self.book_id = book_id
        self.copy_id = copy_id
        self.borrowed_at = borrowed_at if borrowed_at is not None else datetime.now()
        self.due_date = due_date if due_date is not None else (
            self.borrowed_at + timedelta(days=self.LOAN_PERIOD_DAYS)
        )
        self.returned_at = returned_at
        self.fine_amount = float(fine_amount)

    @property
    def loan_id(self):
        return self.id

    @loan_id.setter
    def loan_id(self, value):
        self.id = value

    @property
    def is_returned(self):
        return self.returned_at is not None

    def mark_returned(self, returned_at=None):
        self.returned_at = returned_at if returned_at is not None else datetime.now()

    def calculate_fine(self, rate=0.50, cap=None, today=None):
        check_date = today if today is not None else date.today()
        due = self.due_date
        if isinstance(due, str):
            due = date.fromisoformat(due)
        elif isinstance(due, datetime):
            due = due.date()
        days_late = (check_date - due).days
        amount = max(0, days_late) * rate
        if cap is not None:
            amount = min(amount, cap)
        self.fine_amount = round(amount, 2)
        return self.fine_amount

    @staticmethod
    def _save_date(value):
        return value.isoformat() if hasattr(value, "isoformat") else value

    @staticmethod
    def _load_date(value):
        if value is None or not isinstance(value, str):
            return value
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return value

    def to_dict(self):
        return {
            "id": self.id,
            "loan_id": self.id,
            "member_id": self.member_id,
            "book_id": self.book_id,
            "copy_id": self.copy_id,
            "borrowed_at": self._save_date(self.borrowed_at),
            "due_date": self._save_date(self.due_date),
            "returned_at": self._save_date(self.returned_at),
            "fine_amount": self.fine_amount,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            member_id=data["member_id"], book_id=data["book_id"],
            copy_id=data["copy_id"], loan_id=data.get("id", data.get("loan_id")),
            borrowed_at=cls._load_date(data.get("borrowed_at")),
            due_date=cls._load_date(data.get("due_date")),
            returned_at=cls._load_date(data.get("returned_at")),
            fine_amount=data.get("fine_amount", 0.0),
        )

    def __repr__(self):
        return f"Loan(id={self.id!r}, member_id={self.member_id!r}, book_id={self.book_id!r})"