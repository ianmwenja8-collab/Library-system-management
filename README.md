# Library Management CLI

A command-line library management system.
Members can browse the catalog, check out and return books, and view their
own loan history. Librarians can additionally manage the catalog and see
which loans are overdue.

## Team

| Person | Owns | Rubric focus |
|---|---|---|
| Allan | `models/`, `auth/` | OOP Design (inheritance, encapsulation) |
| Edger | `services/library_service.py` | OOP Design (multi-class relationships), Persistence, RBAC |
| Ian | `cli/`, `main.py`, `utils/`, `storage/` | CLI, Persistence, Code Structure |
| Victor | `tests/`, this README, Git workflow (`CONTRIBUTING.md`) | Testing & Debugging, Git Workflow |

## Features

- User registration and login with salted, hashed passwords (no plaintext
  passwords are ever stored or logged)
- Role-based access: `member` vs `librarian`, enforced with decorators
  (`@login_required`, `@role_required`)
- Per-copy tracking: a `Book` is catalog metadata; each physical `Copy` has
  its own status (`available` / `borrowed` / `reserved`), so the system
  knows exactly which copy is out, not just how many
- Catalog search by title, author, or category
- Waitlist queue: if all copies are out, join the queue; the next returned
  copy is automatically reserved for the next person in line instead of
  going back into general circulation
- Tiered, capped overdue fines: rate and cap depend on the borrower's role
  (`LibraryService.FINE_RATE_PER_DAY` / `FINE_CAP`), and a librarian can
  waive a fine
- JSON file persistence for users, books, copies, loans, and waitlists —
  no database required
- Both an interactive menu (`python main.py`) and one-shot `argparse`
  subcommands for scripting/grading
- Input validation with clear error messages instead of stack traces
- Uses the `tabulate` package for a clean book-listing table

## Project structure

```
main.py                  # entry point
models/                  # Person -> User -> Librarian/Member, Book, Copy, Loan, Waitlist
auth/                    # AuthManager (register/login) + decorators
storage/                 # generic JSONStore load/save with error handling
services/                # LibraryService: the business logic
cli/                     # argparse subcommands + interactive menu
utils/                   # input validators
data/                    # users/books/copies/loans/waitlists.json (generated at runtime)
tests/                   # pytest suite
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

Interactive menu (recommended — this is the main experience):

```bash
python main.py
```

One-shot subcommands (each prompts for a password where needed):

```bash
python main.py register --name "Vic" --email vic@example.com --username vic --role librarian
python main.py list-books
python main.py add-book --title Dune --author "Frank Herbert" --isbn 111 --copies 3 --username vic
python main.py checkout --book-id 1 --username someMember
python main.py return-book --loan-id 1 --username someMember
python main.py list-overdue --username vic
```

## Entities and relationships

- `Person` (base) → `User` (adds credentials) → `Librarian` / `Member` (roles)
- `User` (specifically `Member`) → many `Loan`s (one-to-many)
- `Book` → many `Loan`s over its lifetime (one-to-many)
- `Loan` is the join entity linking a member to a book with checkout/due/return dates

## Running tests

```bash
pytest
```

## Known issues / limitations

- Sessions are per-process only: the interactive menu keeps you logged in
  for the whole session, but each one-shot `argparse` subcommand re-prompts
  for a password since there's no persistent session token between
  separate CLI invocations.
- No password reset flow.
- Loan period is a fixed 14 days (`Loan.LOAN_PERIOD_DAYS`), not configurable
  from the CLI yet.
