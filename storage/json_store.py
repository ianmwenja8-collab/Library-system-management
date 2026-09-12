import json
from pathlib import Path


class JSONStore:
    """Save and load information from a JSON file."""

    def __init__(self, filename):
        self.filename = Path(filename)

    def load(self):
        """Load data from the file."""
        if not self.filename.exists():
            return []

        try:
            with self.filename.open("r", encoding="utf-8") as file:
                return json.load(file)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"{self.filename} contains invalid JSON."
            ) from error

        except PermissionError as error:
            raise PermissionError(
                f"Cannot read {self.filename}."
            ) from error

    def save(self, data):
        """Save data to the file."""
        self.filename.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        try:
            with self.filename.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)

        except PermissionError as error:
            raise PermissionError(
                f"Cannot write to {self.filename}."
            ) from error
