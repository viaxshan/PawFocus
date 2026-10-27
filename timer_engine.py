class StudyTimer:
    """StudyTimer class that manages the time aspects of the application."""
    def __init__(self):
        self.studies = {
            "Pomodoro": [25, 5, 4], # type mapped to studytime, breaktime, and number of rounds
            "52/17": [52, 17, 2],
            "90/20": [90, 20, 2],
            "Custom": [25, 5, 1]
        }

        # initialize instance variables to default to Pomodoro
        self.active_method = "Pomodoro"
        self.study_mins = self.studies["Pomodoro"][0]
        self.study_break = self.studies["Pomodoro"][1]
        self.study_rounds = self.studies["Pomodoro"][2]

        self.time_left_seconds = self.study_mins * 60
        self.current_round = 1
        self.is_break_state = False
        self.is_running = False

    def set_study_method(self, name: str):
        """Set the selected study method as the active one. Raises a ValueError if the selected method is not in the list of options."""
        if name not in self.studies:
            raise ValueError("This method is not an option.")
        self.active_method = name
        self.study_mins = self.studies[name][0]
        self.study_break = self.studies[name][1]
        self.study_rounds = self.studies[name][2]

        self.time_left_seconds = self.study_mins * 60
        self.is_break_state = False
        self.current_round = 1
    
    def set_custom(self, study_time: int, break_time: int):
        """Sets the custom values for the custom study time."""
        self.studies["Custom"][0] = study_time
        self.studies["Custom"][1] = break_time

        if self.active_method == "Custom":
            self.study_mins = study_time
            self.study_break = break_time
            self.time_left_seconds = study_time * 60

    def set_rounds(self, rounds: int):
        """Sets the number of rounds for the study method chosen."""
        self.study_rounds = rounds
        self.studies[self.active_method][2] = rounds

    def tick(self) -> str:
        """Determines the state of the application and decides to tick down, switch states, or finish."""
        if not self.is_running:
            return "PAUSED"
            
        if self.time_left_seconds > 0:
            self.time_left_seconds -= 1
            return "TICK"
            
        if not self.is_break_state:
            self.is_break_state = True
            self.time_left_seconds = self.study_break * 60
            return "BREAK"
        else:
            if self.current_round >= self.study_rounds:
                self.is_running = False
                return "FINISHED"
            else:
                self.current_round += 1
                self.is_break_state = False
                self.time_left_seconds = self.study_mins * 60
                return "NEXT_ROUND"
                
    def get_formatted_time(self) -> str:
        """Helper to get clean clock numbers."""
        mins, secs = divmod(self.time_left_seconds, 60)
        return f"{mins:02d}:{secs:02d}"
