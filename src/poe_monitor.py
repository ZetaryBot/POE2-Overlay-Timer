"""
Monitors:
  1. PoE2 window focus  → show/hide overlay, auto-pause/resume stopwatch
  2. PoE2 process life  → crash detection → crash_pause
  3. Client.txt         → area-entered events → update map notes
"""
import os
import re
import time
import threading
import winreg

import win32gui
import win32process
import psutil

from src.stopwatch import Stopwatch


# Primary pattern: PoE2 uses [SCENE] Set Source [AreaName] in Client.txt
# Skip the reset line where source is (null)
_SCENE_PATTERN = re.compile(r'\[SCENE\] Set Source \[(?!\(null\))(.+)\]')

# Fallback patterns for "You have entered …" (PoE1 style / older PoE2 builds)
_AREA_PATTERNS = [
    re.compile(r'You have entered (.+)\.$'),          # EN
    re.compile(r'你進入了 (.+)\.$'),                   # ZH-TW
    re.compile(r'你进入了 (.+)\.$'),                   # ZH-CN
    re.compile(r'당신은 (.+)에 들어섰습니다\.$'),      # KO
    re.compile(r'Sie haben (.+) betreten\.$'),         # DE
    re.compile(r'Vous êtes entré(?:e)? dans (.+)\.$'), # FR
    re.compile(r'Hai raggiunto (.+)\.$'),              # IT
    re.compile(r'Entraste em (.+)\.$'),                # PT
    re.compile(r'Вы вошли в (.+)\.$'),                 # RU
    re.compile(r'Ha entrado en (.+)\.$'),              # ES
]

_POE2_EXECUTABLES = frozenset({
    'pathofexile2.exe',
    'pathofexile.exe',
    'pathofexilesteam.exe',
    'pathofexile2steam.exe',
})


