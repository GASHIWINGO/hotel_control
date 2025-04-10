"""
Модуль для работы с базой данных.
Обеспечивает подключение к PostgreSQL через SQLAlchemy ORM.
"""

import logging
import re
from contextlib import contextmanager
from typing import Optional, Tuple, Any

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from config import DATABASE_URL

# Настройка логирования
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Базовое исключение для ошибок базы данных."""
    pass


class ConnectionError(DatabaseError):
    """Исключение для ошибок соединения с БД."""
    pass


class QueryError(DatabaseError):
    """Исключение для ошибок выполнения запросов."""
    pass


class DatabaseManager:
    """
    Менеджер базы данных.
    Управляет подключением и сессиями базы данных.
    """
    
    def __init__(self, database_url: str):
        """
        Инициализирует менеджер базы данных.
        
        Args:
            database_url (str): URL подключения к базе данных
            
        Raises:
            ValueError: Если URL подключения некорректен
        """
        self.validate_database_url(database_url)
        self.database_url = database_url
        self._engine = None
        self._session_factory = None
        self._setup_engine()
    
    @staticmethod
    def validate_database_url(url: str) -> bool:
        """
        Проверяет корректность URL подключения к БД.
        
        Args:
            url (str): URL подключения
            
        Returns:
            bool: True, если URL корректен
            
        Raises:
            ValueError: Если URL некорректен
        """
        pattern = r'^postgresql(\+psycopg2)?://[^:]+:[^@]+@[^:]+:\d+/[^/]+'
        if not re.match(pattern, url):
            raise ValueError(f"Некорректный URL подключения к БД: {url}")
        return True
    
    def _setup_engine(self):
        """
        Настраивает engine SQLAlchemy с оптимальными параметрами.
        """
        try:
            self._engine = create_engine(
                self.database_url,
                echo=False,  # Отключаем логирование SQL-запросов в консоль
                pool_pre_ping=True,  # Проверка соединения перед использованием
                pool_recycle=3600,  # Переподключение через 1 час неактивности
                pool_size=5,  # Максимальное количество соединений в пуле
                max_overflow=10,  # Максимальное количество временных соединений
                pool_timeout=30,  # Таймаут получения соединения из пула (сек)
                connect_args={
                    "connect_timeout": 5,  # Таймаут соединения с БД (сек)
                    "application_name": "HotelControlSystem"  # Имя приложения в БД
                }
            )
            
            # Создаем фабрику сессий
            self._session_factory = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self._engine
                )
            )
            
            logger.info("Engine SQLAlchemy успешно настроен")
            
        except Exception as e:
            logger.error(f"Ошибка настройки engine SQLAlchemy: {e}")
            raise ConnectionError(f"Не удалось настроить подключение к БД: {e}")
    
    def get_session(self) -> Session:
        """
        Создает и возвращает новую сессию базы данных.
        
        Returns:
            Session: Объект сессии SQLAlchemy
            
        Raises:
            ConnectionError: При проблемах с созданием сессии
        """
        try:
            session = self._session_factory()
            return session
        except Exception as e:
            logger.error(f"Ошибка создания сессии БД: {e}")
            raise ConnectionError(f"Не удалось создать сессию БД: {e}")
    
    @contextmanager
    def session_scope(self):
        """
        Контекстный менеджер для работы с сессией базы данных.
        Автоматически закрывает сессию после использования.
        
        Yields:
            Session: Объект сессии SQLAlchemy
            
        Raises:
            QueryError: При ошибках выполнения операций с БД
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка в операции с БД: {e}")
            raise QueryError(f"Ошибка выполнения операции: {e}")
        finally:
            session.close()
    
    def check_connection(self) -> Tuple[bool, str]:
        """
        Проверяет подключение к базе данных.
        
        Returns:
            tuple: (успех, сообщение)
        """
        try:
            with self._engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                connection.commit()
            logger.info("Подключение к БД успешно проверено")
            return True, "Успешное подключение к базе данных"
            
        except OperationalError as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False, f"Ошибка подключения к БД: {e}"
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка SQLAlchemy: {e}")
            return False, f"Ошибка в работе с БД: {e}"
            
        except Exception as e:
            logger.error(f"Неожиданная ошибка при проверке подключения: {e}")
            return False, f"Непредвиденная ошибка: {e}"
    
    def execute_query(self, query: str, params: Optional[dict] = None, commit: bool = False) -> Any:
        """
        Выполняет SQL-запрос к базе данных.
        
        Args:
            query (str): SQL-запрос
            params (dict, optional): Параметры запроса
            commit (bool): Выполнить commit после запроса
            
        Returns:
            Any: Результат выполнения запроса
            
        Raises:
            QueryError: При ошибках выполнения запроса
        """
        with self.session_scope() as session:
            try:
                result = session.execute(text(query), params or {})
                if commit:
                    session.commit()
                return result
            except Exception as e:
                logger.error(f"Ошибка выполнения запроса: {e}")
                raise QueryError(f"Ошибка выполнения запроса: {e}")


# Создаем экземпляр менеджера БД
db_manager = DatabaseManager(DATABASE_URL)

# Создаем базовый класс для моделей
Base = declarative_base()

# Функции для обратной совместимости
def get_db_session() -> Session:
    """
    Получает сессию базы данных.
    
    Returns:
        Session: Объект сессии SQLAlchemy
    """
    return db_manager.get_session()

def check_db_connection() -> Tuple[bool, str]:
    """
    Проверяет подключение к базе данных.
    
    Returns:
        tuple: (успех, сообщение)
    """
    return db_manager.check_connection()


if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO)
    
    # Проверка подключения
    success, message = check_db_connection()
    print(f"Результат проверки подключения: {message}")
    
    if success:
        # Тестовый запрос
        try:
            with db_manager.session_scope() as session:
                result = session.execute(text("SELECT version()"))
                print(f"Версия PostgreSQL: {result.scalar()}")
        except DatabaseError as e:
            print(f"Ошибка при выполнении тестового запроса: {e}")