"""
Application root – wires all components together.
"""
import json
import os

from src.stopwatch   import Stopwatch
from src.notes       import NotesManager
from src.overlay     import OverlayWindow
from src.poe_monitor import PoeMonitor
from src.hotkeys     import HotkeyManager

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')


class App:
    def __init__(self, debug: bool = False, test_map: str | None = None,
                 list_notes: bool = False):
        self._debug      = debug
        self._test_map   = test_map
        self._list_notes = list_notes

        self.config       = self._load_config()
        self.stopwatch    = Stopwatch()
        self.notes_mgr    = NotesManager(self.config)
        self.overlay      = OverlayWindow(self.config, self.stopwatch, self.notes_mgr,
                                          save_config=self._save_config)
        self.poe_monitor  = PoeMonitor(self.config, self.overlay, self.stopwatch,
                                       debug=debug)
        self.hotkey_mgr   = HotkeyManager(
            self.config, self.overlay, self.stopwatch, self.poe_monitor
        )
        # Back-reference so overlay context menu can reach poe_monitor
        self.overlay.poe_monitor = self.poe_monitor

    # ── Config I/O ────────────────────────────────────────────────────────────

    def _load_config(self) -> dict:
        try:
            with open(_CONFIG_PATH, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        except Exception as exc:
            print(f'[config] Could not load config.json: {exc}')
            return {}

    def _save_config(self):
        try:
            with open(_CONFIG_PATH, 'w', encoding='utf-8') as fh:
                json.dump(self.config, fh, indent=2, ensure_ascii=False)
        except Exception as exc:
            print(f'[config] Could not save config.json: {exc}')

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        # ── --list-notes: print all parsed entries and exit ───────────────
        if self._list_notes:
            entries = self.notes_mgr._notes
            if not entries:
                print('[notes] No entries found. '
                      'Make sure .txt files exist in the notes/ folder.')
            else:
                print(f'[notes] {len(entries)} entries loaded:')
                for key, (canonical, body) in sorted(entries.items()):
                    preview = body[:60].replace('\n', ' ')
                    print(f'  {canonical!r:40s} → {preview!r}')
            return

        # ── --debug / --test-map: show overlay immediately ─────────────────
        if self._debug:
            print('[debug] Debug mode – overlay always visible, PoE2 not required.')
            self.overlay.root.after(200, self.overlay.show)

        if self._test_map:
            notes = self.notes_mgr.find_notes(self._test_map)
            if notes:
                print(f'[test] Notes found for {self._test_map!r}:\n{notes}\n')
            else:
                print(f'[test] No notes found for {self._test_map!r}. '
                      f'Check spelling or notes/ files.')
            self.overlay.root.after(
                300,
                lambda: self.overlay.set_map(self._test_map, notes)
            )

        self.poe_monitor.start()
        self.hotkey_mgr.start()
        try:
            self.overlay.run()      # blocks until window is closed
        finally:
            self.poe_monitor.stop()
            self.hotkey_mgr.stop()
            self._save_config()
