import json
import os


class TodoList:
    """Stores the to-do items and saves them to a JSON file so they survive restarts."""

    def __init__(self, save_path: str):
        self.save_path = save_path
        self.items = []  # each item: {"text": str, "done": bool}
        self.load()

    def load(self):
        """Loads saved tasks. A missing or broken file just gives an empty list."""
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.items = [
                {"text": str(entry["text"]), "done": bool(entry.get("done", False))}
                for entry in data
                if isinstance(entry, dict) and "text" in entry
            ]
        except (OSError, ValueError, TypeError):
            self.items = []

    def save(self):
        """Writes to a temp file first, so a crash mid-save can't wipe the list."""
        tmp_path = self.save_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.save_path)
        except OSError:
            pass

    def add(self, text: str) -> bool:
        text = text.strip()
        if not text:
            return False
        self.items.append({"text": text, "done": False})
        self.save()
        return True

    def toggle(self, index: int):
        if 0 <= index < len(self.items):
            self.items[index]["done"] = not self.items[index]["done"]
            self.save()

    def remove(self, index: int):
        if 0 <= index < len(self.items):
            del self.items[index]
            self.save()

    def clear_done(self):
        self.items = [item for item in self.items if not item["done"]]
        self.save()

    def remaining(self) -> int:
        return sum(1 for item in self.items if not item["done"])