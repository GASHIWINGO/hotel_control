import os

# Настройки подключения к БД
DB_HOST = os.getenv('DB_HOST', '185.121.134.33')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'hotel')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123')

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Настройки приложения
APP_NAME = "Hotel Control System"
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600