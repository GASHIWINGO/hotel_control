from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt

from core.auth import change_password


class ChangePasswordDialog(QDialog):
    """Диалог для смены пароля при первом входе."""
    
    def __init__(self, user_id, current_password, parent=None):
        super().__init__(parent)
        
        self.user_id = user_id
        self.current_password = current_password
        
        self.setWindowTitle("Смена пароля")
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Информационное сообщение
        info_label = QLabel(
            "Это ваш первый вход в систему или был выполнен сброс пароля. "
            "Пожалуйста, смените пароль для продолжения работы."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Поле для текущего пароля
        current_label = QLabel("Текущий пароль:")
        self.current_edit = QLineEdit()
        self.current_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_edit.setText(current_password)  # Заполняем текущим паролем для удобства
        layout.addWidget(current_label)
        layout.addWidget(self.current_edit)
        
        # Поле для нового пароля
        new_label = QLabel("Новый пароль:")
        self.new_edit = QLineEdit()
        self.new_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(new_label)
        layout.addWidget(self.new_edit)
        
        # Поле для подтверждения нового пароля
        confirm_label = QLabel("Подтверждение нового пароля:")
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(confirm_label)
        layout.addWidget(self.confirm_edit)
        
        # Кнопки
        button_box = QDialogButtonBox()
        self.ok_button = QPushButton("Изменить пароль")
        self.ok_button.clicked.connect(self.accept_change)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        
        button_box.addButton(self.ok_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        
        layout.addWidget(button_box)
        
        self.setTabOrder(self.current_edit, self.new_edit)
        self.setTabOrder(self.new_edit, self.confirm_edit)
        self.setTabOrder(self.confirm_edit, button_box)
        
        self.new_edit.setFocus()
    
    def accept_change(self):
        """Обработка нажатия кнопки OK."""
        current_password = self.current_edit.text()
        new_password = self.new_edit.text()
        confirm_password = self.confirm_edit.text()
        
        # Валидация
        if not current_password:
            QMessageBox.warning(self, "Ошибка", "Введите текущий пароль.")
            self.current_edit.setFocus()
            return
        
        if not new_password:
            QMessageBox.warning(self, "Ошибка", "Введите новый пароль.")
            self.new_edit.setFocus()
            return
        
        if not confirm_password:
            QMessageBox.warning(self, "Ошибка", "Подтвердите новый пароль.")
            self.confirm_edit.setFocus()
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            self.confirm_edit.setFocus()
            return
        
        if new_password == current_password:
            QMessageBox.warning(self, "Ошибка", "Новый пароль должен отличаться от текущего.")
            self.new_edit.setFocus()
            return
        
        # Проверяем сложность пароля
        if len(new_password) < 6:
            QMessageBox.warning(self, "Ошибка", "Новый пароль должен содержать не менее 6 символов.")
            self.new_edit.setFocus()
            return
        
        # Меняем пароль
        success, message = change_password(self.user_id, current_password, new_password)
        
        if success:
            QMessageBox.information(self, "Успех", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", message)