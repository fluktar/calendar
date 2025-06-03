from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton, QLabel, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCharFormat, QColor

class NoteSingleDialog(QDialog):
    COLORS = [
        ("Czarny", "black"),
        ("Czerwony", "red"),
        ("Zielony", "green"),
        ("Niebieski", "blue"),
        ("Pomarańczowy", "orange"),
        ("Fioletowy", "purple"),
    ]
    def __init__(self, parent, note=None):
        super().__init__(parent)
        self.setWindowTitle("Notatka")
        self.resize(400, 300)
        self.note = note
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        if self.note:
            self.text_edit.setPlainText(self.note['content'])
        layout.addWidget(QLabel("Treść notatki:"))
        layout.addWidget(self.text_edit)
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Kolor tekstu:"))
        self.color_combo = QComboBox()
        for name, color in self.COLORS:
            self.color_combo.addItem(name, color)
        if self.note:
            idx = self.color_combo.findData(self.note.get('color', 'black'))
            if idx >= 0:
                self.color_combo.setCurrentIndex(idx)
        color_layout.addWidget(self.color_combo)
        color_btn = QPushButton("Zmień kolor zaznaczenia")
        color_btn.clicked.connect(self.change_text_color)
        color_layout.addWidget(color_btn)
        layout.addLayout(color_layout)
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Zapisz")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        del_btn = QPushButton("Usuń")
        del_btn.clicked.connect(self.delete_note)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_note(self):
        return self.text_edit.toHtml(), self.color_combo.currentData()

    def change_text_color(self):
        color = self.color_combo.currentData()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(cursor.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.text_edit.mergeCurrentCharFormat(fmt)

    def delete_note(self):
        self.done(2)  # custom code for delete
