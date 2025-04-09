from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QFormLayout, QLineEdit, QComboBox,
    QMessageBox, QCheckBox, QLabel, QSpacerItem, QSizePolicy,
    QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.auth import create_user, unblock_user, update_user
from core.models import UserRoleEnum, Role, User
from core.database import get_db_session


class UserDialog(QDialog):
    """Диалог для добавления или редактирования пользователя."""
    
    def __init__(self, parent=None, user_id=None):

        super().__init__(parent)
        
        self.user_id = user_id
        self.is_edit_mode = user_id is not None
        
        # Настройка диалога
        self.setWindowTitle("Редактирование пользователя" if self.is_edit_mode else "Добавление пользователя")
        self.setMinimumWidth(350)
        
        # Создаем форму
        layout = QFormLayout(self)
        layout.setSpacing(10)
        
        # Поле логина
        self.login_input = QLineEdit()
        layout.addRow("Логин:", self.login_input)
        
        # Поле пароля (только для новых пользователей)
        if not self.is_edit_mode:
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addRow("Пароль:", self.password_input)
        
        # Выпадающий список ролей
        self.role_combo = QComboBox()
        self.load_roles()
        layout.addRow("Роль:", self.role_combo)
        
        # Флажок блокировки
        if self.is_edit_mode:
            self.block_check = QCheckBox("Заблокирован")
            layout.addRow("Статус:", self.block_check)
            self.load_user_data()
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow("", button_layout)
    
    def load_roles(self):
        """Загружает список ролей."""
        session = get_db_session()
        try:
            roles = session.query(Role).all()
            
            for role in roles:
                # Добавляем роль в комбобокс
                self.role_combo.addItem(role.role_name.value, role.role_id)
        finally:
            session.close()
    
    def load_user_data(self):
        """Загружает данные пользователя для редактирования."""
        session = get_db_session()
        try:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user:
                self.login_input.setText(user.login)
                
                # Выбираем роль пользователя
                for i in range(self.role_combo.count()):
                    if self.role_combo.itemData(i) == user.role_id:
                        self.role_combo.setCurrentIndex(i)
                        break
                
                self.block_check.setChecked(user.is_blocked)
        finally:
            session.close()
    
    def get_form_data(self):
        """Получает данные формы."""
        data = {
            'login': self.login_input.text().strip(),
            'role_id': self.role_combo.currentData()
        }
        
        if not self.is_edit_mode:
            data['password'] = self.password_input.text()
        
        if self.is_edit_mode:
            data['is_blocked'] = self.block_check.isChecked()
        
        return data


