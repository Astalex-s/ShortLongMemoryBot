"""
Модуль для хранения короткой памяти диалогов пользователей
"""
import logging
from typing import List, Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Класс для хранения истории диалогов пользователей"""
    
    def __init__(self, max_messages: int = 10):
        """
        Инициализация памяти диалогов
        
        Args:
            max_messages: Максимальное количество сообщений пользователя в истории (по умолчанию 10)
        """
        self.max_messages = max_messages
        # Хранилище истории: {user_id: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]}
        self.conversations: Dict[int, List[Dict[str, str]]] = defaultdict(list)
        logger.info(f"Инициализирована память диалогов с максимумом {max_messages} сообщений пользователя")
    
    def add_user_message(self, user_id: int, message: str) -> None:
        """
        Добавляет сообщение пользователя в историю
        
        Args:
            user_id: ID пользователя
            message: Текст сообщения
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            "role": "user",
            "content": message
        })
        
        logger.debug(f"Добавлено сообщение пользователя {user_id} в историю. Всего сообщений: {len(self.conversations[user_id])}")
    
    def add_assistant_message(self, user_id: int, message: str) -> None:
        """
        Добавляет ответ ассистента в историю
        
        Args:
            user_id: ID пользователя
            message: Текст ответа
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            "role": "assistant",
            "content": message
        })
        
        # Ограничиваем историю до max_messages сообщений пользователя
        self._limit_history(user_id)
        
        logger.debug(f"Добавлен ответ ассистента для пользователя {user_id} в историю")
    
    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """
        Получает историю диалога пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список сообщений в формате для OpenAI API
        """
        history = self.conversations.get(user_id, [])
        logger.debug(f"Получена история для пользователя {user_id}: {len(history)} сообщений")
        return history.copy()
    
    def clear_history(self, user_id: int) -> None:
        """
        Очищает историю диалога пользователя
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"История диалога пользователя {user_id} очищена")
    
    def _limit_history(self, user_id: int) -> None:
        """
        Ограничивает историю до max_messages сообщений пользователя
        
        Args:
            user_id: ID пользователя
        """
        if user_id not in self.conversations:
            return
        
        history = self.conversations[user_id]
        
        # Подсчитываем количество сообщений пользователя
        user_message_count = sum(1 for msg in history if msg["role"] == "user")
        
        # Если сообщений пользователя больше max_messages, удаляем старые пары
        if user_message_count > self.max_messages:
            # Удаляем пары (user, assistant) пока не останется max_messages сообщений пользователя
            while user_message_count > self.max_messages:
                # Удаляем первую пару сообщений
                if len(history) >= 2 and history[0]["role"] == "user" and history[1]["role"] == "assistant":
                    history.pop(0)  # Удаляем сообщение пользователя
                    history.pop(0)  # Удаляем ответ ассистента
                    user_message_count -= 1
                elif len(history) >= 1 and history[0]["role"] == "user":
                    # Если есть только сообщение пользователя без ответа
                    history.pop(0)
                    user_message_count -= 1
                else:
                    # Если структура неожиданная, очищаем историю
                    logger.warning(f"Неожиданная структура истории для пользователя {user_id}, очищаем")
                    history.clear()
                    break
            
            logger.info(
                f"История пользователя {user_id} ограничена до {self.max_messages} сообщений. "
                f"Удалено старых сообщений"
            )
    
    def get_stats(self) -> Dict[str, int]:
        """
        Получает статистику использования памяти
        
        Returns:
            Словарь со статистикой
        """
        total_users = len(self.conversations)
        total_messages = sum(len(history) for history in self.conversations.values())
        return {
            "total_users": total_users,
            "total_messages": total_messages
        }

