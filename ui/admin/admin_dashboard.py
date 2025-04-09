from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.admin.user_management_widget import UserManagementWidget

class AdminDashboard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        """Настраивает интерфейс панели администратора"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        header_layout = QHBoxLayout()
        title = QLabel("Панель управления администратора")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        
        # Управление пользователями
        self.user_management = UserManagementWidget()
        self.tab_widget.addTab(self.user_management, "Пользователи")
        
        # Уведомление о будущих функциях
        info_layout = QVBoxLayout()
        info_label = QLabel("Другие модули управления находятся в разработке")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(info_label)
        
        info_widget = QWidget()
        info_widget.setLayout(info_layout)
        
        self.tab_widget.addTab(info_widget, "Информация")
        
        layout.addWidget(self.tab_widget)
    
    def setup(self, user_data):
        """Настраивает панель управления с данными пользователя"""
        self.user_data = user_data