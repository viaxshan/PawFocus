import tkinter as tk
from tkinter import messagebox

DRAG_THRESHOLD = 4     # pixels the mouse must move before a click counts as a drag
KEEP_ON_TOP_MS = 500   # how often the cat re-asserts that it's the top window


class AppController:
    def __init__(self, timer, dashboard, overlay, todo_view, todo_list):
        self.timer = timer
        self.view = dashboard
        self.overlay = overlay
        self.todo_view = todo_view
        self.todo_list = todo_list
        self.show_overlay_clock = True
        self.dialog_open = False

        self.view.selected_method.trace_add("write", lambda *args: self.handle_method_change(self.view.selected_method.get()))
        self.view.start_btn.config(command=self.handle_start)
        self.view.cancel_btn.config(command=self.handle_cancel)
        self.view.save_custom_btn.config(command=self.handle_apply_settings)
        self.view.toggle_overlay_clock_btn.config(command=self.handle_toggle_clock)
        self.view.size_slider.config(command=self.handle_scale_slider)

        # Closing the dashboard is the only way to quit; the cat itself can't be closed
        self.view.protocol("WM_DELETE_WINDOW", self.handle_quit)
        self.overlay.protocol("WM_DELETE_WINDOW", lambda: None)
        self.todo_view.protocol("WM_DELETE_WINDOW", self.todo_view.close)

        # Click the cat = open/close to-do list. Click and drag = move the cat.
        self.overlay.x_offset = 0
        self.overlay.y_offset = 0
        self.press_root = (0, 0)
        self.is_dragging = False
        self.overlay.canvas.bind("<Button-1>", self.start_drag)
        self.overlay.canvas.bind("<B1-Motion>", self.drag_window)
        self.overlay.canvas.bind("<ButtonRelease-1>", self.end_drag)

        self.todo_view.on_add = self.handle_todo_add
        self.todo_view.on_toggle = self.handle_todo_toggle
        self.todo_view.on_delete = self.handle_todo_delete
        self.todo_view.on_clear_done = self.handle_todo_clear_done
        self.refresh_todo_view()

        self.sync_timers_display()
        self.refresh_ui_fields_from_model()
        self.keep_on_top()

    # ---------- popups ----------

    def show_popup(self, title, message, parent=None, kind="info"):
        """Shows a message box on top of everything, pausing the keep-on-top loop so the cat doesn't cover it."""
        self.dialog_open = True
        try:
            parent = parent or self.overlay
            if parent is self.overlay:
                self.overlay.attributes("-topmost", True)
            if kind == "error":
                messagebox.showerror(title, message, parent=parent)
            else:
                messagebox.showinfo(title, message, parent=parent)
        finally:
            self.dialog_open = False

    # ---------- always on top ----------

    def keep_on_top(self):
        """Runs every half second: brings the cat (and an open to-do list) back to the front."""
        if not self.dialog_open:
            windows = [self.overlay]
            if self.todo_view.is_open:
                windows.append(self.todo_view)
            for window in windows:
                try:
                    if window.state() != "normal":   # e.g. hidden by "Show desktop"
                        window.deiconify()
                    window.attributes("-topmost", True)
                    window.lift()
                except tk.TclError:
                    return  # app is shutting down
        try:
            self.view.after(KEEP_ON_TOP_MS, self.keep_on_top)
        except tk.TclError:
            pass

    def handle_quit(self):
        self.todo_list.save()
        self.view.destroy()

    # ---------- timer + settings ----------

    def sync_timers_display(self):
        time_str = self.timer.get_formatted_time()
        self.view.timer_label.config(text=time_str)
        self.overlay.update_overlay_clock_text(time_str)

    def refresh_ui_fields_from_model(self):
        self.view.study_entry.config(state="normal")
        self.view.break_entry.config(state="normal")
        self.view.rounds_entry.config(state="normal")

        self.view.study_entry.delete(0, "end")
        self.view.study_entry.insert(0, str(self.timer.study_mins))

        self.view.break_entry.delete(0, "end")
        self.view.break_entry.insert(0, str(self.timer.study_break))

        self.view.rounds_entry.delete(0, "end")
        self.view.rounds_entry.insert(0, str(self.timer.study_rounds))

        if self.timer.active_method == "Custom":
            self.view.study_entry.config(state="normal")
            self.view.break_entry.config(state="normal")
            self.view.rounds_entry.config(state="normal")
            self.view.save_custom_btn.config(state="normal")
        else:
            self.view.study_entry.config(state="disabled")
            self.view.break_entry.config(state="disabled")
            self.view.rounds_entry.config(state="normal")
            self.view.save_custom_btn.config(state="disabled")

    def handle_method_change(self, selected_value):
        self.timer.set_study_method(selected_value)
        self.sync_timers_display()
        self.refresh_ui_fields_from_model()

    def handle_apply_settings(self):
        try:
            study_t = int(self.view.study_entry.get())
            break_t = int(self.view.break_entry.get())
            rounds_t = int(self.view.rounds_entry.get())

            self.timer.set_custom(study_t, break_t)
            self.timer.set_rounds(rounds_t)

            self.sync_timers_display()
            self.show_popup("Saved!", "Session parameters successfully committed!", parent=self.view)
        except ValueError:
            self.show_popup("Error", "Please input whole numbers only into settings fields!", parent=self.view, kind="error")

    def handle_toggle_clock(self):
        if self.show_overlay_clock:
            self.show_overlay_clock = False
            self.overlay.set_clock_visibility(False)
            self.view.toggle_overlay_clock_btn.config(text="⏰ Show Clock on Cat")
        else:
            self.show_overlay_clock = True
            self.overlay.set_clock_visibility(True)
            self.view.toggle_overlay_clock_btn.config(text="⏰ Hide Clock on Cat")
        self.position_todo()

    def handle_scale_slider(self, val):
        level = int(val)
        labels = {1: "Size: 50%", 2: "Size: 100%", 3: "Size: 150%"}
        self.view.size_label.config(text=labels[level])
        self.overlay.apply_scale_factor(level)
        self.position_todo()

    def handle_start(self):
        try:
            rounds_t = int(self.view.rounds_entry.get())
            self.timer.set_rounds(rounds_t)
        except ValueError:
            pass

        self.timer.is_running = True
        self.overlay.change_kitty_state("reading")

        self.view.status_label.config(text="Status: Focus Mode Active! 🐾", fg="#3d3a4e")
        self.view.start_btn.config(state="disabled")
        self.view.cancel_btn.config(state="normal")
        self.view.study_entry.config(state="disabled")
        self.view.break_entry.config(state="disabled")
        self.view.dropdown.config(state="disabled")
        self.view.rounds_entry.config(state="disabled")
        self.view.save_custom_btn.config(state="disabled")

        self.countdown_heartbeat()

    def handle_cancel(self):
        self.timer.is_running = False
        self.timer.set_study_method(self.timer.active_method)
        self.overlay.change_kitty_state("sleeping")

        self.sync_timers_display()
        self.refresh_ui_fields_from_model()

        self.view.rounds_entry.config(state="normal")

        self.view.status_label.config(text="Status: Ready to read!", fg="#3d3a4e")
        self.view.start_btn.config(state="normal")
        self.view.cancel_btn.config(state="disabled")
        self.view.dropdown.config(state="normal")

    def countdown_heartbeat(self):
        if self.timer.is_running:
            signal = self.timer.tick()
            self.sync_timers_display()

            if signal == "TICK":
                self.view.after(1000, self.countdown_heartbeat)

            elif signal == "BREAK":
                self.overlay.change_kitty_state("playing")
                self.view.status_label.config(text=f"Status: Break Time! Round {self.timer.current_round}")
                self.view.bell()
                self.show_popup("Take a Break!", "Time for a short break! Your kitty is playing.")
                self.view.after(1000, self.countdown_heartbeat)

            elif signal == "NEXT_ROUND":
                self.overlay.change_kitty_state("reading")
                self.view.status_label.config(text=f"Status: Focus Phase! Round {self.timer.current_round} 🐾", fg="#3d3a4e")
                self.view.bell()
                self.show_popup("Back to Work!", "Break's over! Let's lock back in.")
                self.view.after(1000, self.countdown_heartbeat)

            elif signal == "FINISHED":
                self.view.bell()
                self.show_popup("Session Finished!", "Good study session!")
                self.handle_cancel()

    # ---------- moving the cat / clicking it ----------

    def start_drag(self, event):
        self.overlay.x_offset = event.x
        self.overlay.y_offset = event.y
        self.press_root = (event.x_root, event.y_root)
        self.is_dragging = False

    def drag_window(self, event):
        if not self.is_dragging:
            moved_x = abs(event.x_root - self.press_root[0])
            moved_y = abs(event.y_root - self.press_root[1])
            if max(moved_x, moved_y) < DRAG_THRESHOLD:
                return  # still just a click, not a drag
            self.is_dragging = True

        x = event.x_root - self.overlay.x_offset
        y = event.y_root - self.overlay.y_offset
        self.overlay.geometry(f"+{x}+{y}")
        self.position_todo(x, y)  # the to-do list follows the cat

    def end_drag(self, event):
        if not self.is_dragging:
            self.toggle_todo()
        self.is_dragging = False

    # ---------- to-do list ----------

    def toggle_todo(self):
        if self.todo_view.is_open:
            self.todo_view.close()
        else:
            self.refresh_todo_view()
            self.todo_view.place_near(*self.overlay.get_bounds())
            self.todo_view.open()

    def position_todo(self, x=None, y=None):
        if self.todo_view.is_open:
            self.todo_view.place_near(*self.overlay.get_bounds(x, y))

    def refresh_todo_view(self):
        self.todo_view.render(self.todo_list.items, self.todo_list.remaining())
        self.position_todo()  # height may have changed

    def handle_todo_add(self, text):
        added = self.todo_list.add(text)
        if added:
            self.refresh_todo_view()
        return added

    def handle_todo_toggle(self, index):
        self.todo_list.toggle(index)
        self.refresh_todo_view()

    def handle_todo_delete(self, index):
        self.todo_list.remove(index)
        self.refresh_todo_view()

    def handle_todo_clear_done(self):
        self.todo_list.clear_done()
        self.refresh_todo_view()