class PoeMonitor:
    def __init__(self, config: dict, overlay, stopwatch: Stopwatch,
                 debug: bool = False):
        self._config    = config
        self._overlay   = overlay
        self._stopwatch = stopwatch
        self._debug     = debug

        self._running = False
        self._threads: list[threading.Thread] = []

        self._poe2_hwnd: int | None = None
        self._poe2_pid:  int | None = None

        self._was_running = False
        self._was_focused = False

    def _log(self, msg: str):
        if self._debug:
            print(f'[monitor] {msg}')

    # ── Public ────────────────────────────────────────────────────────────

    def start(self):
        self._running = True
        t_focus = threading.Thread(
            target=self._focus_loop, daemon=True, name='poe-focus'
        )
        t_log = threading.Thread(
            target=self._log_loop, daemon=True, name='poe-log'
        )
        self._threads = [t_focus, t_log]
        t_focus.start()
        t_log.start()

    def stop(self):
        self._running = False

    def is_poe2_focused(self) -> bool:
        if self._poe2_hwnd is None:
            return False
        try:
            fg = win32gui.GetForegroundWindow()
            return fg != 0 and fg == self._poe2_hwnd
        except Exception:
            return False

    # ── Window / process detection ────────────────────────────────────────

    def _find_poe2_window(self) -> bool:
        """Scan all visible windows; populate _poe2_hwnd / _poe2_pid."""
        found: list[tuple[int, int]] = []

        def _enum_cb(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            title = win32gui.GetWindowText(hwnd)
            if 'Path of Exile' not in title:
                return True
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc = psutil.Process(pid)
                if proc.name().lower() in _POE2_EXECUTABLES:
                    found.append((hwnd, pid))
            except Exception:
                pass
            return True

        try:
            win32gui.EnumWindows(_enum_cb, None)
        except Exception:
            pass

        if found:
            self._poe2_hwnd, self._poe2_pid = found[0]
            try:
                name = psutil.Process(self._poe2_pid).name()
            except Exception:
                name = '?'
            self._log(f'PoE2 window found  pid={self._poe2_pid}  exe={name}')
            return True
        self._poe2_hwnd = None
        self._poe2_pid  = None
        return False

    def _is_process_alive(self) -> bool:
        if self._poe2_pid is None:
            return False
        try:
            p = psutil.Process(self._poe2_pid)
            return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            return False

    # ── Focus loop ────────────────────────────────────────────────────────

    def _focus_loop(self):
        while self._running:
            try:
                if not self._is_process_alive():
                    self._find_poe2_window()

                running = self._is_process_alive()
                focused = self.is_poe2_focused() if running else False

                if not running:
                    if self._was_running:
                        # PoE2 just died / crashed
                        self._log('PoE2 process gone – crash_pause')
                        self._stopwatch.crash_pause()
                        self._schedule(self._overlay.hide)
                        self._was_running = False
                        self._was_focused = False
                        self._poe2_hwnd   = None
                        self._poe2_pid    = None
                elif focused:
                    if not self._was_focused:
                        # Just gained focus
                        self._log('PoE2 gained focus – showing overlay')
                        self._schedule(self._overlay.show)
                        self._stopwatch.auto_resume()
                        self._was_focused = True
                    self._was_running = True
                else:
                    # Running but not focused
                    if self._was_focused:
                        self._log('PoE2 lost focus – hiding overlay')
                        self._schedule(self._overlay.hide)
                        self._stopwatch.auto_pause()
                        self._was_focused = False
                    self._was_running = True

            except Exception:
                pass

            time.sleep(0.25)

    # ── Client.txt log loop ───────────────────────────────────────────────

    def _find_client_txt(self) -> str | None:
        # 1. User-configured path
        cfg = self._config.get('client_log_path', '').strip()
        if cfg and os.path.isfile(cfg):
            return cfg

        # 2. Derive from running process exe
        if self._poe2_pid:
            try:
                exe  = psutil.Process(self._poe2_pid).exe()
                path = os.path.join(os.path.dirname(exe), 'logs', 'Client.txt')
                if os.path.isfile(path):
                    self._config['client_log_path'] = path
                    return path
            except Exception:
                pass

        # 3. Steam registry lookup
        for reg_root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for subkey in (
                r'SOFTWARE\WOW6432Node\Valve\Steam',
                r'SOFTWARE\Valve\Steam',
            ):
                try:
                    key        = winreg.OpenKey(reg_root, subkey)
                    steam_path, _ = winreg.QueryValueEx(key, 'InstallPath')
                    winreg.CloseKey(key)
                    candidate  = os.path.join(
                        steam_path, 'steamapps', 'common',
                        'Path of Exile 2', 'logs', 'Client.txt'
                    )
                    if os.path.isfile(candidate):
                        self._config['client_log_path'] = candidate
                        return candidate
                except Exception:
                    pass

        # 4. Brute-force common drive letters
        for drive in ('C', 'D', 'E', 'F', 'G'):
            for rel in (
                r'Program Files (x86)\Steam\steamapps\common\Path of Exile 2\logs\Client.txt',
                r'Program Files\Steam\steamapps\common\Path of Exile 2\logs\Client.txt',
                r'SteamLibrary\steamapps\common\Path of Exile 2\logs\Client.txt',
                r'Games\Path of Exile 2\logs\Client.txt',
            ):
                path = f'{drive}:\\{rel}'
                if os.path.isfile(path):
                    self._config['client_log_path'] = path
                    return path

        return None

    def _log_loop(self):
        missing_ticks = 0
        while self._running:
            path = self._find_client_txt()
            if not path:
                missing_ticks += 1
                # Only warn after PoE2 is detected and a few retries failed,
                # to avoid the spurious startup message before _poe2_pid is set.
                if self._poe2_pid is not None and missing_ticks >= 2:
                    print('[monitor] Client.txt not found. '
                          'Set "client_log_path" in config.json if auto-detect fails.')
                    missing_ticks = 0   # re-arm: warn again if it disappears later
                time.sleep(5)
                continue
            missing_ticks = 0
            self._log(f'Reading Client.txt: {path}')
            print(f'[monitor] Client.txt found: {path}')
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    # ── Seed the overlay with the last known area ──────────
                    last_map = self._read_last_map(fh)
                    if last_map:
                        notes = self._overlay.notes_manager.find_notes(last_map)
                        print(f'[monitor] Last location: {last_map!r} '
                              f'({"notes found" if notes else "no notes"})')
                        self._schedule(
                            lambda mn=last_map, nt=notes: self._overlay.set_map(mn, nt)
                        )
                    # ── Tail from end for new entries ──────────────────────
                    fh.seek(0, 2)
                    self._log('Tailing log – waiting for area entry...')
                    while self._running:
                        line = fh.readline()
                        if not line:
                            time.sleep(0.3)
                            continue
                        self._check_line(line.rstrip())
            except OSError:
                time.sleep(2)

    def _check_line(self, line: str):
        # PoE2 primary: [SCENE] Set Source [AreaName]
        m = _SCENE_PATTERN.search(line)
        if not m:
            # Fallback: "You have entered …" style
            for pattern in _AREA_PATTERNS:
                m = pattern.search(line)
                if m:
                    break
        if not m:
            return
        map_name = m.group(1).strip()
        notes    = self._overlay.notes_manager.find_notes(map_name)
        has_note = bool(notes)
        print(f'[monitor] Entered map: {map_name!r}  '
              f'({"notes found" if has_note else "no notes"})')
        self._schedule(
            lambda mn=map_name, nt=notes: self._overlay.set_map(mn, nt)
        )
    def _read_last_map(self, fh) -> str | None:
        """Return the most recent area name written to Client.txt."""
        try:
            fh.seek(0, 2)
            size = fh.tell()
            read_size = min(64 * 1024, size)   # scan last 64 KB
            fh.seek(max(0, size - read_size))
            tail = fh.read()
            last_map = None
            for line in tail.splitlines():
                m = _SCENE_PATTERN.search(line)
                if m:
                    candidate = m.group(1).strip()
                    if candidate:
                        last_map = candidate
                    continue
                for pattern in _AREA_PATTERNS:
                    m = pattern.search(line)
                    if m:
                        last_map = m.group(1).strip()
                        break
            return last_map
        except Exception:
            return None
    # ── Helpers ───────────────────────────────────────────────────────────

    def _schedule(self, fn):
        """Run *fn* on the tkinter main thread; silently ignore if destroyed."""
        try:
            self._overlay.root.after(0, fn)
        except Exception:
            pass
