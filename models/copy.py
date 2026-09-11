"""A physical copy of a book."""

class Copy:
    VALID_STATUSES = {"available", "borrowed", "reserved"}

    def __init__(self, book_id, status="available", reserved_for=None,
                 copy_id=None, condition="good"):
        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid copy status.")
        self.id = copy_id
        self.book_id = book_id
        self.status = status
        self.reserved_for = reserved_for
        self.condition = condition

    @property
    def copy_id(self):
        return self.id

    @copy_id.setter
    def copy_id(self, value):
        self.id = value

    def is_claimable_by(self, member_id):
        if self.status == "available":
            return True
        return self.status == "reserved" and self.reserved_for == member_id

    def borrow(self, member_id=None):
        if not self.is_claimable_by(member_id):
            return False
        self.status = "borrowed"
        self.reserved_for = None
        return True

    def return_copy(self, reserved_for=None):
        if self.status != "borrowed":
            return False
        if reserved_for is None:
            self.status = "available"
        else:
            self.status = "reserved"
            self.reserved_for = reserved_for
        return True

    def reserve(self, member_id):
        if self.status != "available":
            return False
        self.status = "reserved"
        self.reserved_for = member_id
        return True

    def to_dict(self):
        return {
            "id": self.id,
            "copy_id": self.id,
            "book_id": self.book_id,
            "status": self.status,
            "reserved_for": self.reserved_for,
            "condition": self.condition,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            book_id=data["book_id"],
            status=data.get("status", "available"),
            reserved_for=data.get("reserved_for"),
            copy_id=data.get("id", data.get("copy_id")),
            condition=data.get("condition", "good"),
        )

    def __repr__(self):
        return f"Copy(id={self.id!r}, book_id={self.book_id!r}, status={self.status!r})"
