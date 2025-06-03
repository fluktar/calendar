from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLineEdit, QPushButton, QHBoxLayout, QDialogButtonBox, QComboBox, QLabel
from PySide6.QtCore import QDate, Qt

class TaskListDialog(QDialog):
    def __init__(self, parent, date: QDate, tasks: list, on_add, on_task_clicked, on_remove_task, filter_status='wszystkie'):
        super().__init__(parent)
        self.setWindowTitle(f"Zadania na {date.toString('dd MMMM yyyy')}")
        self.resize(400, 350)
        self.on_add = on_add
        self.on_task_clicked = on_task_clicked
        self.on_remove_task = on_remove_task
        self.date = date
        self.tasks = tasks
        self.filter_status = filter_status
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filtruj po statusie:")
        filter_layout.addWidget(filter_label)
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["wszystkie", "nowe", "w toku", "wykonane"])
        self.filter_combo.setCurrentText(self.filter_status)
        self.filter_combo.currentTextChanged.connect(self.refresh_list)
        filter_layout.addWidget(self.filter_combo)
        layout.addLayout(filter_layout)
        self.task_list = QListWidget()
        self.task_list.setWordWrap(True)
        layout.addWidget(self.task_list)
        self.refresh_list()
        add_layout = QHBoxLayout()
        self.new_task_edit = QLineEdit()
        self.new_task_edit.setPlaceholderText("Dodaj nowe zadanie...")
        add_btn = QPushButton("Dodaj")
        add_btn.clicked.connect(self.add_task)
        add_layout.addWidget(self.new_task_edit)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)
        self.task_list.itemClicked.connect(self.handle_task_clicked)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def refresh_list(self):
        self.task_list.clear()
        status_filter = self.filter_combo.currentText()
        for task in self.tasks:
            if status_filter == "wszystkie" or task.get('status', 'nowe') == status_filter:
                item_text = f"{task['text']} [{task.get('status', 'nowe')}] ({task.get('priority', 'średni')})"
                self.task_list.addItem(item_text)

    def add_task(self):
        text = self.new_task_edit.text().strip()
        if text:
            self.on_add(self.date, text)
            self.new_task_edit.clear()
            self.accept()

    def handle_task_clicked(self, item):
        task_text = item.text().split(' [')[0]
        self.on_task_clicked(self.date, task_text)
        self.accept()

    def remove_task(self, idx):
        task = self.tasks[idx]
        self.on_remove_task(self.date, task['text'])
        self.accept()
