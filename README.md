# PawFocus =^_^=

A cozy, pastel-themed desktop overlay study timer built with Python and Tkinter. Features a floating cat companion that switches states (sleeping, reading, playing) based on your timer, plus a (toggleable) countdown.

---

## 💻 Requirements

*   **Python 3.10.x** or newer
*   **Tkinter** (Built-in)
*   **Pixelify Sans** (The included `.ttf` font file)

---

## Setup

1. **Clone the Repo:** onto your computer.
2. **Install the Font (Mac Only):** If you are on a Mac, double-click `PixelifySans-VariableFont_wght.ttf` inside your project folder and install it to your system Font Book. (Windows loads it automatically).

---

## How to Use

1. **Launch the App:** Open your terminal in the project folder and run:
   ```bash
   python main.py
   ```
   or alternatively, press the Run button in your IDE.

2. **Set Your Timer:** 
   * **Presets:** Pick a method like *Pomodoro*, *52/17*, or *90/20* from the blue dropdown.
   * **Rounds:** Type directly into the rounds field to change how many sessions you want to do.
   * **Custom:** Select *Custom* from the dropdown to unlock the study and break minute text boxes. Type your times and click **Apply Settings**.

3. **Control the Kitty Overlay:**
   * **Start:** Click **▶ START**. Your settings entry boxes will lock, your kitty will switch to reading mode, and the clock will start counting down.
   * **Move:** Left-click and drag anywhere on the cat to move it around your desktop. It stays on top of all your other windows (it re-checks every half second).
   * **Right-click Menu:** Right-click the cat (two-finger click on a Mac trackpad) to reopen the PawFocus settings window, show/hide the to-do list, or **Quit PawFocus** for good.
   * **Close the Dashboard:** Closing the dashboard window only hides it. The cat and timer keep running. Reopen it from the cat's right-click menu (or the Dock icon on Mac).
   * **To-Do List:** Click the cat (without dragging) to drop down your to-do list. Type a task and press Enter or **+ Add**, tick the box to mark it done, **✕** to delete, and **🧹 clear finished** to tidy up. Click the cat again or press Esc to fold it away. Tasks are saved to `todos.json` in the project folder, so they're still there next time.
   * **Hide Time:** Click **Hide/Show Clock on Cat** on the dashboard to toggle the numbers on and off if they distract you.
   * **Resize:** Move the **Kitty Scale Size Settings** slider to instantly resize the cat to 50%, 100%, or 150%.
   * **Alerts:** When time is up, an alarm rings and a popup appears to tell you it's break time. 
   * **Stop:** Click the red **❌ STOP** button anytime to cancel the ongoing timer.

4. **Resize the Dashboard:** Drag the dashboard window's edges and all the text, buttons and spacing scale to fit. It won't shrink below 320×540, and it stops growing at 200%.