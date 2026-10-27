from tkinter import messagebox

class AppController:
    def __init__(self, timer, dashboard, overlay):
        self.timer = timer
        self.view = dashboard
        self.overlay = overlay
        
        self.view.selected_method.trace_add("write", lambda *args: self.handle_method_change(self.view.selected_method.get()))
        self.view.start_btn.config(command=self.handle_start)
        self.view.cancel_btn.config(command=self.handle_cancel)
        
        self.overlay.x_offset = 0
        self.overlay.y_offset = 0
        self.overlay.canvas.bind("<Button-1>", self.start_drag)
        self.overlay.canvas.bind("<B1-Motion>", self.drag_window)
        
        self.view.timer_label.config(text=self.timer.get_formatted_time())

    def handle_method_change(self, selected_value):
        """Triggers when the dropdown method choice updates."""
        self.timer.set_study_method(selected_value)
        self.view.timer_label.config(text=self.timer.get_formatted_time())

    def handle_start(self):
        """Triggers when clicking the START button."""
        self.timer.is_running = True
        
        self.overlay.change_kitty_state("reading")
        
        self.view.status_label.config(text="Status: Focus Mode Active!", fg="#3d3a4e")
        self.view.start_btn.config(state="disabled")
        self.view.cancel_btn.config(state="normal")
        self.view.dropdown.config(state="disabled")
        
        self.countdown_heartbeat()

    def handle_cancel(self):
        """Triggers when clicking CANCEL or when session completely resets."""
        self.timer.is_running = False
        self.timer.set_study_method(self.timer.active_method) 
        
        self.overlay.change_kitty_state("sleeping")
        
        self.view.timer_label.config(text=self.timer.get_formatted_time())
        self.view.status_label.config(text="Status: Ready to study!", fg="#3d3a4e")
        self.view.start_btn.config(state="normal")
        self.view.cancel_btn.config(state="disabled")
        self.view.dropdown.config(state="normal")

    def countdown_heartbeat(self):
        """The loops that fires every 1000ms to process time tracking changes."""
        if self.timer.is_running:
            signal = self.timer.tick()
            
            self.view.timer_label.config(text=self.timer.get_formatted_time())
            
            if signal == "TICK":
                self.view.after(1000, self.countdown_heartbeat)
                
            elif signal == "BREAK":
                self.overlay.change_kitty_state("playing")
                self.view.status_label.config(text=f"Status: Break Time! Round {self.timer.current_round}")
                self.view.bell()
                messagebox.showinfo("Take a Break!", "Time for a short break! Your kitty is playing.")
                self.view.after(1000, self.countdown_heartbeat)
                
            elif signal == "NEXT_ROUND":
                self.overlay.change_kitty_state("reading")
                self.view.status_label.config(text=f"Status: Focus Phase! Round {self.timer.current_round} 🐾")
                self.view.bell()
                messagebox.showinfo("Back to Work!", "Break's over! Let's lock back in.")
                self.view.after(1000, self.countdown_heartbeat)
                
            elif signal == "FINISHED":
                self.view.bell()
                messagebox.showinfo("Session Finished!", "Good study session!")
                self.handle_cancel()

    def start_drag(self, event):
        self.overlay.x_offset = event.x
        self.overlay.y_offset = event.y

    def drag_window(self, event):
        x = self.overlay.winfo_x() - self.overlay.x_offset + event.x
        y = self.overlay.winfo_y() - self.overlay.y_offset + event.y
        self.overlay.geometry(f"+{x}+{y}")
