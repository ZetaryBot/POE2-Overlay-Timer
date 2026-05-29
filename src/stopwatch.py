"""
Stopwatch with three pause modes:
  - toggle()      : user-initiated start/pause (F4)
  - auto_pause()  : triggered by PoE2 losing focus → auto_resume() on regain
  - crash_pause() : triggered by PoE2 crash      → requires manual F4 to resume
  - reset()       : Ctrl+0, back to 00:00:00
"""
import time
import threading


class Stopwatch:
    def __init__(self):
        self._lock        = threading.Lock()
        self._accumulated = 0.0
        self._start_time  = None   # monotonic timestamp when last started
        self.is_paused    = True
        self.has_started  = False  # False until user presses F4 at least once
        self._auto_paused = False  # True only when paused by focus-loss

    # ── User actions ──────────────────────────────────────────────────────

    def toggle(self):
        """F4: start if paused, pause if running."""
        with self._lock:
            if self.is_paused:
                self._start_time  = time.monotonic()
                self.is_paused    = False
                self.has_started  = True
                self._auto_paused = False
            else:
                self._accumulate()
                self.is_paused    = True
                self._auto_paused = False  # manual pause, not auto

    def reset(self):
        """Ctrl+0: stop and zero the counter."""
        with self._lock:
            self._accumulated = 0.0
            self._start_time  = None
            self.is_paused    = True
            self.has_started  = False
            self._auto_paused = False

    # ── Automatic actions (called by PoeMonitor) ──────────────────────────

    def auto_pause(self):
        """Pause because PoE2 lost focus; can be undone by auto_resume."""
        with self._lock:
            if not self.is_paused:
                self._accumulate()
                self.is_paused    = True
                self._auto_paused = True

    def auto_resume(self):
        """Resume only if previously auto-paused (not manually paused)."""
        with self._lock:
            if self.is_paused and self._auto_paused and self.has_started:
                self._start_time  = time.monotonic()
                self.is_paused    = False
                self._auto_paused = False

    def crash_pause(self):
        """Pause because PoE2 crashed – needs manual F4 to restart."""
        with self._lock:
            if not self.is_paused:
                self._accumulate()
                self.is_paused = True
            self._auto_paused = False  # do NOT auto-resume after a crash

    # ── Query ─────────────────────────────────────────────────────────────

    def get_elapsed(self) -> float:
        """Current elapsed seconds (thread-safe)."""
        with self._lock:
            if not self.is_paused and self._start_time is not None:
                return self._accumulated + (time.monotonic() - self._start_time)
            return self._accumulated

    # ── Internal ──────────────────────────────────────────────────────────

    def _accumulate(self):
        """Add running time to _accumulated. Call only while holding _lock."""
        if self._start_time is not None:
            self._accumulated += time.monotonic() - self._start_time
            self._start_time = None
