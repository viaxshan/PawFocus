import tkinter as tk
from tkinter import messagebox

class AppController:
    def __init__(self, timer, dashboard, overlay):
        self.timer = timer
        self.view = dashboard
        self.overlay = overlay
        self.show_overlay_clock = True
        
        self.view.selected_method.trace_add("write", lambda *args: self.handle_method_change(self.view.selected_method.get()))
        self.view.start_btn.config(command=self.handle_start)
        self.view.cancel_btn.config(command=self.handle_cancel)
        self.view.save_custom_btn.config(command=self.handle_apply_settings)
        self.view.toggle_overlay_clock_btn.config(command=self.handle_toggle_clock)
        self.view.size_slider.config(command=self.handle_scale_slider)
        
        self.overlay.x_offset = 0
        self.overlay.y_offset = 0
        self.overlay.canvas.bind("<Button-1>", self.start_drag)
        self.overlay.canvas.bind("<B1-Motion>", self.drag_window)
        
        self.sync_timers_display()
        self.refresh_ui_fields_from_model()

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
            messagebox.showinfo("Saved!", "Session parameters successfully committed!")
        except ValueError:
            messagebox.showerror("Error", "Please input whole numbers only into settings fields!")

    def handle_toggle_clock(self):
        if self.show_overlay_clock:
            self.show_overlay_clock = False
            self.overlay.set_clock_visibility(False)
            self.view.toggle_overlay_clock_btn.config(text="⏰ Show Clock on Cat")
        else:
            self.show_overlay_clock = True
            self.overlay.set_clock_visibility(True)
            self.view.toggle_overlay_clock_btn.config(text="⏰ Hide Clock on Cat")

    def handle_scale_slider(self, val):
        level = int(val)
        labels = {1: "Size: 50%", 2: "Size: 100%", 3: "Size: 150%"}
        self.view.size_label.config(text=labels[level])
        self.overlay.apply_scale_factor(level)

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
                
                self.overlay.attributes("-topmost", True)
                messagebox.showinfo("Take a Break!", "Time for a short break! Your kitty is playing.", parent=self.overlay)
                
                self.view.after(1000, self.countdown_heartbeat)
                
            elif signal == "NEXT_ROUND":
                self.overlay.change_kitty_state("reading")
                self.view.status_label.config(text=f"Status: Focus Phase! Round {self.timer.current_round} 🐾", fg="#3d3a4e")
                self.view.bell()
                
                self.overlay.attributes("-topmost", True)
                messagebox.showinfo("Back to Work!", "Break's over! Let's lock back in.", parent=self.overlay)
                
                self.view.after(1000, self.countdown_heartbeat)
                
            elif signal == "FINISHED":
                self.view.bell()
                
                self.overlay.attributes("-topmost", True)
                messagebox.showinfo("Session Finished!", "Good study session!", parent=self.overlay)
                
                self.handle_cancel()

    def start_drag(self, event):
        self.overlay.x_offset = event.x
        self.overlay.y_offset = event.y

    def drag_window(self, event):
        x = self.overlay.winfo_x() - self.overlay.x_offset + event.x
        y = self.overlay.winfo_y() - self.overlay.y_offset + event.y
        self.overlay.geometry(f"+{x}+{y}")
