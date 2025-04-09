from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ManagerDashboard(QWidget):
    """Панель управления для менеджера."""
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        """Настраивает интерфейс панели управления"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("Панель управления менеджера")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Информационное сообщение
        info = QLabel("Панель управления для менеджера находится в разработке.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        # Кнопка выхода
        logout_button = QPushButton("Выйти из системы")
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)
        
        layout.addStretch()
    
    def setup(self, user_data):
        """Настраивает панель с учетом данных пользователя"""
        self.user_data = user_data
    
    def logout(self):
        """Обрабатывает выход из системы"""
        if self.main_window:
            self.main_window.show_login() 