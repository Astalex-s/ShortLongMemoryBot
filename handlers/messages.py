"""
Обработчики текстовых сообщений бота
"""
import time
import traceback
import logging
from telebot import TeleBot
from utils.ai_client import AIClient
from utils.messages import Messages
from utils.memory_manager import memory

logger = logging.getLogger(__name__)

# Инициализируем AI клиент
ai_client = AIClient()


def register_message_handlers(bot: TeleBot):
    """
    Регистрирует обработчики текстовых сообщений
    
    Args:
        bot: Экземпляр TeleBot
    """
    
    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        """Обработчик всех текстовых сообщений"""
        start_time = time.time()
        
        user = message.from_user
        user_id = user.id
        user_info = f"ID: {user_id}, Username: @{user.username or 'N/A'}, Имя: {user.first_name or 'N/A'}"
        user_message = message.text
        chat_id = message.chat.id
        
        logger.info(
            f"Получено сообщение от пользователя {user_info}. "
            f"Chat ID: {chat_id}, Длина сообщения: {len(user_message)} символов"
        )
        logger.debug(f"Текст сообщения: {user_message}")
        
        # Отправляем индикатор печати
        try:
            bot.send_chat_action(chat_id, 'typing')
            logger.debug(f"Индикатор печати отправлен в чат {chat_id}")
        except Exception as e:
            logger.warning(f"Не удалось отправить индикатор печати: {e}")
        
        try:
            # Получаем историю диалога пользователя
            history = memory.get_history(user_id)
            
            # Получаем ответ от AI с учетом истории
            ai_response = ai_client.get_response(user_message, history=history)
            
            if not ai_response:
                ai_response = Messages.ERROR_AI_RESPONSE
            
            # Сохраняем сообщение пользователя и ответ в память
            memory.add_user_message(user_id, user_message)
            memory.add_assistant_message(user_id, ai_response)
            
            # Отправляем ответ пользователю
            bot.reply_to(message, ai_response)
            
            elapsed_time = time.time() - start_time
            logger.info(
                f"Ответ успешно отправлен пользователю {user_id}. "
                f"Общее время обработки: {elapsed_time:.2f}с"
            )
            logger.debug(f"Текст ответа пользователю {user_id}: {ai_response[:200]}...")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_traceback = traceback.format_exc()
            logger.error(
                f"Ошибка при обработке сообщения от пользователя {user_id} "
                f"(время обработки: {elapsed_time:.2f}с): {e}\n"
                f"Traceback:\n{error_traceback}"
            )
            
            try:
                bot.reply_to(message, Messages.ERROR_GENERAL)
            except Exception as send_error:
                logger.error(f"Не удалось отправить сообщение об ошибке пользователю: {send_error}")

