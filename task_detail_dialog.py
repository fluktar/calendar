from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QLineEdit, QDialogButtonBox, QHBoxLayout, QComboBox, QTextEdit, QDateEdit
from PySide6.QtCore import QDate
import json

class TaskDetailDialog(QDialog):
    def __init__(self, parent, date: QDate, task: dict, on_save, on_edit, on_remove):
        super().__init__(parent)
        self.setWindowTitle("Szczegóły zadania")
        self.task = task
        self.on_save = on_save
        self.on_edit = on_edit
        self.on_remove = on_remove
        self.date = date
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        label = QLabel(f"Tytuł: {self.task['text']}")
        layout.addWidget(label)
        desc_label = QLabel("Opis:")
        layout.addWidget(desc_label)
        self.desc_edit = QTextEdit(self.task.get('description', ''))
        layout.addWidget(self.desc_edit)
        priority_label = QLabel("Priorytet:")
        layout.addWidget(priority_label)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["niski", "średni", "wysoki"])
        self.priority_combo.setCurrentText(self.task.get('priority', 'średni'))
        layout.addWidget(self.priority_combo)
        repeat_label = QLabel("Powtarzanie:")
        layout.addWidget(repeat_label)
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["brak", "co tydzień", "co miesiąc"])
        self.repeat_combo.setCurrentText(self.task.get('repeat', 'brak'))
        layout.addWidget(self.repeat_combo)
        deadline_label = QLabel("Termin (deadline):")
        layout.addWidget(deadline_label)
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        if self.task.get('deadline'):
            self.deadline_edit.setDate(QDate.fromString(self.task['deadline'], 'yyyy-MM-dd'))
        else:
            self.deadline_edit.setDate(self.date)
        layout.addWidget(self.deadline_edit)
        status_box = QCheckBox("Wykonane")
        status_box.setChecked(self.task.get('status', 'nowe') == 'wykonane')
        layout.addWidget(status_box)
        in_progress_box = QCheckBox("W toku")
        in_progress_box.setChecked(self.task.get('status', 'nowe') == 'w toku')
        layout.addWidget(in_progress_box)
        edit_btn = QPushButton("Edytuj tytuł")
        layout.addWidget(edit_btn)
        remove_btn = QPushButton("Usuń")
        layout.addWidget(remove_btn)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        layout.addWidget(buttons)
        self.setLayout(layout)
        def save_changes():
            status = 'wykonane' if status_box.isChecked() else ('w toku' if in_progress_box.isChecked() else 'nowe')
            self.on_save(
                self.date,
                self.task['text'],
                self.task['text'],
                status,
                self.desc_edit.toPlainText(),
                self.priority_combo.currentText(),
                self.repeat_combo.currentText(),
                self.deadline_edit.date().toString('yyyy-MM-dd')
            )
            self.accept()
        def edit_task():
            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle("Edytuj tytuł zadania")
            edit_layout = QVBoxLayout()
            edit_line = QLineEdit(self.task['text'])
            edit_layout.addWidget(edit_line)
            save_btn = QPushButton("Zapisz zmiany")
            def save_edit():
                self.on_edit(
                    self.date,
                    self.task['text'],
                    edit_line.text(),
                    self.task.get('status', 'nowe'),
                    self.desc_edit.toPlainText(),
                    self.priority_combo.currentText(),
                    self.repeat_combo.currentText(),
                    self.deadline_edit.date().toString('yyyy-MM-dd')
                )
                edit_dialog.accept()
                self.accept()
            save_btn.clicked.connect(save_edit)
            edit_layout.addWidget(save_btn)
            edit_dialog.setLayout(edit_layout)
            edit_dialog.exec()
        def remove_task():
            self.on_remove(self.date, self.task['text'])
            self.accept()
        status_box.stateChanged.connect(lambda: (in_progress_box.setChecked(False)))
        in_progress_box.stateChanged.connect(lambda: (status_box.setChecked(False)))
        edit_btn.clicked.connect(edit_task)
        remove_btn.clicked.connect(remove_task)
        buttons.accepted.connect(save_changes)
