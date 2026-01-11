"""
Модуль для работы с OpenAI API через ProxyAPI
"""
import time
import traceback
import logging
from openai import OpenAI
from config.settings import Settings

logger = logging.getLogger(__name__)


class AIClient:
    """Класс для работы с OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI"""
        self.client = OpenAI(
            api_key=Settings.OPENAI_API_KEY,
            base_url=Settings.OPENAI_BASE_URL,
        )
        self.model = Settings.AI_MODEL
    
    def get_response(self, user_message: str, history: list = None) -> str:
        """
        Получает ответ от OpenAI через ProxyAPI
        
        Args:
            user_message: Сообщение пользователя
            history: История предыдущих сообщений в формате [{"role": "user", "content": "..."}, ...]
            
        Returns:
            Ответ от AI модели
        """
        start_time = time.time()
        
        # Формируем список сообщений для API
        messages = []
        if history:
            messages.extend(history)
        
        # Добавляем текущее сообщение пользователя
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            logger.debug(
                f"Отправка запроса к OpenAI API. "
                f"Длина сообщения: {len(user_message)} символов. "
                f"История: {len(history) if history else 0} сообщений"
            )
            
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            elapsed_time = time.time() - start_time
            
            # Извлекаем ответ из completion
            response = chat_completion.choices[0].message.content
            
            # Логируем информацию о запросе
            response_preview = response[:100] + "..." if len(response) > 100 else response
            logger.info(
                f"Получен ответ от OpenAI API за {elapsed_time:.2f}с. "
                f"Длина ответа: {len(response)} символов. "
                f"Превью: {response_preview}"
            )
            logger.debug(f"Полный ответ от API: {response}")
            
            return response if response else None
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_traceback = traceback.format_exc()
            logger.error(
                f"Ошибка при запросе к OpenAI API (время выполнения: {elapsed_time:.2f}с): {e}\n"
                f"Traceback:\n{error_traceback}"
            )
            raise

