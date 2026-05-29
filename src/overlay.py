"""
Tkinter always-on-top overlay window.

Layout
──────
  ┌──────────────────────────────────────┐
  │  00:00:00 ⏸          The Riverbank  │  ← drag handle (timer row)
  ├──────────────────────────────────────┤
  │  Notes text (scrollable, read-only)  │  ← only when notes exist & visible
  └──────────────────────────────────────┘

Visibility:
  • Starts hidden (root.withdraw).
  • PoeMonitor calls show() / hide() from its background thread via root.after().
  • Notes section shown/hidden by toggle_content() (HOME key).
  • Auto-sizes height based on note line count.

Drag:
  • Click-drag anywhere on the timer row moves the window.
  • Position is persisted to config dict on drag-end (saved by App on exit).

Right-click context menu:
  • Copy notes / Reload notes / Exit
"""
import ctypes
import tkinter as tk
import tkinter.font as tkfont

from src.stopwatch import Stopwatch
from src.notes import NotesManager


# ── Colour palette ────────────────────────────────────────────────────────────
BG              = '#1A1A1A'
TIMER_IDLE_FG   = '#888888'
TIMER_RUN_FG    = '#00FF88'
TIMER_PAUSE_FG  = '#FFAA00'
NOTES_FG        = '#DEDEDE'
MAP_FG          = '#666666'
DIVIDER_COLOR   = '#2E2E2E'


