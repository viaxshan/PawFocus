import tkinter as tk
import tkinter.font as tkfont
import os
import sys

PALETTE = {
    "bg_dark":   "#2d2b38",
    "bg_light":  "#ffe5ec",
    "blue":      "#b5e2fa",
    "yellow":    "#fdf0d5",
    "text_dark": "#3d3a4e",
    "text_white":"#fefefe",
    "pink":      "#ffb7c5",
    "dark_pink": "#8d4e7c",
    "grey":      "#9a96a8"
}

# Look for assets next to this file, so the app works no matter which folder you launch it from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def asset_path(filename):
    return os.path.join(BASE_DIR, filename)

FONT_NAME = "Pixelify Sans"
FONT_FILE = "PixelifySans-VariableFont_wght.ttf"
FONT_PATH = asset_path(FONT_FILE)

if sys.platform.startswith("win"):
    if os.path.exists(FONT_PATH):
        import ctypes
        FR_PRIVATE = 0x10
        ctypes.windll.gdi32.AddFontResourceExW(FONT_PATH, FR_PRIVATE, 0)
elif sys.platform.startswith("darwin"):
    if not os.path.exists(os.path.expanduser(f"~/Library/Fonts/{FONT_FILE}")):
        print(f"Tip: For best results on Mac, double-click and install '{FONT_FILE}' to your font book!")

# Dashboard sizing: the layout is designed at BASE size and scales from there.
BASE_WIDTH, BASE_HEIGHT = 380, 640
MIN_WIDTH, MIN_HEIGHT = 320, 540   # cut-off: the window can't be dragged smaller than this
MAX_SCALE = 2.0                    # stop growing past 200% so things don't get silly on huge monitors


