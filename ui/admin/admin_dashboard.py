"""
Модуль панели управления администратора.
Предоставляет интерфейс для управления системой и пользователями.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QMessageBox, QStatusBar, QProgressBar, 
    QShortcut, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QIcon

from ui.admin.user_management_widget import UserManagementWidget
import logging

# Настройка логирования
logger = logging.getLogger(__name__)


class HeaderWidget(QFrame):
    """
    Виджет заголовка панели администратора.
    
    Отображает заголовок и информацию о текущем пользователе.
    """
    refresh_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setup_ui()
    
    def setup_ui(self):
        """Настраивает интерфейс заголовка."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Заголовок
        title = QLabel("Панель управления администратора")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        # Информация о пользователе
        self.user_info_label = QLabel()
        self.user_info_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Кнопка обновления
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setToolTip("Обновить данные (F5)")
        self.refresh_button.clicked.connect(self.refresh_clicked.emit)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.user_info_label)
        layout.addWidget(self.refresh_button)
    
    def set_user_info(self, user_data):
        """Устанавливает информацию о пользователе."""
        if user_data and isinstance(user_data, dict):
            login = user_data.get('login', 'Неизвестно')
            role = user_data.get('role', 'Неизвестно')
            self.user_info_label.setText(f"Пользователь: {login} | Роль: {role}")


class StatusBarManager(QStatusBar):
    """
    Менеджер статусной строки.
    
    Управляет отображением сообщений и индикацией прогресса.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Индикатор прогресса
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Бесконечный прогресс
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(150)
        
        # Добавляем индикатор в правую часть статусной строки
        self.addPermanentWidget(self.progress_bar)
    
    def show_message(self, message, timeout=5000):
        """Показывает сообщение в статусной строке."""
        self.showMessage(message, timeout)
    
    def show_loading(self, is_loading=True, message=None):
        """Показывает/скрывает индикатор загрузки."""
        self.progress_bar.setVisible(is_loading)
        if message and is_loading:
            self.showMessage(message)
        elif not is_loading:
            self.clearMessage()


class AdminDashboard(QWidget):
    """
    Панель управления администратора системы.
    
    Предоставляет интерфейс для управления пользователями и 
    доступа к системной информации через табличное представление.
    
    Attributes:
        main_window: Главное окно приложения
        user_data: Данные авторизованного администратора
    """
    def __init__(self, main_window):
        """
        Инициализирует панель управления администратора.
        
        Args:
            main_window: Главное окно приложения
        """
        super().__init__()
        self.main_window = main_window
        self.user_data = None
        
        # Установка минимального размера
        self.setMinimumSize(800, 600)
        
        # Инициализация интерфейса
        self.setup_ui()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс панели администратора."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок
        self.header = HeaderWidget()
        self.header.refresh_clicked.connect(self.refresh_data)
        layout.addWidget(self.header)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # Вкладка управления пользователями
        self.user_management = UserManagementWidget()
        self.user_management.user_modified.connect(self.on_user_modified)
        self.tab_widget.addTab(self.user_management, "Пользователи")
        
        # Вкладка с информацией о других модулях
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_label = QLabel("Другие модули управления находятся в разработке")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(info_label)
        self.tab_widget.addTab(info_widget, "Информация")
        
        layout.addWidget(self.tab_widget)
        
        # Статусная строка
        self.status_bar = StatusBarManager()
        layout.addWidget(self.status_bar)
        
        # Настройка порядка перехода фокуса по табуляции
        self.setTabOrder(self.header.refresh_button, self.tab_widget)
        self.setTabOrder(self.tab_widget, self.user_management)
    
    def setup_shortcuts(self):
        """Настраивает горячие клавиши."""
        # Обновление данных по F5
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.refresh_data)
        
        # Переключение между вкладками Ctrl+1, Ctrl+2
        for i in range(1, min(10, self.tab_widget.count() + 1)):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i}"), self)
            shortcut.activated.connect(lambda idx=i-1: self.tab_widget.setCurrentIndex(idx))
    
    def setup(self, user_data):
        """
        Настраивает панель управления с данными пользователя.
        
        Args:
            user_data: Словарь с данными пользователя
        """
        try:
            # Валидация данных пользователя
            self.validate_user_data(user_data)
            
            # Устанавливаем данные
            self.user_data = user_data
            
            # Обновляем интерфейс
            self.header.set_user_info(user_data)
            self.refresh_data()
            
            # Показываем уведомление
            self.status_bar.show_message("Панель управления администратора успешно загружена")
            
            logger.info(f"Администратор {user_data.get('login')} вошел в систему")
            
        except ValueError as e:
            logger.error(f"Ошибка при настройке панели администратора: {e}")
            QMessageBox.critical(
                self, 
                "Ошибка инициализации", 
                f"Не удалось загрузить панель: {str(e)}"
            )
            
            # Возврат к экрану входа
            if self.main_window:
                self.main_window.show_login()
    
    def validate_user_data(self, user_data):
        """
        Проверяет корректность данных пользователя.
        
        Args:
            user_data: Словарь с данными пользователя
            
        Raises:
            ValueError: Если данные некорректны
        """
        if not user_data or not isinstance(user_data, dict):
            raise ValueError("Некорректный формат данных пользователя")
        
        # Проверка обязательных полей
        required_fields = ['user_id', 'login', 'role']
        missing_fields = [field for field in required_fields if field not in user_data]
        
        if missing_fields:
            raise ValueError(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")
        
        # Проверка роли
        if user_data.get('role') != 'Administrator':
            raise ValueError("Недостаточно прав для доступа к панели администратора")
    
    def refresh_data(self):
        """Обновляет данные во всех активных виджетах."""
        try:
            # Показываем индикатор загрузки
            self.status_bar.show_loading(True, "Обновление данных...")
            
            # Обновляем данные в текущей вкладке
            current_tab = self.tab_widget.currentWidget()
            
            if current_tab == self.user_management:
                self.user_management.load_users()
            
            # Скрываем индикатор и показываем сообщение об успехе
            self.status_bar.show_loading(False)
            self.status_bar.show_message("Данные успешно обновлены")
            
        except Exception as e:
            # Логируем ошибку
            logger.error(f"Ошибка обновления данных: {e}")
            
            # Скрываем индикатор и показываем сообщение об ошибке
            self.status_bar.show_loading(False)
            self.status_bar.show_message("Ошибка обновления данных")
            
            # Показываем диалог с ошибкой
            QMessageBox.warning(
                self, 
                "Ошибка обновления", 
                f"Не удалось обновить данные: {str(e)}"
            )
    
    def on_user_modified(self):
        """Обработчик изменения данных пользователей."""
        self.status_bar.show_message("Данные пользователей успешно обновлены")
        logger.info("Данные пользователей изменены")