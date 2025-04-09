import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow
from core.database import check_db_connection
from config import APP_NAME

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Проверяем подключение к базе данных при запуске
    connected, message = check_db_connection()
    
    if not connected:
        QMessageBox.critical(None, f"{APP_NAME} - Ошибка", 
                            f"Не удалось подключиться к базе данных.\n\n{message}")
        sys.exit(1)
    
    # Запускаем главное окно
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec())