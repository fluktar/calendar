import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QCalendarWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QListWidget, QMessageBox, QMenuBar, QDialog
from PySide6.QtCore import QDate, QLocale, Qt
from PySide6.QtGui import QFont, QTextCharFormat, QPalette, QColor, QAction
from task_manager import TaskManager
from task_detail_dialog import TaskDetailDialog
from task_list_dialog import TaskListDialog
from login_dialog import LoginDialog
from user_manager import UserManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Przykład QCalendarWidget")
        self.resize(400, 300)
        self.user_manager = UserManager()
        self.theme = 'light'
        self.login_user()
        self.setup_ui()
        self.add_theme_switcher()
        self.add_notes_menu()

    def login_user(self):
        login_dialog = LoginDialog(self.user_manager)
        if login_dialog.exec() != QDialog.Accepted:
            sys.exit(0)
        self.task_manager = TaskManager(self.user_manager.user_id)

    def setup_ui(self):
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setLocale(QLocale("pl_PL"))
        self.calendar.setFirstDayOfWeek(Qt.Monday)
        self.calendar.setGridVisible(True)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setNavigationBarVisible(True)
        fmt = QTextCharFormat()
        fmt.setFont(QFont("Arial", 10, QFont.Bold))
        self.calendar.setDateTextFormat(QDate.currentDate(), fmt)
        self.calendar.clicked.connect(self.on_date_clicked)
        left_layout.addWidget(self.calendar)
        self.label = QLabel("Wybierz datę z kalendarza")
        left_layout.addWidget(self.label)
        main_layout.addLayout(left_layout)
        self.all_tasks_list = QListWidget()
        self.all_tasks_list.setMinimumWidth(250)
        self.all_tasks_list.setWordWrap(True)
        self.refresh_all_tasks()
        self.all_tasks_list.itemClicked.connect(self.on_all_tasks_item_clicked)
        main_layout.addWidget(self.all_tasks_list)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.refresh_calendar_colors()

    def add_theme_switcher(self):
        menubar = self.menuBar() if hasattr(self, 'menuBar') else QMenuBar(self)
        theme_menu = menubar.addMenu("Motyw")
        light_action = QAction("Jasny", self)
        dark_action = QAction("Ciemny", self)
        light_action.triggered.connect(lambda: self.set_theme('light'))
        dark_action.triggered.connect(lambda: self.set_theme('dark'))
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)
        self.setMenuBar(menubar)

    def add_notes_menu(self):
        menubar = self.menuBar()
        notes_menu = menubar.addMenu("Notatki")
        open_notes_action = QAction("Otwórz notatki", self)
        open_notes_action.triggered.connect(self.open_notes_dialog)
        notes_menu.addAction(open_notes_action)

    def open_notes_dialog(self):
        from notes_dialog import NotesDialog
        dialog = NotesDialog(self, self.user_manager.user_id)
        dialog.exec()

    def set_theme(self, theme):
        app = QApplication.instance()
        palette = QPalette()
        if theme == 'dark':
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setStyleSheet("")
        else:
            palette = app.style().standardPalette()
            # Wymuszam jasny styl dla menu rozwijanego
            app.setStyleSheet("QMenu { background: #f5f5f5; color: #222; } QMenu::item:selected { background: #d0d0d0; color: #000; }")
        app.setPalette(palette)
        self.theme = theme

    def refresh_all_tasks(self):
        self.all_tasks_list.clear()
        tasks = self.task_manager.load_tasks()
        for date_str, day_tasks in tasks.items():
            for task in day_tasks:
                status = task.get('status', 'nowe')
                self.all_tasks_list.addItem(f"{date_str}: {task['text']} [{status}]")

    def refresh_calendar_colors(self):
        fmt_task = QTextCharFormat()
        fmt_task.setBackground(Qt.yellow)
        fmt_task.setFontWeight(QFont.Bold)
        for date_str in self.task_manager.get_all_dates_with_tasks():
            try:
                qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                self.calendar.setDateTextFormat(qdate, fmt_task)
            except Exception:
                pass

    def on_date_clicked(self, date):
        formatted_date = date.toString("dd MMMM yyyy")
        self.label.setText(f"Wybrano datę: {formatted_date}")
        self.show_tasks_dialog(date)

    def on_all_tasks_item_clicked(self, item):
        try:
            date_str, rest = item.text().split(': ', 1)
            task_text = rest.rsplit(' [', 1)[0]
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            self.show_task_detail_dialog(date, task_text)
        except Exception:
            pass

    def show_tasks_dialog(self, date):
        tasks = self.task_manager.get_tasks_for_date(date)
        def on_add(date, text):
            # Dodajemy zadanie z domyślnymi wartościami, można rozbudować o okno dialogowe
            self.task_manager.save_task(date.toString('yyyy-MM-dd'), text)
            self.refresh_all_tasks()
            self.refresh_calendar_colors()
        def on_task_clicked(date, task_text):
            self.show_task_detail_dialog(date, task_text)
        def on_remove_task(date, text):
            self.task_manager.remove_task(date, text)
            self.refresh_all_tasks()
            self.refresh_calendar_colors()
        dialog = TaskListDialog(self, date, tasks, on_add, on_task_clicked, on_remove_task)
        dialog.exec()
        self.refresh_all_tasks()
        self.refresh_calendar_colors()

    def show_task_detail_dialog(self, date, task_text):
        tasks = self.task_manager.get_tasks_for_date(date)
        task = next((t for t in tasks if t['text'] == task_text), None)
        if not task:
            return
        def on_save(date, old_text, new_text, status, description, priority, repeat, deadline):
            self.task_manager.update_task(
                task['id'],
                new_text=new_text,
                status=status,
                description=description,
                priority=priority,
                repeat=repeat,
                deadline=deadline
            )
            self.refresh_all_tasks()
            self.refresh_calendar_colors()
        def on_edit(date, old_text, new_text, status, description, priority, repeat, deadline):
            self.task_manager.update_task(
                task['id'],
                new_text=new_text,
                status=status,
                description=description,
                priority=priority,
                repeat=repeat,
                deadline=deadline
            )
            self.refresh_all_tasks()
            self.refresh_calendar_colors()
        def on_remove(date, text):
            self.task_manager.remove_task(task['id'])
            self.refresh_all_tasks()
            self.refresh_calendar_colors()
        dialog = TaskDetailDialog(self, date, task, on_save, on_edit, on_remove)
        dialog.exec()
        self.refresh_all_tasks()
        self.refresh_calendar_colors()

    def showEvent(self, event):
        super().showEvent(event)
        self.show_today_tasks_notification()

    def show_today_tasks_notification(self):
        today_tasks = self.task_manager.get_tasks_for_today()
        if today_tasks:
            msg = QMessageBox(self)
            msg.setWindowTitle("Zadania na dziś")
            msg.setText("Masz zadania na dziś:")
            msg.setInformativeText("\n".join([f"- {t['text']}" for t in today_tasks]))
            msg.exec()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()