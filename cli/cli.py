import argparse
import getpass

from tabulate import tabulate

from auth.auth_manager import AuthManager
from services.library_service import LibraryService
from utils.validators import require_non_empty, require_positive_int


class LibraryCLI:
    """Ties auth + service together into an interactive, menu-driven CLI."""

    def __init__(self):
        self.auth = AuthManager()
        self.service = LibraryService(self.auth)

    # ---------------- interactive menu ----------------

    def run_interactive(self):
        print("=== Library Management System ===")
        while True:
            if self.auth.current_user is None:
                self._guest_menu()
            else:
                self._logged_in_menu()

    def _guest_menu(self):
        print("\n1) Register  2) Login  3) List books  4) Search books  5) Quit")
        choice = input("> ").strip()
        if choice == "1":
            self._do_register()
        elif choice == "2":
            self._do_login()
        elif choice == "3":
            self._print_books(self.service.list_books())
        elif choice == "4":
            self._do_search()
        elif choice == "5":
            self._quit()
        else:
            print("Invalid choice.")

    def _logged_in_menu(self):
        user = self.auth.current_user
        print(f"\nLogged in as {user.username} ({user.role})")
        lines = [
            "1) List books", "2) Search books", "3) Checkout book", "4) Return book",
            "5) Join waitlist", "6) My loans", "7) My fines", "8) Logout", "9) Quit",
        ]
        actions = {
            "1": lambda: self._print_books(self.service.list_books()),
            "2": self._do_search,
            "3": self._do_checkout,
            "4": self._do_return,
            "5": self._do_join_waitlist,
            "6": self._print_my_loans,
            "7": lambda: self._print_fines(self.service.my_fines()),
            "8": self._do_logout,
            "9": self._quit,
        }
        if user.role == "librarian":
            lines += [
                "10) Add book", "11) Remove book", "12) Overdue loans",
                "13) All fines", "14) Waive fine",
            ]
            actions["10"] = self._do_add_book
            actions["11"] = self._do_remove_book
            actions["12"] = self._print_overdue
            actions["13"] = lambda: self._print_fines(self.service.all_fines())
            actions["14"] = self._do_waive_fine
        print("  ".join(lines))

        choice = input("> ").strip()
        action = actions.get(choice)
        if action is None:
            print("Invalid choice.")
            return
        try:
            action()
        except ValueError as e:
            print(f"Error: {e}")

    def _quit(self):
        print("Goodbye.")
        raise SystemExit(0)

    def _do_register(self):
        try:
            name = require_non_empty(input("Name: "), "Name")
            email = require_non_empty(input("Email: "), "Email")
            username = require_non_empty(input("Username: "), "Username")
            password = getpass.getpass("Password: ")
            role = input("Role (member/librarian) [member]: ").strip() or "member"
            self.auth.register(name, email, username, password, role)
            print("Registered! You can now log in.")
        except ValueError as e:
            print(f"Error: {e}")

    def _do_login(self):
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        try:
            self.auth.login(username, password)
            print(f"Welcome back, {self.auth.current_user.name}.")
        except ValueError as e:
            print(f"Error: {e}")

    def _do_logout(self):
        self.auth.logout()
        print("Logged out.")

    # ---------------- display helpers ----------------

    def _print_books(self, books):
        if not books:
            print("No books found.")
            return
        rows = [
            [b.id, b.title, b.author, b.category, self.service.available_count(b.id)]
            for b in books
        ]
        print(tabulate(rows, headers=["ID", "Title", "Author", "Category", "Available"], tablefmt="simple"))

    def _print_my_loans(self):
        loans = self.service.my_loans()
        if not loans:
            print("You have no loans.")
            return
        for l in loans:
            print(l)

    def _print_overdue(self):
        loans = self.service.list_overdue()
        if not loans:
            print("Nothing overdue.")
            return
        for l in loans:
            print(l)

    def _print_fines(self, fines):
        if not fines:
            print("No outstanding fines.")
            return
        for l in fines:
            print(l)

    # ---------------- actions ----------------

    def _do_search(self):
        title = input("Title contains (blank to skip): ").strip() or None
        author = input("Author contains (blank to skip): ").strip() or None
        category = input("Category contains (blank to skip): ").strip() or None
        self._print_books(self.service.search_books(title=title, author=author, category=category))

    def _do_add_book(self):
        title = require_non_empty(input("Title: "), "Title")
        author = require_non_empty(input("Author: "), "Author")
        isbn = require_non_empty(input("ISBN: "), "ISBN")
        category = require_non_empty(input("Category: "), "Category")
        copies = require_positive_int(input("Copies: "), "Copies")
        self.service.add_book(title, author, isbn, category, copies)
        print("Book added.")

    def _do_remove_book(self):
        book_id = require_positive_int(input("Book id to remove: "), "Book id")
        self.service.remove_book(book_id)
        print("Book removed.")

    def _do_checkout(self):
        book_id = require_positive_int(input("Book id to checkout: "), "Book id")
        loan = self.service.checkout_book(book_id)
        if loan:
            print(f"Checked out. Due {loan.due_date}.")

    def _do_return(self):
        loan_id = require_positive_int(input("Loan id to return: "), "Loan id")
        loan = self.service.return_book(loan_id)
        if loan:
            if loan.fine_amount:
                print(f"Returned. Fine: ${loan.fine_amount:.2f}")
            else:
                print("Returned. No fine — thanks!")

    def _do_join_waitlist(self):
        book_id = require_positive_int(input("Book id to wait for: "), "Book id")
        self.service.join_waitlist(book_id)
        print("Added to the waitlist. You'll get first claim on the next return.")

    def _do_waive_fine(self):
        loan_id = require_positive_int(input("Loan id to waive fine for: "), "Loan id")
        self.service.waive_fine(loan_id)
        print("Fine waived.")


