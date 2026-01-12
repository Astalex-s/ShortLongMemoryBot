"""
Модуль настроек приложения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class Settings:
    """Класс для хранения настроек приложения"""
    
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # OpenAI API Key для ProxyAPI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # OpenAI API Base URL
    OPENAI_BASE_URL = "https://openai.api.proxyapi.ru/v1"
    
    # Модель для использования
    AI_MODEL = "gpt-4.1-mini-2025-04-14"
    
    # Настройки логирования
    LOG_DIR = "logs"
    
    # Настройки памяти диалогов
    MAX_MESSAGES_HISTORY = 10  # Максимальное количество сообщений пользователя в истории
    
    # Настройки PostgreSQL
    DB_HOST = os.getenv('DB_HOST') or '85.198.96.156'
    DB_PORT = os.getenv('DB_PORT') or '5432'
    DB_NAME = os.getenv('DB_NAME') or 'memorybot'
    DB_USER = os.getenv('DB_USER') or 'postgres'
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    @classmethod
    def validate(cls):
        """
        Проверяет наличие необходимых переменных окружения
        
        Raises:
            ValueError: Если отсутствуют обязательные переменные
        """
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY не установлен в переменных окружения")
        if not cls.DB_HOST:
            raise ValueError("DB_HOST не установлен")
        if not cls.DB_PASSWORD:
            raise ValueError("DB_PASSWORD не установлен")