class OverlayWindow:
    def __init__(self, config: dict, stopwatch: Stopwatch,
                 notes_manager: NotesManager, save_config=None):
        self._config         = config
        self._stopwatch      = stopwatch
        self.notes_manager   = notes_manager
        self._save_config_fn = save_config  # called after file selection to persist

        # Set by App after full construction
        self.poe_monitor = None

        self._current_map   = ''
        self._current_notes = ''
        self._show_content  = True
        self._is_visible    = False
        self._drag_data     = None       # (x_root, y_root, win_x, win_y)

        self.root = tk.Tk()
        self._build_window()
        self._build_ui()
        self._tick()   # start timer refresh loop

    # ── Window setup ──────────────────────────────────────────────────────────

    def _build_window(self):
        r = self.root
        r.overrideredirect(True)          # no title bar / border
        r.wm_attributes('-topmost', True)
        r.configure(bg=BG)

        screen_w  = r.winfo_screenwidth()
        self._scale = screen_w / 1920.0

        cfg = self._config.get('overlay', {})
        opacity = float(cfg.get('opacity', 0.88))
        r.wm_attributes('-alpha', max(0.1, min(1.0, opacity)))

        self._fs_timer = max(12, int(20 * self._scale))
        self._fs_notes = max(9,  int(11 * self._scale))
        self._fs_map   = max(8,  int(10 * self._scale))

        self._win_w = int(cfg.get('width', -1))
        if self._win_w <= 0:
            self._win_w = max(300, int(430 * self._scale))

        x = int(cfg.get('x', -1))
        y = int(cfg.get('y', -1))
        if x < 0:
            x = (screen_w - self._win_w) // 2
        if y < 0:
            y = max(8, int(40 * self._scale))

        self._timer_row_h = max(36, int(48 * self._scale))
        r.geometry(f'{self._win_w}x{self._timer_row_h}+{x}+{y}')

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        r = self.root
        f_timer = tkfont.Font(family='Consolas', size=self._fs_timer, weight='bold')
        f_notes = tkfont.Font(family='Consolas', size=self._fs_notes)
        f_map   = tkfont.Font(family='Consolas', size=self._fs_map)

        # ── Timer row (drag handle) ───────────────────────────────────────
        self._row_top = tk.Frame(r, bg=BG, height=self._timer_row_h)
        self._row_top.pack(fill='x')
        self._row_top.pack_propagate(False)

        self._lbl_timer = tk.Label(
            self._row_top, text='00:00:00',
            font=f_timer, fg=TIMER_IDLE_FG, bg=BG, padx=8, anchor='w'
        )
        self._lbl_timer.pack(side='left')

        self._lbl_map = tk.Label(
            self._row_top, text='',
            font=f_map, fg=MAP_FG, bg=BG, padx=6, anchor='e'
        )
        self._lbl_map.pack(side='right')

        # Drag only on timer row and its children
        for widget in (self._row_top, self._lbl_timer, self._lbl_map):
            widget.bind('<Button-1>',        self._drag_start)
            widget.bind('<B1-Motion>',       self._drag_motion)
            widget.bind('<ButtonRelease-1>', self._drag_end)

        # Right-click context menu on timer row AND notes area
        for widget in (self._row_top, self._lbl_timer, self._lbl_map):
            widget.bind('<Button-3>', self._show_context_menu)

        # ── Divider ───────────────────────────────────────────────────────
        self._divider = tk.Frame(r, bg=DIVIDER_COLOR, height=1)

        # ── Notes area ────────────────────────────────────────────────────
        self._frame_notes = tk.Frame(r, bg=BG)

        self._scrollbar = tk.Scrollbar(
            self._frame_notes, orient='vertical',
            bg='#2E2E2E', troughcolor=BG, activebackground='#555',
            relief='flat', bd=0, width=8,
        )
        # Pre-compute the text area width in characters so that
        # count('displaylines') is accurate even before first render.
        _char_px   = max(1, f_notes.measure('a'))
        _text_w_px = self._win_w - 16 - 8   # window - padx(8+8) - scrollbar
        notes_char_w = max(20, _text_w_px // _char_px)
        self._txt_notes = tk.Text(
            self._frame_notes,
            font=f_notes, fg=NOTES_FG, bg=BG,
            relief='flat', bd=0, padx=8, pady=4,
            wrap='word', state='disabled',
            cursor='arrow', exportselection=False,
            selectbackground=BG,
            yscrollcommand=self._scrollbar.set,
            width=notes_char_w,   # used by count('displaylines') before render
        )
        self._scrollbar.configure(command=self._txt_notes.yview)
        self._txt_notes.pack(side='left', fill='both', expand=True)
        # Right-click on notes area opens the same context menu
        for widget in (self._frame_notes, self._txt_notes, self._scrollbar):
            widget.bind('<Button-3>', self._show_context_menu)

        self._popup = None      # custom right-click popup (no-activate Toplevel)

        r.withdraw()   # start hidden

    # ── Drag ──────────────────────────────────────────────────────────────────

    def _drag_start(self, e: tk.Event):
        self._drag_data = (e.x_root, e.y_root,
                           self.root.winfo_x(), self.root.winfo_y())

    def _drag_motion(self, e: tk.Event):
        if self._drag_data:
            dx = e.x_root - self._drag_data[0]
            dy = e.y_root - self._drag_data[1]
            self.root.geometry(
                f'+{self._drag_data[2] + dx}+{self._drag_data[3] + dy}'
            )

    def _drag_end(self, e: tk.Event):
        if self._drag_data:
            self._config.setdefault('overlay', {})['x'] = self.root.winfo_x()
            self._config.setdefault('overlay', {})['y'] = self.root.winfo_y()
        self._drag_data = None

    # ── Context menu ──────────────────────────────────────────────────────────

    def _show_context_menu(self, e: tk.Event):
        """Show a no-activate popup so the fullscreen game never minimizes.
        We build a Toplevel and show it via ShowWindow(SW_SHOWNOACTIVATE)
        instead of tk_popup(), which always activates its window."""
        self._close_popup()
        mx, my = e.x_root, e.y_root

        p = tk.Toplevel(self.root)
        p.withdraw()
        p.overrideredirect(True)
        p.wm_attributes('-topmost', True)
        p.configure(bg='#3A3A3A')   # 1-px border colour

        f = tkfont.Font(family='Consolas', size=self._fs_notes)

        def add_item(text, cmd=None):
            lbl = tk.Label(p, text=text,
                           bg='#2D2D2D', fg='#FFFFFF',
                           font=f, anchor='w', padx=14, pady=3)
            lbl.pack(fill='x', padx=1, pady=0)
            if cmd:
                def on_click(_, c=cmd):
                    self._close_popup()
                    self.root.after(1, c)
                lbl.bind('<Button-1>', on_click)
                lbl.bind('<Enter>', lambda _, w=lbl: w.configure(bg='#444444'))
                lbl.bind('<Leave>', lambda _, w=lbl: w.configure(bg='#2D2D2D'))

        def add_sep():
            tk.Frame(p, bg='#555555', height=1).pack(fill='x', padx=0, pady=2)

        add_item('Copy notes  [V]', self._do_copy_notes)
        add_sep()
        files        = self.notes_manager.list_files()
        active_count = sum(1 for _, a in files if a)
        all_active   = (active_count == len(files))
        for fname, is_active in files:
            mark = '\u25cf' if (is_active and not all_active) else '\u25cb'
            add_item(f'{mark}  {fname}', lambda fn=fname: self._select_notes_file(fn))
        add_sep()
        add_item('Reload all notes', self._do_reload_notes)
        add_sep()
        add_item('Exit', self._do_exit)

        # Compute natural size, position near cursor but keep on screen
        p.update_idletasks()
        pw = p.winfo_reqwidth()
        ph = p.winfo_reqheight()
        sw = p.winfo_screenwidth()
        sh = p.winfo_screenheight()
        x  = max(0, min(mx, sw - pw))
        y  = max(0, min(my, sh - ph))
        p.geometry(f'{pw}x{ph}+{x}+{y}')
        p.update_idletasks()

        # Apply WS_EX_NOACTIVATE, then show WITHOUT activating
        try:
            GWL_EXSTYLE       = -20
            WS_EX_NOACTIVATE  = 0x08000000
            SW_SHOWNOACTIVATE = 4
            hwnd = ctypes.windll.user32.GetParent(p.winfo_id())
            if not hwnd:
                hwnd = p.winfo_id()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
                                                style | WS_EX_NOACTIVATE)
            ctypes.windll.user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
        except Exception:
            p.deiconify()   # safe fallback

        self._popup = p
        # Close popup on any left-click on the overlay itself
        self.root.bind('<Button-1>', lambda _: self._close_popup(), add='+')

    def _close_popup(self):
        if self._popup is not None:
            try:
                self._popup.destroy()
            except Exception:
                pass
            self._popup = None

    def _select_notes_file(self, fname: str):
        self.notes_manager.select_file(fname)
        if self._save_config_fn:
            self._save_config_fn()   # persist immediately
        if self._current_map:
            notes = self.notes_manager.find_notes(self._current_map)
            self.set_map(self._current_map, notes)

    def _reset_notes_file(self):
        self._config['active_notes_file'] = ''
        self.notes_manager.reload()
        if self._current_map:
            notes = self.notes_manager.find_notes(self._current_map)
            self.set_map(self._current_map, notes)

    def _do_copy_notes(self):
        import pyperclip
        if self._current_notes:
            try:
                pyperclip.copy(self._current_notes)
            except Exception:
                pass

    def _do_reload_notes(self):
        self.notes_manager.reload()
        if self._current_map:
            notes = self.notes_manager.find_notes(self._current_map)
            self.set_map(self._current_map, notes)

    def _do_exit(self):
        if self.poe_monitor:
            self.poe_monitor.stop()
        self.root.destroy()

    # ── Public interface (called by PoeMonitor / HotkeyManager) ──────────────

    def show(self):
        if not self._is_visible:
            self.root.deiconify()
            self._is_visible = True
            # Apply WS_EX_NOACTIVATE after first deiconify so the HWND is live.
            # This prevents the overlay from stealing focus from a fullscreen
            # game when the user clicks or drags it.
            self.root.after(10, self._apply_noactivate)

    def _apply_noactivate(self):
        try:
            GWL_EXSTYLE      = -20
            WS_EX_NOACTIVATE = 0x08000000
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if not hwnd:
                hwnd = self.root.winfo_id()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
                                                style | WS_EX_NOACTIVATE)
        except Exception:
            pass

    def hide(self):
        if self._is_visible:
            self.root.withdraw()
            self._is_visible = False

    def toggle_content(self):
        self._show_content = not self._show_content
        self._refresh_layout()

    def set_map(self, map_name: str, notes: str):
        self._current_map   = map_name
        self._current_notes = notes
        self._show_content  = True     # reveal notes on new map
        self._refresh_notes_widget()
        self._refresh_layout()

    def get_notes_text(self) -> str:
        return self._current_notes

    # ── Internal refresh ──────────────────────────────────────────────────────

    def _refresh_notes_widget(self):
        self._txt_notes.configure(state='normal')
        self._txt_notes.delete('1.0', 'end')
        if self._current_notes:
            self._txt_notes.insert('1.0', self._current_notes)
        self._txt_notes.configure(state='disabled')

    def _refresh_layout(self):
        has_notes = bool(self._current_notes and self._show_content)
        x = self.root.winfo_x()
        y = self.root.winfo_y()

        if has_notes:
            self._divider.pack(fill='x')
            self._frame_notes.pack(fill='both', expand=True)

            # Quick first-pass: use hard-newline count so the window is given a
            # real height before count('displaylines') runs.  This avoids the
            # winfo_width()==0 problem that causes every character to wrap to
            # its own line and produce an enormous initial window.
            lh    = self._fs_notes + 6
            max_h = int(self.root.winfo_screenheight() * 0.45)
            n_hard = max(1, self._current_notes.count('\n') + 1)
            notes_h_est = min(n_hard * lh + 12, max_h)
            self.root.geometry(f'{self._win_w}x{self._timer_row_h + 1 + notes_h_est}+{x}+{y}')

            # After 80 ms the layout has settled; re-measure with the accurate
            # display-line count (accounts for word-wrapping of long lines).
            self.root.after(80, self._remeasure_notes)
        else:
            self._frame_notes.pack_forget()
            self._divider.pack_forget()
            self._scrollbar.pack_forget()
            self.root.geometry(f'{self._win_w}x{self._timer_row_h}+{x}+{y}')

    def _remeasure_notes(self):
        """Accurate re-measurement after the window is fully laid out."""
        if not self._current_notes or not self._show_content:
            return
        # If the widget hasn't been rendered to its real pixel width yet,
        # wait another 50 ms and retry rather than measuring against width=0/1
        # (which would count every character as its own display line).
        if self._txt_notes.winfo_width() <= 1:
            self.root.after(50, self._remeasure_notes)
            return
        lh    = self._fs_notes + 6
        max_h = int(self.root.winfo_screenheight() * 0.45)
        try:
            result  = self._txt_notes.count('1.0', 'end', 'displaylines')
            n_lines = max(1, int(result[0] or 1))
        except Exception:
            n_lines = max(1, self._current_notes.count('\n') + 1)

        notes_h = min(n_lines * lh + 12, max_h)
        total_h = self._timer_row_h + 1 + notes_h
        x = self.root.winfo_x()
        y = self.root.winfo_y()

        if n_lines * lh + 12 > max_h:
            self._scrollbar.pack(side='right', fill='y')
        else:
            self._scrollbar.pack_forget()

        self.root.geometry(f'{self._win_w}x{total_h}+{x}+{y}')

        self._lbl_map.configure(
            text=(self._current_map[:30] if self._current_map else '')
        )

    def _tick(self):
        """Refresh timer label every 100 ms on the main thread."""
        try:
            elapsed = self._stopwatch.get_elapsed()
            paused  = self._stopwatch.is_paused
            started = self._stopwatch.has_started

            h = int(elapsed // 3600)
            m = int((elapsed % 3600) // 60)
            s = int(elapsed % 60)
            text = f'{h:02d}:{m:02d}:{s:02d}'

            if not started:
                color = TIMER_IDLE_FG
            elif paused:
                text  += '  ⏸'
                color  = TIMER_PAUSE_FG
            else:
                color  = TIMER_RUN_FG

            self._lbl_timer.configure(text=text, fg=color)
            self.root.after(100, self._tick)
        except tk.TclError:
            pass   # window was destroyed

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()
