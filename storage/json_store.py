import json
import os


class JSONStore:
    """Generic JSON-backed collection loader/saver.

    Every model (users, books, loans) gets its own JSONStore pointed at a
    different file, so persistence logic lives in exactly one place.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def load(self):
        """Return the list of records, or [] if the file is missing/empty/corrupt."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: could not read {self.filepath} ({e}). Starting with empty data.")
            return []

    def save(self, records):
        try:
            with open(self.filepath, "w") as f:
                json.dump(records, f, indent=2)
        except OSError as e:
            print(f"Error: could not save to {self.filepath}: {e}")