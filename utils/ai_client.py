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
    
    def get_response(self, user_message: str, history: list = None, system_context: str = None) -> str:
        """
        Получает ответ от OpenAI через ProxyAPI
        
        Args:
            user_message: Сообщение пользователя
            history: История предыдущих сообщений в формате [{"role": "user", "content": "..."}, ...]
            system_context: Долгосрочный контекст (тезисы) для добавления в системный промпт
            
        Returns:
            Ответ от AI модели
        """
        start_time = time.time()
        
        # Формируем список сообщений для API
        messages = []
        
        # Добавляем системный контекст (тезисы), если есть
        if system_context:
            messages.append({
                "role": "system",
                "content": f"Контекст предыдущих разговоров с пользователем:\n{system_context}"
            })
        
        # Добавляем короткую историю
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
    
    def generate_theses(self, messages: list) -> str:
        """
        Генерирует тезисы из последних сообщений пользователя для долгосрочной памяти
        
        Args:
            messages: Список последних сообщений пользователя
            
        Returns:
            Тезисы в виде текста
        """
        if not messages:
            return ""
        
        start_time = time.time()
        
        try:
            # Формируем запрос для генерации тезисов
            messages_text = "\n".join([f"- {msg}" for msg in messages])
            prompt = f"""Проанализируй следующие сообщения пользователя и создай краткие тезисы (2-3 предложения), 
отражающие главные темы, интересы и важную информацию:

{messages_text}

Тезисы должны быть:
- Краткими и информативными
- Без лишних деталей
- Сфокусированными на ключевых моментах
- В формате списка через точку с запятой

Ответ дай ТОЛЬКО в виде тезисов, без дополнительного текста."""

            logger.debug(f"Генерация тезисов для {len(messages)} сообщений")
            
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            elapsed_time = time.time() - start_time
            theses = chat_completion.choices[0].message.content
            
            logger.info(
                f"Тезисы сгенерированы за {elapsed_time:.2f}с. "
                f"Длина: {len(theses)} символов"
            )
            logger.debug(f"Сгенерированные тезисы: {theses}")
            
            return theses if theses else ""
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_traceback = traceback.format_exc()
            logger.error(
                f"Ошибка при генерации тезисов (время выполнения: {elapsed_time:.2f}с): {e}\n"
                f"Traceback:\n{error_traceback}"
            )
            return ""