def _shade(hex_color, amount=0.12):
    """Mixes a colour slightly toward the dark text colour (used for the pressed look)."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    dr, dg, db = (int(PALETTE["text_dark"][i:i + 2], 16) for i in (1, 3, 5))
    mix = lambda c, d: round(c + (d - c) * amount)
    return f"#{mix(r, dr):02x}{mix(g, dg):02x}{mix(b, db):02x}"


class FlatButton(tk.Frame):
    """A button drawn from a Frame (the border) and a Label (the face).

    macOS ignores the colours, borders and relief of a normal tk.Button and always draws
    its own rounded system button. Frames and Labels keep their colours on every OS,
    so this looks the same on Mac and Windows. It accepts the same config() options the
    controller uses: text, command and state.
    """

    def __init__(self, parent, text="", command=None, font=None, bg=PALETTE["blue"],
                 fg=PALETTE["text_dark"], border=2, width=None, state="normal", padx=6, pady=3):
        super().__init__(parent, bg=PALETTE["text_dark"], padx=border, pady=border)
        self._face_bg = bg
        self._face_fg = fg
        self._command = command
        self._state = state

        self.label = tk.Label(self, text=text, font=font, bg=bg, fg=fg, padx=padx, pady=pady)
        if width:
            self.label.config(width=width)
        self.label.pack(fill="both", expand=True)

        for widget in (self, self.label):
            widget.bind("<ButtonPress-1>", self._on_press)
            widget.bind("<ButtonRelease-1>", self._on_release)
        self._refresh_look()

    def _refresh_look(self, pressed=False):
        enabled = self._state != "disabled"
        self.label.config(
            bg=_shade(self._face_bg) if pressed else self._face_bg,
            fg=self._face_fg if enabled else PALETTE["grey"],
            cursor="hand2" if enabled else ""
        )

    def _on_press(self, event):
        if self._state != "disabled":
            self._refresh_look(pressed=True)

    def _on_release(self, event):
        if self._state == "disabled":
            return
        self._refresh_look()
        # Only fire if the mouse is still over the button (lets you "cancel" a click by dragging off)
        if self.winfo_containing(event.x_root, event.y_root) in (self, self.label) and self._command:
            self._command()

    def configure(self, cnf=None, **kw):
        if cnf:
            kw.update(cnf)
        if "command" in kw:
            self._command = kw.pop("command")
        if "state" in kw:
            self._state = kw.pop("state")
        if "bg" in kw:
            self._face_bg = kw.pop("bg")
        if "fg" in kw:
            self._face_fg = kw.pop("fg")
        label_opts = {k: kw.pop(k) for k in ("text", "font", "width") if k in kw}
        if label_opts:
            self.label.config(**label_opts)
        if kw:
            super().configure(**kw)
        self._refresh_look()

    config = configure


class FlatDropdown(FlatButton):
    """Replacement for tk.OptionMenu, which macOS also draws as a native grey/blue control."""

    def __init__(self, parent, variable, options, font=None, menu_font=None, **kw):
        super().__init__(parent, font=font, command=self._open_menu, **kw)
        self.variable = variable
        self.menu = tk.Menu(
            self, tearoff=0, font=menu_font,
            bg=PALETTE["yellow"], fg=PALETTE["text_dark"],
            activebackground=PALETTE["pink"], activeforeground=PALETTE["text_dark"]
        )
        for option in options:
            self.menu.add_command(label=option, command=lambda o=option: self.variable.set(o))
        self.variable.trace_add("write", lambda *args: self._show_value())
        self._show_value()

    def _show_value(self):
        self.label.config(text=f"{self.variable.get()}  ▾")

    def _open_menu(self):
        self.menu.tk_popup(self.winfo_rootx(), self.winfo_rooty() + self.winfo_height())


def make_bordered_entry(parent, font, width=None, justify="left"):
    """An Entry with a thin dark outline that looks the same on Mac and Windows.

    Returns (outline_frame, entry): place the frame with pack/grid, use the entry for text.
    Colours are set explicitly so macOS dark mode doesn't turn the boxes black.
    """
    outline = tk.Frame(parent, bg=PALETTE["text_dark"], padx=1, pady=1)
    entry = tk.Entry(
        outline, font=font, justify=justify, relief="flat", bd=2, highlightthickness=0,
        bg="#ffffff", fg=PALETTE["text_dark"], insertbackground=PALETTE["text_dark"],
        disabledbackground="#ececec", disabledforeground=PALETTE["grey"],
        selectbackground=PALETTE["pink"], selectforeground=PALETTE["text_dark"]
    )
    if width:
        entry.config(width=width)
    entry.pack(fill="both", expand=True)
    return outline, entry


class DashboardWindow(tk.Tk):
    def __init__(self, methods_list):
        super().__init__()
        self.title("PawFocus Dashboard")
        self.geometry(f"{BASE_WIDTH}x{BASE_HEIGHT}")
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.config(bg=PALETTE["bg_light"])

        # Named fonts: changing a font's size later instantly resizes every widget that uses it
        self.fonts = {
            "title":    tkfont.Font(self, family=FONT_NAME, size=20, weight="bold"),
            "dropdown": tkfont.Font(self, family=FONT_NAME, size=12),
            "menu":     tkfont.Font(self, family=FONT_NAME, size=11),
            "section":  tkfont.Font(self, family=FONT_NAME, size=10, weight="bold"),
            "body":     tkfont.Font(self, family=FONT_NAME, size=10),
            "apply":    tkfont.Font(self, family=FONT_NAME, size=9, weight="bold"),
            "status":   tkfont.Font(self, family=FONT_NAME, size=12, slant="italic"),
            "timer":    tkfont.Font(self, family=FONT_NAME, size=36, weight="bold"),
            "button":   tkfont.Font(self, family=FONT_NAME, size=11, weight="bold"),
        }
        self._base_font_sizes = {name: int(font.cget("size")) for name, font in self.fonts.items()}

        # Paddings that should grow/shrink with the window: (setter function, base values)
        self._scaled_spacing = []
        self._scale = 1.0
        self._resize_job = None

        self.frame = tk.Frame(self, bg=PALETTE["bg_light"])
        self._scaled_config(self.frame, padx=20, pady=15)
        self.frame.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            self.frame, text="PawFocus Menu", font=self.fonts["title"],
            fg=PALETTE["text_dark"], bg=PALETTE["bg_light"]
        )
        self._pack(self.title_label, pady=5)

        self.selected_method = tk.StringVar(value=methods_list[0])
        self.dropdown = FlatDropdown(
            self.frame, self.selected_method, methods_list,
            font=self.fonts["dropdown"], menu_font=self.fonts["menu"], bg=PALETTE["blue"]
        )
        self._pack(self.dropdown, pady=5, fill="x")

        self.input_frame = tk.LabelFrame(
            self.frame, text="⚙️ Session Settings",
            font=self.fonts["section"], fg=PALETTE["text_dark"], bg=PALETTE["bg_light"],
            bd=2, relief="solid"
        )
        self._scaled_config(self.input_frame, padx=10, pady=10)
        self._pack(self.input_frame, fill="x", pady=5)

        study_lbl = tk.Label(self.input_frame, text="Study Mins:", font=self.fonts["body"], bg=PALETTE["bg_light"], fg=PALETTE["text_dark"])
        self._grid(study_lbl, row=0, column=0, sticky="e", pady=2)
        study_box, self.study_entry = make_bordered_entry(self.input_frame, self.fonts["body"], width=6, justify="center")
        self._grid(study_box, row=0, column=1, padx=5, pady=2)

        break_lbl = tk.Label(self.input_frame, text="Break Mins:", font=self.fonts["body"], bg=PALETTE["bg_light"], fg=PALETTE["text_dark"])
        self._grid(break_lbl, row=0, column=2, sticky="e", pady=2)
        break_box, self.break_entry = make_bordered_entry(self.input_frame, self.fonts["body"], width=6, justify="center")
        self._grid(break_box, row=0, column=3, padx=5, pady=2)

        rounds_lbl = tk.Label(self.input_frame, text="Rounds:", font=self.fonts["body"], bg=PALETTE["bg_light"], fg=PALETTE["text_dark"])
        self._grid(rounds_lbl, row=1, column=0, sticky="e", pady=5)
        rounds_box, self.rounds_entry = make_bordered_entry(self.input_frame, self.fonts["body"], width=6, justify="center")
        self._grid(rounds_box, row=1, column=1, padx=5, pady=5)

        self.save_custom_btn = FlatButton(
            self.input_frame, text="💾 Apply Settings", font=self.fonts["apply"],
            bg=PALETTE["blue"], border=1
        )
        self._grid(self.save_custom_btn, row=1, column=2, columnspan=2, sticky="we", padx=5, pady=5)

        # Let the settings columns share extra width when the window gets wider
        for col in range(4):
            self.input_frame.grid_columnconfigure(col, weight=1)

        self.size_frame = tk.LabelFrame(
            self.frame, text="📐 Kitty Scale Size Settings",
            font=self.fonts["section"], fg=PALETTE["text_dark"], bg=PALETTE["bg_light"],
            bd=2, relief="solid"
        )
        self._scaled_config(self.size_frame, padx=10, pady=5)
        self._pack(self.size_frame, fill="x", pady=5)

        self.size_slider = tk.Scale(
            self.size_frame, from_=1, to=3, orient="horizontal",
            bg=PALETTE["bg_light"], fg=PALETTE["text_dark"], font=self.fonts["body"],
            highlightthickness=0, bd=0, showvalue=False
        )
        self._scaled_config(self.size_slider, sliderlength=30, width=15)
        self.size_slider.set(2)
        self._pack(self.size_slider, side="left", fill="x", expand=True, padx=5)

        self.size_label = tk.Label(
            self.size_frame, text="Size: 100%", font=self.fonts["section"],
            bg=PALETTE["bg_light"], fg=PALETTE["text_dark"], width=10
        )
        self._pack(self.size_label, side="right", padx=5)

        self.status_label = tk.Label(
            self.frame, text="Status: Ready to read!",
            font=self.fonts["status"], fg=PALETTE["text_dark"], bg=PALETTE["bg_light"]
        )
        self._pack(self.status_label, pady=5)

        # The timer box keeps its natural height; its text still scales with the window
        self.timer_label = tk.Label(
            self.frame, text="00:00", font=self.fonts["timer"],
            fg=PALETTE["text_white"], bg=PALETTE["bg_dark"], bd=3, relief="solid"
        )
        self._pack(self.timer_label, pady=5, fill="x")

        self.toggle_overlay_clock_btn = FlatButton(
            self.frame, text="⏰ Hide Clock on Cat", font=self.fonts["section"],
            bg=PALETTE["yellow"]
        )
        self._pack(self.toggle_overlay_clock_btn, fill="x", pady=5)

        btn_box = tk.Frame(self.frame, bg=PALETTE["bg_light"])
        self._pack(btn_box, side="bottom", fill="x", pady=5)

        self.start_btn = FlatButton(
            btn_box, text="▶ START", font=self.fonts["button"],
            bg=PALETTE["blue"], width=12, pady=5
        )
        self._pack(self.start_btn, side="left", expand=True, padx=5)

        self.cancel_btn = FlatButton(
            btn_box, text="❌ STOP", font=self.fonts["button"],
            bg=PALETTE["yellow"], width=12, pady=5, state="disabled"
        )
        self._pack(self.cancel_btn, side="left", expand=True, padx=5)

        self.bind("<Configure>", self._on_window_configure)

    # ---------- layout helpers that remember padding so it can be rescaled ----------

    def _pack(self, widget, **options):
        widget.pack(**options)
        self._remember_spacing(widget.pack_configure, options, ("padx", "pady"))

    def _grid(self, widget, **options):
        widget.grid(**options)
        self._remember_spacing(widget.grid_configure, options, ("padx", "pady"))

    def _scaled_config(self, widget, **options):
        widget.config(**options)
        self._remember_spacing(widget.config, options, tuple(options))

    def _remember_spacing(self, setter, options, keys):
        spacing = {k: options[k] for k in keys if k in options}
        if spacing:
            self._scaled_spacing.append((setter, spacing))

    # ---------- responsive scaling ----------

    def _on_window_configure(self, event):
        # This binding also fires for every child widget; only react to the window itself
        if event.widget is not self:
            return
        # Wait until the user pauses dragging, so we don't rebuild fonts 60 times a second
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(40, self._apply_window_scale)

    def _apply_window_scale(self):
        self._resize_job = None
        width, height = self.winfo_width(), self.winfo_height()

        # Use whichever direction is tighter, so everything still fits
        scale = min(width / BASE_WIDTH, height / BASE_HEIGHT, MAX_SCALE)
        scale = max(scale, min(MIN_WIDTH / BASE_WIDTH, MIN_HEIGHT / BASE_HEIGHT))

        if abs(scale - self._scale) < 0.02:
            return
        self._scale = scale

        for name, font in self.fonts.items():
            font.configure(size=max(7, round(self._base_font_sizes[name] * scale)))

        for setter, spacing in self._scaled_spacing:
            setter(**{k: max(1, round(v * scale)) for k, v in spacing.items()})


class KittyOverlay(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.base_art_width = 120
        self.base_art_height = 85
        self.art_width = self.base_art_width
        self.art_height = self.base_art_height
        self.clock_height = 30

        self.geometry(f"{self.art_width}x{self.art_height + self.clock_height}+100+100")
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Make everything behind the cat see-through
        if sys.platform.startswith("win"):
            # Windows: any pixel of exactly this colour becomes invisible. It's a shade
            # next to the clock's pink shadow, so the soft edges of the clock text blend
            # into pink instead of leaving a blue-ish halo. (Not used anywhere in the cat art.)
            self.chroma_color = "#8c4d7b"
            self.canvas_bg = self.chroma_color
            self.config(bg=self.chroma_color)
            self.attributes("-transparentcolor", self.chroma_color)
        elif sys.platform.startswith("darwin"):
            # macOS: Tk's special transparent colour + a transparent window
            self.canvas_bg = "systemTransparent"
            self.config(bg="systemTransparent")
            self.attributes("-transparent", True)
        else:
            # Linux can't do per-pixel transparency in Tk, so keep the coloured box there
            self.canvas_bg = PALETTE["blue"]
            self.config(bg=PALETTE["blue"])
            self.attributes("-alpha", 0.95)

        self.canvas = tk.Canvas(self, width=self.art_width, height=self.art_height + self.clock_height, bg=self.canvas_bg, highlightthickness=0, cursor="hand2")
        self.canvas.pack(fill="both", expand=True)

        self.base_images = {
            state: tk.PhotoImage(file=asset_path(f"cat_{state}.png")) if os.path.exists(asset_path(f"cat_{state}.png")) else None
            for state in ("sleeping", "reading", "playing")
        }

        self.current_images = dict(self.base_images)
        self.active_state = "sleeping"
        self.current_image_obj = None
        self.current_time_str = "00:00"
        self.scale_level = 2
        self.show_clock = True

        # On a transparent macOS window, Tk draws PNG images as invisible, but shapes and
        # text show up fine. So on Mac the cat is drawn pixel-by-pixel as tiny squares.
        self.draw_as_pixels = sys.platform.startswith("darwin")
        self.pixel_grids = {}
        if self.draw_as_pixels:
            for state, img in self.base_images.items():
                if img:
                    self.pixel_grids[state] = self._read_pixels(img)

        self.redraw_overlay()

    @staticmethod
    def _read_pixels(img):
        """Turns a PhotoImage into rows of colour strings (None = transparent pixel)."""
        grid = []
        for y in range(img.height()):
            row = []
            for x in range(img.width()):
                if img.transparency_get(x, y):
                    row.append(None)
                else:
                    r, g, b = img.get(x, y)
                    row.append(f"#{r:02x}{g:02x}{b:02x}")
            grid.append(row)
        return grid

    def _draw_pixel_cat(self, grid):
        """Draws the pixel grid at the current size. Neighbouring same-colour pixels in a row
        are merged into one rectangle, so this stays fast."""
        scale = {1: 0.5, 2: 1.0, 3: 1.5}[self.scale_level]
        src_h, src_w = len(grid), len(grid[0])
        out_w, out_h = max(1, round(src_w * scale)), max(1, round(src_h * scale))
        left = self.art_width // 2 - out_w // 2
        top = self.art_height // 2 - out_h // 2

        for ty in range(out_h):
            src_row = grid[min(src_h - 1, int(ty / scale))]
            run_color, run_start = None, 0
            for tx in range(out_w + 1):
                color = src_row[min(src_w - 1, int(tx / scale))] if tx < out_w else None
                if color != run_color:
                    if run_color is not None:
                        self.canvas.create_rectangle(
                            left + run_start, top + ty, left + tx, top + ty + 1,
                            fill=run_color, outline="", tags="cat"
                        )
                    run_color, run_start = color, tx

    def get_bounds(self, x=None, y=None):
        """Returns (x, y, width, height) of the cat on screen. Pass x/y if you just moved it."""
        if x is None or y is None:
            x, y = self.winfo_x(), self.winfo_y()
        return x, y, self.art_width, self.art_height + self.clock_height

    def apply_scale_factor(self, scale_level):
        self.scale_level = scale_level
        for state, img in self.base_images.items():
            if img:
                if scale_level == 1:
                    self.current_images[state] = img.subsample(2)
                elif scale_level == 3:
                    self.current_images[state] = img.zoom(3).subsample(2)
                else:
                    self.current_images[state] = img

        scale_multipliers = {1: 0.5, 2: 1.0, 3: 1.5}
        clock_heights = {1: 22, 2: 30, 3: 42}

        mult = scale_multipliers[scale_level]
        self.art_width = int(self.base_art_width * mult)
        self.art_height = int(self.base_art_height * mult)
        self.clock_height = clock_heights[scale_level] if self.show_clock else 0

        self.geometry(f"{self.art_width}x{self.art_height + self.clock_height}")
        self.canvas.config(width=self.art_width, height=self.art_height + self.clock_height)
        self.redraw_overlay()

    def update_overlay_clock_text(self, time_str):
        # Only the clock changes every second, so leave the cat alone
        self.current_time_str = time_str
        self.canvas.delete("clock")
        self._draw_clock()

    def set_clock_visibility(self, visible):
        self.show_clock = visible
        clock_heights = {1: 22, 2: 30, 3: 42}
        self.clock_height = clock_heights[self.scale_level] if self.show_clock else 0
        self.geometry(f"{self.art_width}x{self.art_height + self.clock_height}")
        self.canvas.config(width=self.art_width, height=self.art_height + self.clock_height)
        self.redraw_overlay()

    def change_kitty_state(self, state_name):
        self.active_state = state_name
        self.redraw_overlay()

    def redraw_overlay(self):
        self.canvas.delete("all")

        img = self.current_images.get(self.active_state)
        grid = self.pixel_grids.get(self.active_state)
        if grid:
            self._draw_pixel_cat(grid)
        elif img:
            self.current_image_obj = self.canvas.create_image(self.art_width // 2, self.art_height // 2, image=img)
        else:
            emoji = {"sleeping": "💤", "reading": "📚", "playing": "🧶"}
            emoji_char = emoji.get(self.active_state, "🐱")
            self.canvas.create_rectangle(5, 5, self.art_width-5, self.art_height-5, fill=PALETTE["yellow"], outline=PALETTE["text_dark"], width=2)
            self.canvas.create_text(self.art_width // 2, self.art_height // 2, text=f"{emoji_char}\n[{self.active_state.upper()}]", font=(FONT_NAME, int(11 * (self.art_width/120))), fill=PALETTE["text_dark"], justify="center")

        self._draw_clock()

    def _draw_clock(self):
        if not self.show_clock:
            return
        font_sizes = {1: 12, 2: 18, 3: 26}
        f_size = font_sizes[self.scale_level]

        clock_y = self.art_height + (self.clock_height // 2) - 6

        for offset in [1, 2]:
            self.canvas.create_text(
                (self.art_width // 2) + offset, clock_y + offset,
                text=self.current_time_str, font=(FONT_NAME, f_size, "bold"),
                fill=PALETTE["dark_pink"], justify="center", tags="clock"
            )

        self.canvas.create_text(
            self.art_width // 2, clock_y,
            text=self.current_time_str, font=(FONT_NAME, f_size, "bold"),
            fill=PALETTE["text_white"], justify="center", tags="clock"
        )


class TodoDropdown(tk.Toplevel):
    """Borderless to-do panel that drops down under the cat when you click it."""

    WIDTH = 290
    MAX_LIST_HEIGHT = 260  # list scrolls after this many pixels
    GAP = 6                # space between the cat and the panel

    # Font sizes for the panel, all in one place so they're easy to tweak
    TITLE_SIZE = 15
    TASK_SIZE = 13
    SMALL_SIZE = 11

    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self._make_borderless()
        self.attributes("-topmost", True)
        self.config(bg=PALETTE["text_dark"])  # shows through as a 2px outline
        self.is_open = False
        self._check_vars = []

        # Hooks the controller fills in
        self.on_add = None
        self.on_toggle = None
        self.on_delete = None
        self.on_clear_done = None

        self.task_font = tkfont.Font(self, family=FONT_NAME, size=self.TASK_SIZE)
        self.done_font = tkfont.Font(self, family=FONT_NAME, size=self.TASK_SIZE, overstrike=True)
        self.small_font = tkfont.Font(self, family=FONT_NAME, size=self.SMALL_SIZE)
        self.small_bold_font = tkfont.Font(self, family=FONT_NAME, size=self.SMALL_SIZE, weight="bold")

        body = tk.Frame(self, bg=PALETTE["yellow"], padx=8, pady=8)
        body.pack(fill="both", expand=True, padx=2, pady=2)

        header = tk.Frame(body, bg=PALETTE["yellow"])
        header.pack(fill="x")
        tk.Label(
            header, text="📝 To-Do List", font=(FONT_NAME, self.TITLE_SIZE, "bold"),
            fg=PALETTE["text_dark"], bg=PALETTE["yellow"]
        ).pack(side="left")
        self.count_label = tk.Label(
            header, text="", font=self.small_font,
            fg=PALETTE["dark_pink"], bg=PALETTE["yellow"]
        )
        self.count_label.pack(side="right")

        entry_row = tk.Frame(body, bg=PALETTE["yellow"])
        entry_row.pack(fill="x", pady=(6, 6))
        entry_box, self.entry = make_bordered_entry(entry_row, self.task_font)
        entry_box.pack(side="left", fill="both", expand=True)
        self.entry.bind("<Return>", lambda e: self._submit())
        # Clicking the box grabs the keyboard, even when the dashboard is hidden/minimized
        self.entry.bind("<Button-1>", lambda e: self.focus_entry(), add="+")
        self.add_btn = FlatButton(
            entry_row, text="+ Add", font=self.small_bold_font,
            bg=PALETTE["blue"], border=1, command=self._submit
        )
        self.add_btn.pack(side="left", fill="y", padx=(4, 0))

        list_wrap = tk.Frame(body, bg=PALETTE["yellow"])
        list_wrap.pack(fill="both", expand=True)
        self.list_canvas = tk.Canvas(
            list_wrap, bg=PALETTE["yellow"], highlightthickness=0,
            width=self.WIDTH - 20, height=40
        )
        self.scrollbar = tk.Scrollbar(list_wrap, orient="vertical", command=self.list_canvas.yview)
        self.list_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.list_canvas.pack(side="left", fill="both", expand=True)

        self.rows_frame = tk.Frame(self.list_canvas, bg=PALETTE["yellow"])
        self._rows_window = self.list_canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.list_canvas.bind(
            "<Configure>", lambda e: self.list_canvas.itemconfig(self._rows_window, width=e.width)
        )

        self.clear_btn = tk.Label(
            body, text="🧹 clear finished", font=self.small_font,
            fg=PALETTE["dark_pink"], bg=PALETTE["yellow"], cursor="hand2"
        )
        self.clear_btn.pack(anchor="e", pady=(6, 0))
        self.clear_btn.bind("<Button-1>", lambda e: self.on_clear_done and self.on_clear_done())

        # A binding on the Toplevel also catches events from every widget inside it
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Button-4>", lambda e: self.list_canvas.yview_scroll(-1, "units"))
        self.bind("<Button-5>", lambda e: self.list_canvas.yview_scroll(1, "units"))
        self.bind("<Escape>", lambda e: self.close())

    def _make_borderless(self):
        """Removes the title bar while still letting the panel receive typing.

        On macOS, Tk marks overrideredirect windows as "never take keyboard focus",
        so typing only worked while the dashboard window was active. A "plain" Mac
        window is just as borderless but is allowed to take the keyboard itself.
        """
        if sys.platform.startswith("darwin"):
            try:
                self.tk.call("::tk::unsupported::MacWindowStyle", "style", str(self), "plain", "none")
                return
            except tk.TclError:
                pass  # very old Tk: fall back to the regular borderless window
        self.overrideredirect(True)

    def focus_entry(self):
        """Make this panel the active window and put the cursor in the text box."""
        try:
            self.lift()
            self.focus_force()
            self.entry.focus_force()
        except tk.TclError:
            pass

    def _submit(self):
        if self.on_add and self.on_add(self.entry.get()):
            self.entry.delete(0, "end")

    def _on_mousewheel(self, event):
        if self.scrollbar.winfo_ismapped():
            # Windows reports multiples of 120, macOS reports small numbers
            step = -int(event.delta / 120) if abs(event.delta) >= 120 else -event.delta
            self.list_canvas.yview_scroll(step, "units")

    def render(self, items, remaining):
        for child in self.rows_frame.winfo_children():
            child.destroy()
        self._check_vars = []

        if not items:
            tk.Label(
                self.rows_frame, text="Nothing yet, add a task! =^.^=",
                font=self.small_font, fg=PALETTE["grey"], bg=PALETTE["yellow"]
            ).pack(pady=8)

        for index, item in enumerate(items):
            row = tk.Frame(self.rows_frame, bg=PALETTE["yellow"])
            row.pack(fill="x", pady=1)

            done_var = tk.BooleanVar(value=item["done"])
            check = tk.Checkbutton(
                row, variable=done_var, bg=PALETTE["yellow"], activebackground=PALETTE["yellow"],
                highlightthickness=0, bd=0, cursor="hand2",
                command=lambda i=index: self.on_toggle and self.on_toggle(i)
            )
            self._check_vars.append(done_var)  # keep a reference so it isn't garbage-collected
            check.pack(side="left", anchor="n")

            text = tk.Label(
                row, text=item["text"], anchor="w", justify="left",
                wraplength=self.WIDTH - 90,
                font=self.done_font if item["done"] else self.task_font,
                fg=PALETTE["grey"] if item["done"] else PALETTE["text_dark"],
                bg=PALETTE["yellow"]
            )
            text.pack(side="left", fill="x", expand=True, padx=(2, 4))

            delete = tk.Label(
                row, text="✕", font=(FONT_NAME, self.TASK_SIZE, "bold"),
                fg=PALETTE["dark_pink"], bg=PALETTE["yellow"], cursor="hand2"
            )
            delete.pack(side="right", anchor="n")
            delete.bind("<Button-1>", lambda e, i=index: self.on_delete and self.on_delete(i))

        self.count_label.config(text=f"{remaining} left" if items else "")
        done_count = len(items) - remaining
        if done_count:
            self.clear_btn.pack(anchor="e", pady=(6, 0))
        else:
            self.clear_btn.pack_forget()

        # Grow the list to fit its tasks, then switch to scrolling
        self.rows_frame.update_idletasks()
        content_height = self.rows_frame.winfo_reqheight()
        self.list_canvas.config(
            height=min(content_height, self.MAX_LIST_HEIGHT),
            scrollregion=(0, 0, 0, content_height)
        )
        if content_height > self.MAX_LIST_HEIGHT:
            self.scrollbar.pack(side="right", fill="y")
        else:
            self.scrollbar.pack_forget()
            self.list_canvas.yview_moveto(0)

    def place_near(self, cat_x, cat_y, cat_w, cat_h):
        """Centre the panel under the cat; flip above it if it would fall off the screen."""
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()

        x = cat_x + cat_w // 2 - w // 2
        y = cat_y + cat_h + self.GAP
        if y + h > screen_h:
            y = cat_y - h - self.GAP

        x = max(0, min(x, screen_w - w))
        y = max(0, y)
        self.geometry(f"+{x}+{y}")

    def open(self):
        self.deiconify()
        self.attributes("-topmost", True)
        self.lift()
        self.is_open = True
        self.after(50, self.focus_entry)

    def close(self):
        self.withdraw()
        self.is_open = False