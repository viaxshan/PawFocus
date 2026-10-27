from timer_engine import StudyTimer
from ui_views import DashboardWindow, KittyOverlay
from app_controller import AppController

from timer_engine import StudyTimer
from ui_views import DashboardWindow, KittyOverlay
from app_controller import AppController

def main():
    timer = StudyTimer()
    
    methods_list = list(timer.studies.keys())
    
    dashboard = DashboardWindow(methods_list)
    overlay = KittyOverlay(dashboard)
    
    controller = AppController(timer, dashboard, overlay)
    
    dashboard.mainloop()

if __name__ == "__main__":
    main()
