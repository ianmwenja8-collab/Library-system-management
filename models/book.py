"""Book information used by the library catalogue."""

class Book:
    """Store catalogue details for one book title."""

    def __init__(self, title, author, isbn, category, book_id=None):
        self.title = self._text(title, "Title")
        self.author = self._text(author, "Author")
        self.isbn = self._text(isbn, "ISBN")
        self.category = self._text(category, "Category")
        self.id = book_id
        self._copies = []

    @staticmethod
    def _text(value, label):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} cannot be empty.")
        return value.strip()

    @property
    def book_id(self):
        """Keep the older name available to callers that use it."""
        return self.id

    @book_id.setter
    def book_id(self, value):
        self.id = value

    @property
    def copies(self):
        return list(self._copies)

    def add_copy(self, copy):
        if copy not in self._copies:
            self._copies.append(copy)

    def remove_copy(self, copy_id):
        for copy in self._copies:
            if str(copy.id) == str(copy_id):
                self._copies.remove(copy)
                return True
        return False

    def available_count(self):
        return sum(1 for copy in self._copies if copy.status == "available")

    def total_copies(self):
        return len(self._copies)

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data):
        book_id = data.get("id", data.get("book_id"))
        return cls(data["title"], data["author"], data["isbn"],
                   data["category"], book_id=book_id)

    def __str__(self):
        return f"{self.title} by {self.author}"

    def __repr__(self):
        return f"Book(id={self.id!r}, title={self.title!r})"