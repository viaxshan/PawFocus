import tkinter as tk
import os
import sys

PALETTE = {
    "bg_dark":   "#2d2b38",  # High-contrast background framing
    "bg_light":  "#ffe5ec",  # Pastel Pink primary window background
    "blue":      "#b5e2fa",  # Pastel Blue accents
    "yellow":    "#fdf0d5",  # Pastel Yellow highlight banners
    "text_dark": "#3d3a4e",  # Soft dark charcoal/purple for text readability
    "text_white":"#fefefe"   
}

FONT_NAME = "Pixelify Sans"

FONT_PATH = "PixelifySans-VariableFont_wght.ttf"

if sys.platform.startswith("win"):
    # Windows native font loading technique
    if os.path.exists(FONT_PATH):
        import ctypes
        FR_PRIVATE = 0x10
        ctypes.windll.gdi32.AddFontResourceExW(FONT_PATH, FR_PRIVATE, 0)
elif sys.platform.startswith("darwin"):
    # macOS system notification check
    if not os.path.exists(os.path.expanduser(f"~/Library/Fonts/{FONT_PATH}")):
        print(f"Tip: For best results on Mac, double-click and install '{FONT_PATH}' to your font book!")

class DashboardWindow(tk.Tk):
    def __init__(self, methods_list):
        super().__init__()
        self.title("BookCat Dashboard")
        self.geometry("380x480")
        self.config(bg=PALETTE["bg_light"])
        
        self.frame = tk.Frame(self, bg=PALETTE["bg_light"], padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)
        
        self.title_label = tk.Label(
            self.frame, 
            text="BookCat Menu", 
            font=(FONT_NAME, 20, "bold"), 
            fg=PALETTE["text_dark"], 
            bg=PALETTE["bg_light"]
        )
        self.title_label.pack(pady=10)
        
        self.selected_method = tk.StringVar(value=methods_list[0])
        self.dropdown = tk.OptionMenu(self.frame, self.selected_method, *methods_list)
        self.dropdown.config(
            bg=PALETTE["blue"], fg=PALETTE["text_dark"], 
            font=(FONT_NAME, 12), bd=2, relief="solid", highlightthickness=0
        )
        self.dropdown["menu"].config(bg=PALETTE["yellow"], fg=PALETTE["text_dark"], font=(FONT_NAME, 11))
        self.dropdown.pack(pady=15, fill="x")
        
        self.status_label = tk.Label(
            self.frame, 
            text="Status: Ready to read!", 
            font=(FONT_NAME, 12, "italic"), 
            fg=PALETTE["text_dark"], 
            bg=PALETTE["bg_light"]
        )
        self.status_label.pack(pady=5)
        
        self.timer_label = tk.Label(
            self.frame, 
            text="00:00", 
            font=(FONT_NAME, 42, "bold"), 
            fg=PALETTE["text_white"], 
            bg=PALETTE["bg_dark"],
            bd=3, relief="solid", padx=10, pady=5
        )
        self.timer_label.pack(pady=20, fill="x")
        
        btn_box = tk.Frame(self.frame, bg=PALETTE["bg_light"])
        btn_box.pack(side="bottom", fill="x", pady=10)
        
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
        self.art_width = 160
        self.art_height = 160
        
        self.geometry(f"{self.art_width}x{self.art_height}+100+100")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        self.chroma_color = "#abcdef"
        if sys.platform.startswith("win"):
            self.config(bg=self.chroma_color)
            self.attributes("-transparentcolor", self.chroma_color)
            canvas_bg = self.chroma_color
        else:
            self.config(bg=PALETTE["blue"])
            self.attributes("-alpha", 0.95)
            canvas_bg = PALETTE["blue"]
        
        self.canvas = tk.Canvas(self, width=self.art_width, height=self.art_height, bg=canvas_bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.images = {
            "sleeping": tk.PhotoImage(file="cat_sleeping.png") if os.path.exists("cat_sleeping.png") else None,
            "reading": tk.PhotoImage(file="cat_reading.png") if os.path.exists("cat_reading.png") else None,
            "playing": tk.PhotoImage(file="cat_playing.png") if os.path.exists("cat_playing.png") else None
        }
        
        self.current_image_obj = None
        self.change_kitty_state("sleeping")

    def change_kitty_state(self, state_name):
        self.canvas.delete("all")
        
        img = self.images.get(state_name)
        if img:
            self.current_image_obj = self.canvas.create_image(self.art_width // 2, self.art_height // 2, image=img)
        else:
            emoji = {"sleeping": "💤", "reading": "📚", "playing": "🧶"}.get(state_name, "🐱")
            self.canvas.create_rectangle(5, 5, self.art_width-5, self.art_height-5, fill=PALETTE["yellow"], outline=PALETTE["text_dark"], width=2)
            self.canvas.create_text(self.art_width // 2, self.art_height // 2, text=f"{emoji}\n[{state_name.upper()}]", font=(FONT_NAME, 12), fill=PALETTE["text_dark"], justify="center")
