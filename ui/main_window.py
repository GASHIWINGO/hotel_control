"""
Главное окно приложения Hotel Control System.
Управляет основными экранами и обеспечивает навигацию между ними.
"""

import logging
from typing import Optional, Dict

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget,
    QMessageBox, QStatusBar, QMenuBar, QShortcut
)
from PyQt6.QtCore import Qt, QSettings, QSize, QPoint
from PyQt6.QtGui import QIcon, QAction, QKeySequence

from ui.admin.admin_dashboard import AdminDashboard
from ui.manager.manager_dashboard import ManagerDashboard
from ui.login_window import LoginWindow

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 800
COMPANY_NAME = "HotelSystem"
APP_NAME = "Система управления отелем"
APP_VERSION = "1.0"


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    
    Управляет отображением различных экранов (логин, панели администратора
    и менеджера) и обеспечивает навигацию между ними.
    """
    
    def __init__(self):
        """Инициализирует главное окно приложения."""
        super().__init__()
        
        # Инициализация настроек
        self.settings = QSettings(COMPANY_NAME, 'MainWindow')
        
        # Инициализация UI
        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()
        self.setup_statusbar()
        
        # Восстановление состояния окна
        self.restore_window_state()
        
        logger.info("Главное окно инициализировано")
    
    def setup_ui(self):
        """Настраивает основные элементы интерфейса."""
        try:
            # Основные параметры окна
            self.setWindowTitle(APP_NAME)
            self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
            
            # Центральный виджет
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            
            # Основной layout
            self.layout = QVBoxLayout(self.central_widget)
            self.layout.setContentsMargins(0, 0, 0, 0)
            
            # Стек виджетов для разных экранов
            self.stacked_widget = QStackedWidget()
            self.layout.addWidget(self.stacked_widget)
            
            # Инициализация экранов
            self.initialize_screens()
            
            logger.debug("Интерфейс успешно настроен")
            
        except Exception as e:
            logger.error(f"Ошибка при настройке интерфейса: {e}")
            self.show_error("Ошибка инициализации", 
                          "Не удалось настроить интерфейс приложения")
    
    def initialize_screens(self):
        """Инициализирует все экраны приложения."""
        try:
            # Создаем экраны
            self.login_screen = LoginWindow(self)
            self.admin_dashboard = AdminDashboard(self)
            self.manager_dashboard = ManagerDashboard(self)
            
            # Добавляем экраны в стек
            self.stacked_widget.addWidget(self.login_screen)
            self.stacked_widget.addWidget(self.admin_dashboard)
            self.stacked_widget.addWidget(self.manager_dashboard)
            
            # Показываем экран входа по умолчанию
            self.show_login()
            
            logger.debug("Экраны успешно инициализированы")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации экранов: {e}")
            self.show_error("Ошибка инициализации", 
                          "Не удалось инициализировать экраны приложения")
    
    def setup_menu(self):
        """Создает главное меню приложения."""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        logout_action = QAction("Выйти из аккаунта", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")
        
        about_action = QAction("О программе", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_shortcuts(self):
        """Настраивает горячие клавиши."""
        shortcuts = {
            "F5": self.refresh_current_screen,
            "Ctrl+L": self.logout,
            "Ctrl+Q": self.close,
            "F1": self.show_about
        }
        
        for key, callback in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(callback)
    
    def setup_statusbar(self):
        """Настраивает строку состояния."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def show_status_message(self, message: str, timeout: int = 3000):
        """
        Показывает сообщение в строке состояния.
        
        Args:
            message: Текст сообщения
            timeout: Время отображения в миллисекундах
        """
        self.status_bar.showMessage(message, timeout)
    
    def show_dashboard(self, user_data: Dict):
        """
        Показывает соответствующую панель управления.
        
        Args:
            user_data: Словарь с данными пользователя
        """
        try:
            if not isinstance(user_data, dict):
                raise ValueError("Некорректный формат данных пользователя")
            
            role = user_data.get('role')
            if not role:
                raise ValueError("Роль пользователя не указана")
            
            self.show_status_message(f"Загрузка панели для роли: {role}")
            
            if role == 'Administrator':
                self.admin_dashboard.setup(user_data)
                self.stacked_widget.setCurrentWidget(self.admin_dashboard)
                logger.info(f"Загружена панель администратора для {user_data['login']}")
            
            elif role == 'Manager':
                self.manager_dashboard.setup(user_data)
                self.stacked_widget.setCurrentWidget(self.manager_dashboard)
                logger.info(f"Загружена панель менеджера для {user_data['login']}")
            
            else:
                logger.warning(f"Попытка входа с неизвестной ролью: {role}")
                self.show_error("Ошибка доступа", 
                              f"Неизвестная роль пользователя: {role}")
                self.show_login()
            
            self.show_status_message("Панель управления загружена")
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке панели управления: {e}")
            self.show_error("Ошибка", str(e))
            self.show_login()
    
    def show_login(self):
        """Показывает экран входа."""
        self.stacked_widget.setCurrentWidget(self.login_screen)
        self.show_status_message("Экран входа")
        logger.debug("Отображен экран входа")
    
    def logout(self):
        """Обрабатывает выход из системы."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Пользователь вышел из системы")
            self.show_login()
    
    def refresh_current_screen(self):
        """Обновляет текущий экран."""
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
    
    def show_about(self):
        """Показывает информацию о программе."""
        QMessageBox.about(
            self,
            "О программе",
            f"{APP_NAME}\n"
            f"Версия {APP_VERSION}\n\n"
            f"© 2024 {COMPANY_NAME}\n"
            "Все права защищены"
        )
    
    def show_error(self, title: str, message: str):
        """
        Показывает сообщение об ошибке.
        
        Args:
            title: Заголовок сообщения
            message: Текст сообщения
        """
        QMessageBox.critical(self, title, message)
        logger.error(f"Ошибка: {title} - {message}")
    
    def restore_window_state(self):
        """Восстанавливает состояние и геометрию окна."""
        geometry = self.settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value('windowState')
        if state:
            self.restoreState(state)
    
    def save_window_state(self):
        """Сохраняет состояние и геометрию окна."""
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('windowState', self.saveState())
    
    def closeEvent(self, event):
        """
        Обрабатывает событие закрытия окна.
        Сохраняет состояние окна перед закрытием.
        """
        self.save_window_state()
        logger.info("Приложение закрыто")
        super().closeEvent(event)
    
    def cleanup_screens(self):
        """Освобождает ресурсы неиспользуемых экранов."""
        current_widget = self.stacked_widget.currentWidget()
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            if widget != current_widget:
                widget.hide()