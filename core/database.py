from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DATABASE_URL

# Создаем engine SQLAlchemy для подключения к базе
engine = create_engine(
    DATABASE_URL,
    echo=False,  
    pool_pre_ping=True,  
    pool_recycle=3600  # Переподключение через 1 час неактивности
)

# Создаем фабрику сессий
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем thread-local session для безопасного использования в многопоточном окружении
SessionLocal = scoped_session(SessionFactory)

# Импортируем базовый класс модели, чтобы он был доступен отсюда
from core.models import Base

# Функция для получения сессии базы данных
def get_db_session():

    session = SessionLocal()
    return session

# Функция для проверки подключения к БД
def check_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.commit()
        return True, "Успешное подключение к базе данных"
    except Exception as e:
        return False, f"Ошибка подключения к базе данных: {str(e)}"

if __name__ == "__main__":
    connected, message = check_db_connection()
    print(message)
    
    if connected:
        session = get_db_session()
        try:
            from models import User, Role
            users = session.query(User).all()
            print(f"Получено {len(users)} пользователей:")
            for user in users:
                print(f"  - {user}")
        finally:
            session.close()