# ---------------- argparse one-shot subcommands ----------------

def build_parser():
    parser = argparse.ArgumentParser(prog="library-cli", description="Library Management CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("menu", help="Launch the interactive menu (default if no command given)")

    p_register = sub.add_parser("register", help="Register a new user")
    p_register.add_argument("--name", required=True)
    p_register.add_argument("--email", required=True)
    p_register.add_argument("--username", required=True)
    p_register.add_argument("--role", choices=["member", "librarian"], default="member")

    sub.add_parser("list-books", help="List all books in the catalog")

    p_search = sub.add_parser("search", help="Search the catalog")
    p_search.add_argument("--title")
    p_search.add_argument("--author")
    p_search.add_argument("--category")

    p_add = sub.add_parser("add-book", help="Add a book (librarian only)")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--author", required=True)
    p_add.add_argument("--isbn", required=True)
    p_add.add_argument("--category", required=True)
    p_add.add_argument("--copies", type=int, required=True)
    p_add.add_argument("--username", required=True, help="Librarian username")

    p_remove = sub.add_parser("remove-book", help="Remove a book (librarian only)")
    p_remove.add_argument("--book-id", type=int, required=True)
    p_remove.add_argument("--username", required=True)

    p_checkout = sub.add_parser("checkout", help="Check out a book")
    p_checkout.add_argument("--book-id", type=int, required=True)
    p_checkout.add_argument("--username", required=True)

    p_return = sub.add_parser("return-book", help="Return a book")
    p_return.add_argument("--loan-id", type=int, required=True)
    p_return.add_argument("--username", required=True)

    p_wait = sub.add_parser("waitlist", help="Join the waitlist for an unavailable book")
    p_wait.add_argument("--book-id", type=int, required=True)
    p_wait.add_argument("--username", required=True)

    p_overdue = sub.add_parser("list-overdue", help="List overdue loans (librarian only)")
    p_overdue.add_argument("--username", required=True)

    p_fines = sub.add_parser("fines", help="View fines: own (member) or all (librarian)")
    p_fines.add_argument("--username", required=True)

    p_waive = sub.add_parser("waive-fine", help="Waive a fine (librarian only)")
    p_waive.add_argument("--loan-id", type=int, required=True)
    p_waive.add_argument("--username", required=True)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    cli = LibraryCLI()

    if args.command is None or args.command == "menu":
        try:
            cli.run_interactive()
        except (KeyboardInterrupt, SystemExit):
            print("\nGoodbye.")
        return

    if args.command == "register":
        password = getpass.getpass("Password: ")
        try:
            cli.auth.register(args.name, args.email, args.username, password, args.role)
            print("Registered.")
        except ValueError as e:
            print(f"Error: {e}")
        return

    if args.command == "list-books":
        cli._print_books(cli.service.list_books())
        return

    if args.command == "search":
        cli._print_books(cli.service.search_books(title=args.title, author=args.author, category=args.category))
        return

    # Everything below requires a logged-in user for this one-shot invocation.
    password = getpass.getpass("Password: ")
    try:
        cli.auth.login(args.username, password)
    except ValueError as e:
        print(f"Error: {e}")
        return

    try:
        if args.command == "add-book":
            cli.service.add_book(args.title, args.author, args.isbn, args.category, args.copies)
            print("Book added.")
        elif args.command == "remove-book":
            cli.service.remove_book(args.book_id)
            print("Book removed.")
        elif args.command == "checkout":
            loan = cli.service.checkout_book(args.book_id)
            if loan:
                print(f"Checked out. Due {loan.due_date}.")
        elif args.command == "return-book":
            loan = cli.service.return_book(args.loan_id)
            if loan:
                if loan.fine_amount:
                    print(f"Returned. Fine: ${loan.fine_amount:.2f}")
                else:
                    print("Returned. No fine.")
        elif args.command == "waitlist":
            cli.service.join_waitlist(args.book_id)
            print("Added to the waitlist.")
        elif args.command == "list-overdue":
            cli._print_overdue()
        elif args.command == "fines":
            if cli.auth.current_user.role == "librarian":
                cli._print_fines(cli.service.all_fines())
            else:
                cli._print_fines(cli.service.my_fines())
        elif args.command == "waive-fine":
            cli.service.waive_fine(args.loan_id)
            print("Fine waived.")
    except ValueError as e:
        print(f"Error: {e}")
