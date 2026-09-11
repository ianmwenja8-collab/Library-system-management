import json
import os
from datetime import date, timedelta
from models.book import Book
from models.copy import Copy
from models.loan import Loan
from models.waitlist import Waitlist

class LibraryService:
    FINE_CAP = {"member": 10.0, "librarian": 0.0}

    def __init__(self, auth_manager, books_path="books.json", copies_path="copies.json", 
                 loans_path="loans.json", waitlists_path="waitlists.json"):
        self.auth_manager = auth_manager
        self.books_path = books_path
        self.copies_path = copies_path
        self.loans_path = loans_path
        self.waitlists_path = waitlists_path
        self.books = {}
        self.copies = {}
        self.loans = {}
        self.waitlists = {}
        self.load_data()

    def load_data(self):
        if os.path.exists(self.books_path):
            with open(self.books_path, "r") as f:
                self.books = {b["book_id"]: Book(**b) for b in json.load(f)}
        if os.path.exists(self.copies_path):
            with open(self.copies_path, "r") as f:
                self.copies = {c["copy_id"]: Copy(**c) for c in json.load(f)}
        if os.path.exists(self.loans_path):
            with open(self.loans_path, "r") as f:
                self.loans = {l["loan_id"]: Loan(**l) for l in json.load(f)}
        if os.path.exists(self.waitlists_path):
            with open(self.waitlists_path, "r") as f:
                self.waitlists = {w["book_id"]: Waitlist(book_id=w["book_id"], member_ids=w.get("member_ids")) for w in json.load(f)}

    def save_data(self):
        with open(self.books_path, "w") as f:
            json.dump([b.__dict__ for b in self.books.values()], f, indent=4)
        with open(self.copies_path, "w") as f:
            json.dump([c.__dict__ for c in self.copies.values()], f, indent=4)
        with open(self.loans_path, "w") as f:
            json.dump([l.__dict__ for l in self.loans.values()], f, indent=4)
        with open(self.waitlists_path, "w") as f:
            json.dump([{"book_id": w.book_id, "member_ids": w.member_ids} for w in self.waitlists.values()], f, indent=4)

    def add_book(self, title, author, isbn, category, copies_count):
        if not self.auth_manager.current_user or self.auth_manager.current_user.role != "librarian":
            return None
        book_id = str(len(self.books) + 1)
        new_book = Book(book_id=book_id, title=title, author=author, isbn=isbn, category=category)
        self.books[book_id] = new_book
        for i in range(copies_count):
            copy_id = f"{book_id}-C{i+1}"
            self.copies[copy_id] = Copy(copy_id=copy_id, book_id=book_id, condition="Good", status="available")
        self.save_data()
        return new_book

    def remove_book(self, book_id):
        if not self.auth_manager.current_user or self.auth_manager.current_user.role != "librarian":
            raise ValueError("Unauthorized")
        if book_id not in self.books:
            raise ValueError("Book not found")
        for copy in self.copies.values():
            if copy.book_id == book_id and copy.status in ["borrowed", "reserved"]:
                raise ValueError("Cannot remove book with active copies")
        self.copies = {cid: c for cid, c in self.copies.items() if c.book_id != book_id}
        del self.books[book_id]
        self.save_data()

    def list_books(self):
        return list(self.books.values())

    def search_books(self, title=None, author=None, category=None):
        results = list(self.books.values())
        if title:
            results = [b for b in results if title.lower() in b.title.lower()]
        if author:
            results = [b for b in results if author.lower() in b.author.lower()]
        if category:
            results = [b for b in results if category.lower() in b.category.lower()]
        return results

    def available_count(self, book_id):
        return sum(1 for c in self.copies.values() if c.book_id == book_id and c.status == "available")

    def checkout_book(self, book_id):
        user = self.auth_manager.current_user
        if not user:
            return None
        if book_id not in self.books:
            raise ValueError("Book unknown")
        target_copy = next((c for c in self.copies.values() if c.book_id == book_id and c.status == "reserved"), None)
        if not target_copy:
            target_copy = next((c for c in self.copies.values() if c.book_id == book_id and c.status == "available"), None)
        if not target_copy:
            raise ValueError("No copies available")
        target_copy.status = "borrowed"
        loan_id = str(len(self.loans) + 1)
        new_loan = Loan(
            loan_id=loan_id, 
            book_id=target_copy.book_id,
            copy_id=target_copy.copy_id, 
            member_id=user.id,
            borrowed_at=date.today().isoformat(), 
            due_date=(date.today() + timedelta(days=14)).isoformat(), 
            returned_at=None, 
            fine_amount=0.0
        )
        self.loans[loan_id] = new_loan
        self.save_data()
        return new_loan

    def return_book(self, loan_id):
        if loan_id not in self.loans:
            raise ValueError("Loan not found")
        loan = self.loans[loan_id]
        if loan.returned_at is not None:
            raise ValueError("Already returned")
        copy = self.copies.get(loan.copy_id)
        loan.returned_at = date.today().isoformat()
        due = date.fromisoformat(loan.due_date)
        ret = date.fromisoformat(loan.returned_at)
        if ret > due:
            days_late = (ret - due).days
            loan.fine_amount = min(days_late * 0.50, self.FINE_CAP.get("member", 10.0))
        waitlist = self.waitlists.get(copy.book_id)
        if waitlist and waitlist.member_ids:
            waitlist._member_ids.pop(0)
            copy.status = "reserved"
        else:
            copy.status = "available"
        self.save_data()
        return loan

    def join_waitlist(self, book_id):
        user = self.auth_manager.current_user
        if not user:
            return None
        if self.available_count(book_id) > 0:
            raise ValueError("Copies available, cannot join waitlist")
        if book_id not in self.waitlists:
            self.waitlists[book_id] = Waitlist(book_id=book_id)
        try:
            self.waitlists[book_id].add_member(user.id)
        except ValueError:
            pass
        self.save_data()

    def my_fines(self):
        user = self.auth_manager.current_user
        if not user:
            return []
        return [l for l in self.loans.values() if l.member_id == user.id and l.fine_amount > 0]

    def waive_fine(self, loan_id):
        user = self.auth_manager.current_user
        if not user or user.role != "librarian":
            return None
        if loan_id in self.loans:
            self.loans[loan_id].fine_amount = 0.0
            self.save_data()
            return self.loans[loan_id]
        return None