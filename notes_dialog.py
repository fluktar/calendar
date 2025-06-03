from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QWidget, QListWidgetItem, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize
from note_manager import NoteManager
from note_single_dialog import NoteSingleDialog
import os

class NotesDialog(QDialog):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.setWindowTitle("Notatki użytkownika")
        self.resize(500, 400)
        self.manager = NoteManager(user_id)
        self.setup_ui()
        self.refresh_notes()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.notes_list = QListWidget()
        layout.addWidget(self.notes_list)
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Dodaj notatkę")
        add_btn.clicked.connect(self.add_note)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.notes_list.itemClicked.connect(self.open_note)

    def refresh_notes(self):
        self.notes_list.clear()
        notes = self.manager.get_notes()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_ok = QIcon(os.path.join(base_dir, 'images', 'check-solid.svg'))
        icon_x = QIcon(os.path.join(base_dir, 'images', 'rectangle-xmark-solid.svg'))
        for note in notes:
            item = QListWidgetItem(f"{note['created'].strftime('%Y-%m-%d %H:%M')}: {note['content'][:30]}...")
            item.setData(Qt.UserRole, note)
            widget = QWidget()
            hbox = QHBoxLayout()
            hbox.setContentsMargins(0,0,0,0)
            hbox.addWidget(QLabel(item.text()))
            hbox.addStretch(1)  # przesuwa przyciski do prawej
            ok_btn = QPushButton()
            ok_btn.setIcon(icon_ok)
            ok_btn.setIconSize(QSize(18, 18))
            ok_btn.setFixedSize(24, 24)
            ok_btn.setToolTip('Zatwierdź notatkę')
            ok_btn.clicked.connect(lambda _, n=note: self.accept_note(n['id']))
            hbox.addWidget(ok_btn)
            del_btn = QPushButton()
            del_btn.setIcon(icon_x)
            del_btn.setIconSize(QSize(18, 18))
            del_btn.setFixedSize(24, 24)
            del_btn.setToolTip('Usuń notatkę')
            del_btn.clicked.connect(lambda _, n=note: self.delete_note(n['id']))
            hbox.addWidget(del_btn)
            widget.setLayout(hbox)
            item.setSizeHint(widget.sizeHint())
            self.notes_list.addItem(item)
            self.notes_list.setItemWidget(item, widget)

    def add_note(self):
        dialog = NoteSingleDialog(self, None)
        if dialog.exec() == QDialog.Accepted:
            content, color = dialog.get_note()
            self.manager.add_note(content, color)
            self.refresh_notes()

    def open_note(self, item):
        note = item.data(Qt.UserRole)
        dialog = NoteSingleDialog(self, note)
        if dialog.exec() == QDialog.Accepted:
            content, color = dialog.get_note()
            self.manager.update_note(note['id'], content, color)
            self.refresh_notes()

    def accept_note(self, note_id):
        QMessageBox.information(self, "Zatwierdzono", "Notatka została zatwierdzona.")
        # Możesz dodać logikę np. zmiany statusu notatki

    def delete_note(self, note_id):
        reply = QMessageBox.question(self, "Usuń notatkę", "Czy na pewno usunąć notatkę?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.manager.delete_note(note_id)
            self.refresh_notes()
