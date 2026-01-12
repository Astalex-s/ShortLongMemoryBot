"""
Модуль для работы с базой данных PostgreSQL
"""
import psycopg2
from psycopg2.extras import DictCursor
import logging
from config.settings import Settings

logger = logging.getLogger(__name__)


class DBManager:
    """Класс для управления подключением и запросами к PostgreSQL"""

    def __init__(self):
        self.conn_params = {
            "host": Settings.DB_HOST,
            "port": Settings.DB_PORT,
            "database": Settings.DB_NAME,
            "user": Settings.DB_USER,
            "password": Settings.DB_PASSWORD
        }
        self._init_db()

    def _get_connection(self):
        """Создает новое соединение с БД"""
        return psycopg2.connect(**self.conn_params)

    def _init_db(self):
        """Создает необходимые таблицы, если они не существуют"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Таблица сообщений
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS messages (
                            id SERIAL PRIMARY KEY,
                            user_id BIGINT NOT NULL,
                            role VARCHAR(20) NOT NULL,
                            content TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    # Таблица тезисов (Long-term context)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS theses (
                            user_id BIGINT PRIMARY KEY,
                            content TEXT NOT NULL,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                conn.commit()
            logger.info("База данных успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации БД: {e}")

    def save_message(self, user_id: int, role: str, content: str):
        """Сохраняет сообщение в БД"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s)",
                        (user_id, role, content)
                    )
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при сохранении сообщения: {e}")

    def get_user_messages_count(self, user_id: int) -> int:
        """Возвращает количество сообщений пользователя"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT COUNT(*) FROM messages WHERE user_id = %s AND role = 'user'",
                        (user_id,)
                    )
                    return cur.fetchone()[0]
        except Exception as e:
            logger.error(f"Ошибка при получении счетчика сообщений: {e}")
            return 0

    def get_recent_user_messages(self, user_id: int, limit: int = 3) -> list:
        """Возвращает последние N сообщений пользователя"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT content FROM messages WHERE user_id = %s AND role = 'user' ORDER BY id DESC LIMIT %s",
                        (user_id, limit)
                    )
                    rows = cur.fetchall()
                    return [row[0] for row in reversed(rows)]
        except Exception as e:
            logger.error(f"Ошибка при получении последних сообщений: {e}")
            return []

    def save_thesis(self, user_id: int, new_thesis: str):
        """Обновляет или создает тезисы для пользователя (накопительно)"""
        try:
            current_theses = self.get_theses(user_id)
            combined_content = f"{current_theses}\n{new_thesis}".strip() if current_theses else new_thesis
            
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO theses (user_id, content, updated_at) 
                        VALUES (%s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (user_id) DO UPDATE 
                        SET content = EXCLUDED.content, updated_at = CURRENT_TIMESTAMP;
                    """, (user_id, combined_content))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при сохранении тезисов: {e}")

    def get_theses(self, user_id: int) -> str:
        """Возвращает накопленные тезисы пользователя"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT content FROM theses WHERE user_id = %s", (user_id,))
                    row = cur.fetchone()
                    return row[0] if row else ""
        except Exception as e:
            logger.error(f"Ошибка при получении тезисов: {e}")
            return ""

    def clear_all_history(self, user_id: int):
        """Полная очистка истории в БД"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM messages WHERE user_id = %s", (user_id,))
                    cur.execute("DELETE FROM theses WHERE user_id = %s", (user_id,))
                conn.commit()
            logger.info(f"Вся история в БД для пользователя {user_id} удалена")
        except Exception as e:
            logger.error(f"Ошибка при очистке истории в БД: {e}")
