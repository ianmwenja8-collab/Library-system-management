"""Person model for the library management system."""

class Person:
    """Base class for people who use the library system."""

    def __init__(self, name, email):
        self.name = name
        self.email = email

    @property
    def name(self):
        """Return the person's name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set and validate the person's name."""
        if not isinstance(value, str):
            raise ValueError("Name must be a string.")

        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty.")

        self._name = value

    @property
    def email(self):
        """Return the person's email address."""
        return self._email

    @email.setter
    def email(self, value):
        """Set and validate the person's email address."""
        if not isinstance(value, str):
            raise ValueError("Email must be a string.")

        value = value.strip().lower()
        if not value or "@" not in value:
            raise ValueError("Please provide a valid email address.")

        self._email = value

    def to_dict(self):
        """Convert the person into a dictionary for saving."""
        return {
            "name": self.name,
            "email": self.email,
        }

    def __str__(self):
        return f"{self.name} ({self.email})"
