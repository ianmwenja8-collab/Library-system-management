def run_cli():
    """Display the library menu."""

    while True:
        print("\nLibrary System")
        print("1. Search for a book")
        print("2. Borrow a book")
        print("3. Return a book")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            print("Search selected.")

        elif choice == "2":
            print("Borrow selected.")

        elif choice == "3":
            print("Return selected.")

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice.")
