"""FIFO queue for members waiting for a book."""

class Waitlist:
    def __init__(self, book_id, member_ids=None):
        self.book_id = book_id
        self._member_ids = []
        if member_ids is not None:
            for member_id in member_ids:
                self.add_member(member_id)

    @property
    def member_ids(self):
        return list(self._member_ids)

    def add_member(self, member_id):
        if member_id in self._member_ids:
            raise ValueError("Member is already on this waitlist.")
        self._member_ids.append(member_id)

    def next_member(self):
        if not self._member_ids:
            return None
        return self._member_ids[0]

    def pop_next(self):
        if not self._member_ids:
            return None
        return self._member_ids.pop(0)

    def remove_member(self, member_id):
        if member_id not in self._member_ids:
            return False
        self._member_ids.remove(member_id)
        return True

    def __len__(self):
        return len(self._member_ids)

    def to_dict(self):
        return {"book_id": self.book_id, "member_ids": self.member_ids}

    @classmethod
    def from_dict(cls, data):
        return cls(data["book_id"], data.get("member_ids", []))

    def __repr__(self):
        return f"Waitlist(book_id={self.book_id!r}, members={len(self)})"
