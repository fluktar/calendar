from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialogButtonBox, QMessageBox

class LoginDialog(QDialog):
    def __init__(self, task_manager):
        super().__init__()
        self.setWindowTitle("Logowanie/Rejestracja użytkownika")
        self.task_manager = task_manager
        self.setup_ui()
        self.user_id = None

    def setup_ui(self):
        layout = QVBoxLayout()
        self.info_label = QLabel("Podaj nazwę użytkownika i hasło:")
        layout.addWidget(self.info_label)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nazwa użytkownika")
        layout.addWidget(self.username_edit)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Hasło")
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)
        self.login_btn = QPushButton("Zaloguj")
        self.register_btn = QPushButton("Zarejestruj")
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        self.setLayout(layout)
        self.login_btn.clicked.connect(self.try_login)
        self.register_btn.clicked.connect(self.try_register)

    def try_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if self.task_manager.login_user(username, password):
            self.accept()
        else:
            QMessageBox.warning(self, "Błąd logowania", "Nieprawidłowa nazwa użytkownika lub hasło.")

    def try_register(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Błąd", "Podaj nazwę użytkownika i hasło.")
            return
        user_id = self.task_manager.register_user(username, password)
        if user_id:
            QMessageBox.information(self, "Sukces", "Użytkownik zarejestrowany. Możesz się zalogować.")
        else:
            QMessageBox.warning(self, "Błąd", "Taki użytkownik już istnieje.")
