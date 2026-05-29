"""
Loads and queries map notes from .txt files in the notes/ folder.

Notes file format:
    [Map Name EN / 地圖名稱 ZH / 다른언어]
    {
    Your notes here.
    Multiple lines are fine.
    }

Multiple blocks can live in one file.
The special file template_empty.txt is never scanned.
"""
import os
import re


class NotesManager:
    # Matches  [names]  { content }  anywhere in the file
    _BLOCK_RE = re.compile(r'\[([^\]]+)\]\s*\{([^}]*)\}', re.DOTALL)

    def __init__(self, config: dict):
        self._config = config
        # key: normalised map name (lowercase stripped)
        # value: (canonical_name: str, body: str)
        self._notes: dict[str, tuple[str, str]] = {}
        self.reload()

    # ── Public ────────────────────────────────────────────────────────────

    def reload(self):
        self._notes.clear()
        notes_dir = self._notes_dir()
        os.makedirs(notes_dir, exist_ok=True)
        for fname in sorted(os.listdir(notes_dir)):
            if fname.lower().endswith('.txt') and fname != 'template_empty.txt':
                self._parse_file(os.path.join(notes_dir, fname))

    def find_notes(self, map_name: str) -> str:
        """Return note body for *map_name*, or '' if not found."""
        key = map_name.strip().lower()
        if key in self._notes:
            return self._notes[key][1]
        # Fallback: substring / partial match
        for stored_key, (_, body) in self._notes.items():
            if stored_key in key or key in stored_key:
                return body
        return ''

    # ── Private ───────────────────────────────────────────────────────────

    def _notes_dir(self) -> str:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, 'notes')

    def _parse_file(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except OSError:
            return
        for m in self._BLOCK_RE.finditer(text):
            names_raw = m.group(1)
            body      = m.group(2).strip()
            # Split multi-language names separated by '/'
            names = [n.strip() for n in names_raw.split('/') if n.strip()]
            if not names:
                continue
            canonical = names[0]
            for name in names:
                self._notes[name.lower()] = (canonical, body)
