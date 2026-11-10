from timer_engine import StudyTimer
from todo_model import TodoList
from ui_views import DashboardWindow, KittyOverlay, TodoDropdown, asset_path
from app_controller import AppController


def main():
    timer = StudyTimer()
    todo_list = TodoList(asset_path("todos.json"))

    methods_list = list(timer.studies.keys())

    dashboard = DashboardWindow(methods_list)
    overlay = KittyOverlay(dashboard)
    todo_view = TodoDropdown(dashboard)

    controller = AppController(timer, dashboard, overlay, todo_view, todo_list)

    dashboard.mainloop()


if __name__ == "__main__":
    main()