class UserManagementWidget(QWidget):
    """Виджет для управления пользователями."""
    
    user_modified = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Настройка виджета
        self.setup_ui()
        
        # Загрузка данных
        self.load_users()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        main_layout = QVBoxLayout(self)
        
        # Заголовок
        header_label = QLabel("Управление пользователями")
        header_font = header_label.font()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header_label.setFont(header_font)
        main_layout.addWidget(header_label)
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["ID", "Логин", "Роль", "Статус", "Попытки входа"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        main_layout.addWidget(self.users_table)
        
        # Панель кнопок
        button_layout = QHBoxLayout()
        
        # Кнопка добавления пользователя
        self.add_button = QPushButton("Добавить пользователя")
        self.add_button.clicked.connect(self.add_user)
        button_layout.addWidget(self.add_button)
        
        # Кнопка редактирования пользователя
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_user)
        button_layout.addWidget(self.edit_button)
        
        # Кнопка разблокировки пользователя
        self.unblock_button = QPushButton("Разблокировать")
        self.unblock_button.clicked.connect(self.unblock_user)
        button_layout.addWidget(self.unblock_button)
        
        button_layout.addStretch()
        
        # Кнопка обновления
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_users)
        button_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(button_layout)
    
    def load_users(self):
        """Загружает список пользователей из базы данных."""
        session = get_db_session()
        try:
            # Получаем пользователей с их ролями
            users = session.query(User).all()
            
            # Очищаем таблицу
            self.users_table.setRowCount(0)
            
            for user in users:
                row_position = self.users_table.rowCount()
                self.users_table.insertRow(row_position)
                
                # ID
                self.users_table.setItem(row_position, 0, QTableWidgetItem(str(user.user_id)))
                
                # Логин
                self.users_table.setItem(row_position, 1, QTableWidgetItem(user.login))
                
                # Роль
                # Получаем роль пользователя
                role = session.query(Role).filter(Role.role_id == user.role_id).first()
                role_name = role.role_name.value if role else "Неизвестно"
                self.users_table.setItem(row_position, 2, QTableWidgetItem(role_name))
                
                # Статус
                status = "Заблокирован" if user.is_blocked else "Активен"
                status_item = QTableWidgetItem(status)
                status_item.setForeground(Qt.GlobalColor.red if user.is_blocked else Qt.GlobalColor.green)
                self.users_table.setItem(row_position, 3, status_item)
                
                # Попытки входа
                self.users_table.setItem(row_position, 4, QTableWidgetItem(str(user.failed_attempts)))
        finally:
            session.close()
    
    def add_user(self):
        """Обработчик добавления нового пользователя."""
        dialog = UserDialog(self)
        
        if dialog.exec():
            data = dialog.get_form_data()
            
            # Валидация
            if not data['login']:
                QMessageBox.warning(self, "Ошибка", "Логин не может быть пустым.")
                return
            
            if not data.get('password'):
                QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым.")
                return
            
            # Создаем пользователя
            success, message, user_id = create_user(data['login'], data['password'], data['role_id'])
            
            if success:
                QMessageBox.information(self, "Успех", message)
                self.load_users()  # Обновляем список пользователей
                self.user_modified.emit()  # Сигнализируем об изменении
            else:
                QMessageBox.warning(self, "Ошибка", message)
    
    def edit_user(self):
        """Обработчик редактирования пользователя."""
        # Получаем выбранную строку
        selected_rows = self.users_table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для редактирования.")
            return
        
        # Получаем ID пользователя
        row = selected_rows[0].row()
        user_id = int(self.users_table.item(row, 0).text())
        
        # Открываем диалог редактирования
        dialog = UserDialog(self, user_id)
        
        if dialog.exec():
            data = dialog.get_form_data()
            
            print(f"[UI DEBUG] Данные для обновления: user_id={user_id}, login={data['login']}, "
                  f"role_id={data['role_id']}, is_blocked={data.get('is_blocked', False)}")
            
            # Обновляем пользователя
            success, message = update_user(
                user_id, 
                login=data['login'],  # Добавляем передачу логина
                role_id=data['role_id'], 
                is_blocked=data.get('is_blocked', False)
            )
            
            if success:
                QMessageBox.information(self, "Успех", "Данные пользователя обновлены.")
                self.load_users()  # Обновляем список пользователей
                self.user_modified.emit()  # Сигнализируем об изменении
            else:
                QMessageBox.warning(self, "Ошибка", message)
    
    def unblock_user(self):
        """Обработчик разблокировки пользователя."""
        # Получаем выбранную строку
        selected_rows = self.users_table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для разблокировки.")
            return
        
        # Получаем ID пользователя
        row = selected_rows[0].row()
        user_id = int(self.users_table.item(row, 0).text())
        
        # Проверяем статус пользователя
        status = self.users_table.item(row, 3).text()
        if status != "Заблокирован":
            QMessageBox.information(self, "Информация", "Пользователь не заблокирован.")
            return
        
        # Разблокируем пользователя
        success, message = unblock_user(user_id)
        
        if success:
            QMessageBox.information(self, "Успех", message)
            self.load_users()  # Обновляем список пользователей
            self.user_modified.emit()  # Сигнализируем об изменении
        else:
            QMessageBox.warning(self, "Ошибка", message)