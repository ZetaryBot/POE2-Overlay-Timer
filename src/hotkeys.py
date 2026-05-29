"""
Global hotkey registration.

All handlers check is_poe2_focused() before acting, so pressing V or F4
in Discord / browser does nothing.

Hotkeys (defaults, configurable in config.json except Ctrl+0):
  V        → copy current notes text to clipboard
  F4       → toggle stopwatch (start / pause)
  HOME     → toggle notes content visibility
  Ctrl+0   → reset stopwatch (hard-coded combo to prevent accidents)
"""
import pyperclip
import keyboard

from src.stopwatch import Stopwatch
from src.overlay   import OverlayWindow


class HotkeyManager:
    def __init__(
        self,
        config:      dict,
        overlay:     OverlayWindow,
        stopwatch:   Stopwatch,
        poe_monitor,              # PoeMonitor – passed as Any to avoid circular import
    ):
        self._config      = config
        self._overlay     = overlay
        self._stopwatch   = stopwatch
        self._poe_monitor = poe_monitor
        self._hk          = config.get('hotkeys', {})
        self._hooks: list = []

    # ── Public ────────────────────────────────────────────────────────────────

    def start(self):
        hk = self._hk

        self._hooks.append(
            keyboard.on_press_key(
                hk.get('stopwatch_toggle', 'f4'),
                self._on_stopwatch_toggle,
                suppress=False,
            )
        )
        self._hooks.append(
            keyboard.on_press_key(
                hk.get('copy_notes', 'v'),
                self._on_copy_notes,
                suppress=False,
            )
        )
        self._hooks.append(
            keyboard.on_press_key(
                hk.get('hide_content', 'home'),
                self._on_hide_content,
                suppress=False,
            )
        )
        # Ctrl+0 is not in hotkeys config (intentional – prevent accidents)
        keyboard.add_hotkey('ctrl+0', self._on_reset_stopwatch, suppress=False)

    def stop(self):
        for hook in self._hooks:
            try:
                keyboard.remove(hook)
            except Exception:
                pass
        self._hooks.clear()
        try:
            keyboard.remove_hotkey('ctrl+0')
        except Exception:
            pass

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _focused(self) -> bool:
        return self._poe_monitor.is_poe2_focused()

    def _on_stopwatch_toggle(self, _e=None):
        if self._focused():
            # Schedule on tkinter thread to stay thread-safe
            self._schedule(self._stopwatch.toggle)

    def _on_copy_notes(self, _e=None):
        if self._focused():
            notes = self._overlay.get_notes_text()
            if notes:
                try:
                    pyperclip.copy(notes)
                except Exception:
                    pass

    def _on_hide_content(self, _e=None):
        if self._focused():
            self._schedule(self._overlay.toggle_content)

    def _on_reset_stopwatch(self):
        if self._focused():
            self._schedule(self._stopwatch.reset)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _schedule(self, fn):
        try:
            self._overlay.root.after(0, fn)
        except Exception:
            pass
