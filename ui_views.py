import tkinter as tk
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
    "dark_pink": "#8d4e7c"
}

FONT_NAME = "Pixelify Sans"
FONT_PATH = "PixelifySans-VariableFont_wght.ttf"

if sys.platform.startswith("win"):
    if os.path.exists(FONT_PATH):
        import ctypes
        FR_PRIVATE = 0x10
        ctypes.windll.gdi32.AddFontResourceExW(FONT_PATH, FR_PRIVATE, 0)
elif sys.platform.startswith("darwin"):
    if not os.path.exists(os.path.expanduser(f"~/Library/Fonts/{FONT_PATH}")):
        print(f"Tip: For best results on Mac, double-click and install '{FONT_PATH}' to your font book!")

class DashboardWindow(tk.Tk):
    def __init__(self, methods_list):
        super().__init__()
        self.title("BookCat Dashboard")
        self.geometry("380x640")
        self.config(bg=PALETTE["bg_light"])
        
        self.frame = tk.Frame(self, bg=PALETTE["bg_light"], padx=20, pady=15)
        self.frame.pack(fill="both", expand=True)
        
        self.title_label = tk.Label(
            self.frame, text="BookCat Menu", font=(FONT_NAME, 20, "bold"), 
            fg=PALETTE["text_dark"], bg=PALETTE["bg_light"]
        )
        self.title_label.pack(pady=5)
        
        self.selected_method = tk.StringVar(value=methods_list[0])
        self.dropdown = tk.OptionMenu(self.frame, self.selected_method, *methods_list)
        self.dropdown.config(
            bg=PALETTE["blue"], fg=PALETTE["text_dark"], 
            font=(FONT_NAME, 12), bd=2, relief="solid", highlightthickness=0
        )
        self.dropdown["menu"].config(bg=PALETTE["yellow"], fg=PALETTE["text_dark"], font=(FONT_NAME, 11))
        self.dropdown.pack(pady=5, fill="x")
        
        self.input_frame = tk.LabelFrame(
            self.frame, text="⚙️ Session Settings", 
            font=(FONT_NAME, 10, "bold"), fg=PALETTE["text_dark"], bg=PALETTE["bg_light"],
            padx=10, pady=10, bd=2, relief="solid"
        )
        self.input_frame.pack(fill="x", pady=5)
        
        tk.Label(self.input_frame, text="Study Mins:", font=(FONT_NAME, 10), bg=PALETTE["bg_light"], fg=PALETTE["text_dark"]).grid(row=0, column=0, sticky="e", pady=2)
        self.study_entry = tk.Entry(self.input_frame, width=6, font=(FONT_NAME, 10), bd=1, relief="solid", justify="center")
        self.study_entry.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(self.input_frame, text="Break Mins:", font=(FONT_NAME, 10), bg=PALETTE["bg_light"], fg=PALETTE["text_dark"]).grid(row=0, column=2, sticky="e", pady=2)
        self.break_entry = tk.Entry(self.input_frame, width=6, font=(FONT_NAME, 10), bd=1, relief="solid", justify="center")
        self.break_entry.grid(row=0, column=3, padx=5, pady=2)
        
        tk.Label(self.input_frame, text="Rounds:", font=(FONT_NAME, 10), bg=PALETTE["bg_light"], fg=PALETTE["text_dark"]).grid(row=1, column=0, sticky="e", pady=5)
        self.rounds_entry = tk.Entry(self.input_frame, width=6, font=(FONT_NAME, 10), bd=1, relief="solid", justify="center")
        self.rounds_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.save_custom_btn = tk.Button(
            self.input_frame, text="💾 Apply Settings", font=(FONT_NAME, 9, "bold"),
            bg=PALETTE["blue"], fg=PALETTE["text_dark"], bd=1, relief="solid"
        )
        self.save_custom_btn.grid(row=1, column=2, columnspan=2, sticky="we", padx=5, pady=5)
        
        self.size_frame = tk.LabelFrame(
            self.frame, text="📐 Kitty Scale Size Settings", 
            font=(FONT_NAME, 10, "bold"), fg=PALETTE["text_dark"], bg=PALETTE["bg_light"],
            padx=10, pady=5, bd=2, relief="solid"
        )
        self.size_frame.pack(fill="x", pady=5)
        
        self.size_slider = tk.Scale(
            self.size_frame, from_=1, to_=3, orient="horizontal",
            bg=PALETTE["bg_light"], fg=PALETTE["text_dark"], font=(FONT_NAME, 10),
            highlightthickness=0, bd=0, showvalue=False
        )
        self.size_slider.set(2)
        self.size_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.size_label = tk.Label(
            self.size_frame, text="Size: 100%", font=(FONT_NAME, 10, "bold"),
            bg=PALETTE["bg_light"], fg=PALETTE["text_dark"], width=10
        )
        self.size_label.pack(side="right", padx=5)
        
        self.status_label = tk.Label(
            self.frame, text="Status: Ready to read!", 
            font=(FONT_NAME, 12, "italic"), fg=PALETTE["text_dark"], bg=PALETTE["bg_light"]
        )
        self.status_label.pack(pady=5)
        
        self.timer_label = tk.Label(
            self.frame, text="00:00", font=(FONT_NAME, 36, "bold"), 
            fg=PALETTE["text_white"], bg=PALETTE["bg_dark"], bd=3, relief="solid"
        )
        self.timer_label.pack(pady=5, fill="x")
        
        self.toggle_overlay_clock_btn = tk.Button(
            self.frame, text="⏰ Hide Clock on Cat", font=(FONT_NAME, 10, "bold"),
            bg=PALETTE["yellow"], fg=PALETTE["text_dark"], bd=2, relief="solid"
        )
        self.toggle_overlay_clock_btn.pack(fill="x", pady=5)
        
        btn_box = tk.Frame(self.frame, bg=PALETTE["bg_light"])
        btn_box.pack(side="bottom", fill="x", pady=5)
        
        self.start_btn = tk.Button(
            btn_box, text="▶ START", font=(FONT_NAME, 11, "bold"), 
            bg=PALETTE["blue"], fg=PALETTE["text_dark"], bd=2, relief="solid", width=12
        )
        self.start_btn.pack(side="left", expand=True, padx=5)
        
        self.cancel_btn = tk.Button(
            btn_box, text="❌ STOP", font=(FONT_NAME, 11, "bold"), 
            bg=PALETTE["yellow"], fg=PALETTE["text_dark"], bd=2, relief="solid", width=12, state="disabled"
        )
        self.cancel_btn.pack(side="left", expand=True, padx=5)

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
        
        self.chroma_color = "#abcdef"
        self.canvas_bg = self.chroma_color if sys.platform.startswith("win") else PALETTE["blue"]
        if sys.platform.startswith("win"):
            self.config(bg=self.chroma_color)
            self.attributes("-transparentcolor", self.chroma_color)
        else:
            self.config(bg=PALETTE["blue"])
            self.attributes("-alpha", 0.95)
        
        self.canvas = tk.Canvas(self, width=self.art_width, height=self.art_height + self.clock_height, bg=self.canvas_bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.base_images = {
            "sleeping": tk.PhotoImage(file="cat_sleeping.png") if os.path.exists("cat_sleeping.png") else None,
            "reading": tk.PhotoImage(file="cat_reading.png") if os.path.exists("cat_reading.png") else None,
            "playing": tk.PhotoImage(file="cat_playing.png") if os.path.exists("cat_playing.png") else None
        }
        
        self.current_images = dict(self.base_images)
        self.active_state = "sleeping"
        self.current_image_obj = None
        self.current_time_str = "00:00"
        self.scale_level = 2
        self.show_clock = True
        
        self.redraw_overlay()

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
        self.current_time_str = time_str
        self.redraw_overlay()

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
        if img:
            self.current_image_obj = self.canvas.create_image(self.art_width // 2, self.art_height // 2, image=img)
        else:
            emoji = {"sleeping": "💤", "reading": "📚", "playing": "🧶"}
            emoji_char = emoji.get(self.active_state, "🐱")
            self.canvas.create_rectangle(5, 5, self.art_width-5, self.art_height-5, fill=PALETTE["yellow"], outline=PALETTE["text_dark"], width=2)
            self.canvas.create_text(self.art_width // 2, self.art_height // 2, text=f"{emoji_char}\n[{self.active_state.upper()}]", font=(FONT_NAME, int(11 * (self.art_width/120))), fill=PALETTE["text_dark"], justify="center")
            
        if self.show_clock:
            font_sizes = {1: 12, 2: 18, 3: 26}
            f_size = font_sizes[self.scale_level]
            
            clock_y = self.art_height + (self.clock_height // 2) - 6
            
            for offset in [1, 2]:
                self.canvas.create_text(
                    (self.art_width // 2) + offset, clock_y + offset, 
                    text=self.current_time_str, font=(FONT_NAME, f_size, "bold"), 
                    fill=PALETTE["dark_pink"], justify="center"
                )

            self.canvas.create_text(
                self.art_width // 2, clock_y, 
                text=self.current_time_str, font=(FONT_NAME, f_size, "bold"), 
                fill=PALETTE["text_white"], justify="center"
            )