from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel,
    QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction

from ui.admin.admin_dashboard import AdminDashboard
from ui.manager.manager_dashboard import ManagerDashboard

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления отелем")
        self.setMinimumSize(1200, 800)
        
        # Создаем центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Создаем главный
        self.layout = QVBoxLayout(self.central_widget)
        
        # Создаем стек виджетов для разных экранов
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)
        
        # Импортируем LoginWindow здесь
        from ui.login_window import LoginWindow
        
        # Создаем экраны
        self.login_window = LoginWindow(self)
        self.admin_dashboard = AdminDashboard(self)
        self.manager_dashboard = ManagerDashboard(self)
        
        # Добавляем экраны в стек
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.admin_dashboard)
        self.stacked_widget.addWidget(self.manager_dashboard)
        
        # Создаем меню
        self.create_menu()
        
        # Показываем окно входа
        self.show_login()
    
    def create_menu(self):
        """Создает главное меню приложения"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        logout_action = QAction("Выйти", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_login(self):
        """Показывает окно входа"""
        self.stacked_widget.setCurrentWidget(self.login_window)
    
    def show_dashboard(self, user_data):
        """Показывает соответствующую панель управления"""
        role = user_data.get('role')
        
        if role == 'Administrator':
            self.admin_dashboard.setup(user_data)
            self.stacked_widget.setCurrentWidget(self.admin_dashboard)
        elif role == 'Manager':
            self.manager_dashboard.setup(user_data)
            self.stacked_widget.setCurrentWidget(self.manager_dashboard)
        elif role == 'Staff' or role == 'Guest':
            QMessageBox.information(
                self,
                "Информация",
                f"Интерфейс для роли '{role}' в настоящее время находится в разработке."
            )
            self.show_login()
        else:
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Неизвестная роль пользователя: {role}"
            )
            self.show_login()
    
    def logout(self):
        """Обрабатывает выход из системы"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.show_login()
    
    def show_about(self):
        """Показывает информацию о программе"""
        QMessageBox.about(
            self,
            "О программе",
            "Система управления отелем\n"
            "Версия 1.0\n\n"
            "© 2025 Все права защищены"
        )