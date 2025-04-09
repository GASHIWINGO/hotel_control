import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QSpacerItem,
    QSizePolicy, QFrame, QInputDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from core.auth import authenticate_user, is_first_login, hash_password
from core.database import get_db_session
from core.models import User
from ui.change_password_dialog import ChangePasswordDialog
from config import APP_NAME, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT

class LoginWindow(QMainWindow):
    """Окно для входа в систему."""
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        """Настраивает интерфейс окна входа"""
        self.setWindowTitle(f"{APP_NAME} - Вход в систему")
        self.setMinimumSize(400, 250)
        
        # Создание центрального виджета и основного лейаута
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("Система управления отелем")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Подзаголовок
        subtitle = QLabel("Вход в систему")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Форма входа
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Логин
        login_layout = QHBoxLayout()
        login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_input)
        form_layout.addLayout(login_layout)
        
        # Пароль
        password_layout = QHBoxLayout()
        password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)
        
        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)
        
        layout.addWidget(form_frame)
        
        # Кнопка сброса пароля
        reset_button = QPushButton("Забыли пароль?")
        reset_button.setFlat(True)
        reset_button.clicked.connect(self.handle_password_reset)
        layout.addWidget(reset_button)
        
        # Устанавливаем последовательность Tab
        self.setTabOrder(self.login_input, self.password_input)
        self.setTabOrder(self.password_input, self.login_button)
        
        # Устанавливаем фокус на поле логина при открытии окна
        self.login_input.setFocus()
        
        # Привязываем нажатие Enter в полях к функции login
        self.login_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
    
    def handle_login(self):
        """Обрабатывает попытку входа"""
        login = self.login_input.text().strip()
        password = self.password_input.text()
        
        if not login or not password:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пожалуйста, заполните все поля"
            )
            return
        
        # Отключаем кнопку входа
        self.login_button.setEnabled(False)
        self.login_button.setText("Вход...")
        
        # Пытаемся войти
        try:
            success, message, user_data = authenticate_user(login, password)
            
            if success:
                # Проверяем, первый ли это вход пользователя
                is_first_login = user_data.get('is_first_login', False)
                print(f"Информация о первом входе из данных пользователя: {is_first_login}")
                
                if is_first_login:
                    user_id = user_data.get('user_id')
                    # Показываем диалог смены пароля
                    change_dialog = ChangePasswordDialog(user_id, password, self)
                    if change_dialog.exec():
                        # Если пароль успешно изменен, показываем сообщение и панель управления
                        QMessageBox.information(
                            self,
                            "Успешная авторизация",
                            "Вы успешно авторизовались"
                        )
                        if self.main_window:
                            self.main_window.show_dashboard(user_data)
                    else:
                        # Если пароль не изменен, возвращаемся на экран входа
                        QMessageBox.warning(
                            self,
                            "Внимание",
                            "Для продолжения работы необходимо изменить пароль."
                        )
                else:
                    # Показываем сообщение об успешной авторизации
                    QMessageBox.information(
                        self,
                        "Успешная авторизация",
                        "Вы успешно авторизовались"
                    )
                    # Показываем соответствующую панель управления
                    if self.main_window:
                        self.main_window.show_dashboard(user_data)
            else:
                if "заблокирован" in message.lower():
                    QMessageBox.warning(
                        self,
                        "Ошибка входа",
                        "Вы заблокированы. Обратитесь к администратору."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Ошибка входа",
                        "Вы ввели неверный логин или пароль. Пожалуйста проверьте ещё раз введенные данные."
                    )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Критическая ошибка",
                f"Произошла ошибка при попытке входа: {str(e)}"
            )
        
        # Включаем кнопку входа обратно
        self.login_button.setEnabled(True)
        self.login_button.setText("Войти")
    
    def handle_password_reset(self):
        """Обрабатывает запрос на сброс пароля"""
        login, ok = QInputDialog.getText(
            self,
            "Сброс пароля",
            "Введите логин для сброса пароля:"
        )
        
        if ok and login:
            # Проверяем существование пользователя
            session = get_db_session()
            try:
                user = session.query(User).filter(User.login == login).first()
                if not user:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Пользователь с таким логином не найден."
                    )
                    return
                
                # Сбрасываем пароль на временный
                temp_password = "Temp123!"
                
                # Хэшируем временный пароль и сохраняем его
                hashed_password = hash_password(temp_password)
                user.password_hash = hashed_password
                
                # Сбрасываем счетчик попыток и снимаем блокировку
                user.failed_attempts = 0
                user.is_blocked = False
                
                # Для принудительной смены пароля при следующем входе
                user.last_login = None
                
                session.commit()
                
                QMessageBox.information(
                    self,
                    "Сброс пароля",
                    f"Пароль сброшен. Временный пароль: {temp_password}\n"
                    "При следующем входе вам будет предложено изменить пароль."
                )
                
                # Заполняем поля логина и пароля для удобства пользователя
                self.login_input.setText(login)
                self.password_input.setText(temp_password)
                
            except Exception as e:
                session.rollback()
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось сбросить пароль: {str(e)}"
                )
            finally:
                session.close()
        elif ok:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Логин не может быть пустым."
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())