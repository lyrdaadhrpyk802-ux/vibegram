# ============================================
#  userapi/session.py - session storage
#  All code and comments are English. No emojis.
# ============================================
import json
import os
from pathlib import Path


DEFAULT_PATH = Path.home() / ".vibe_session.json"


class Session:
    """Minimal session store for auth key, dc_id, server salt."""

    def __init__(self, path=DEFAULT_PATH):
        self.path = Path(path)
        self.data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except Exception:
                return {}
        return {}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2))
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def clear(self):
        self.data = {}
        if self.path.exists():
            self.path.unlink()
