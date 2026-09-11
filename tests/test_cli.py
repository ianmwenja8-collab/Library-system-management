"""
test for Ian's layer (cli/cli.py + utils/validators.py).

These deliberately avoid mocking input()/argparse's sys.argv wiring in
depth — that gets brittle fast. Instead they test the two things that
are actually worth locking down: the subcommand surface exists as agreed,
and the validators reject bad input the way the contract says they should.
"""
from cli.cli import build_parser
from utils.validators import require_non_empty, require_positive_int


EXPECTED_SUBCOMMANDS = {
    "menu", "register", "list-books", "search", "add-book", "remove-book",
    "checkout", "return-book", "waitlist", "list-overdue", "fines", "waive-fine",
}


def test_all_agreed_subcommands_exist():
    parser = build_parser()
    # argparse doesn't expose subparser names directly; pull them from the
    # subparsers action's choices dict.
    subparsers_action = next(
        a for a in parser._actions if a.dest == "command"
    )
    assert set(subparsers_action.choices.keys()) == EXPECTED_SUBCOMMANDS


def test_checkout_requires_book_id_and_username():
    parser = build_parser()
   args = parser.parse_args(["checkout", "--book-id", "1", "--username", "amy"])
    assert args.book_id == 1
    assert args.username == "amy"


def test_add_book_requires_all_fields():
    parser = build_parser()
    # Missing --copies should cause argparse to error out (SystemExit).
    try:
        parser.parse_args([
            "add-book", "--title", "Dune", "--author", "Herbert",
            "--isbn", "111", "--category", "Sci-Fi", "--username", "vic",
        ])
        assert False, "expected SystemExit for missing --copies"
    except SystemExit:
        pass


def test_require_non_empty_rejects_blank():
    try:
        require_non_empty("   ", "Title")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_require_non_empty_strips_and_returns():
    assert require_non_empty("  Dune  ", "Title") == "Dune"


def test_require_positive_int_rejects_zero_and_negative():
    for bad in ("0", "-3"):
        try:
            require_positive_int(bad, "Copies")
            assert False, f"expected ValueError for {bad}"
        except ValueError:
            pass


def test_require_positive_int_rejects_non_numeric():
    try:
        require_positive_int("abc", "Copies")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_require_positive_int_accepts_valid():
    assert require_positive_int("3", "Copies") == 3
