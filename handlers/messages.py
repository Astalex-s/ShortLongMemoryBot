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
from utils.db_manager import DBManager

logger = logging.getLogger(__name__)

# Инициализируем AI клиент
ai_client = AIClient()

# Инициализируем менеджер БД
db_manager = DBManager()


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
        
        # Отправляем индикатор печати
        try:
            bot.send_chat_action(chat_id, 'typing')
        except Exception as e:
            logger.warning(f"Не удалось отправить индикатор печати: {e}")
        
        try:
            # 1. Сохраняем сообщение пользователя в БД
            db_manager.save_message(user_id, 'user', user_message)

            # 2. Загружаем накопленные тезисы (Long-term context)
            system_context = db_manager.get_theses(user_id)

            # 3. Получаем короткую историю (Short-term context)
            history = memory.get_history(user_id)
            
            # 4. Получаем ответ от AI с учетом тезисов и истории
            ai_response = ai_client.get_response(user_message, history=history, system_context=system_context)
            
            if not ai_response:
                ai_response = Messages.ERROR_AI_RESPONSE
            
            # 5. Сохраняем ответ в оперативную память и в БД
            memory.add_user_message(user_id, user_message)
            memory.add_assistant_message(user_id, ai_response)
            db_manager.save_message(user_id, 'assistant', ai_response)
            
            # 6. Проверяем, нужно ли обновить тезисы (каждые 3 сообщения пользователя)
            user_msg_count = db_manager.get_user_messages_count(user_id)
            if user_msg_count > 0 and user_msg_count % 3 == 0:
                logger.info(f"Запуск генерации тезисов для пользователя {user_id}...")
                recent_msgs = db_manager.get_recent_user_messages(user_id, 3)
                new_theses = ai_client.generate_theses(recent_msgs)
                if new_theses:
                    db_manager.save_thesis(user_id, new_theses)
                    logger.info(f"Тезисы успешно обновлены для {user_id}")

            # 7. Отправляем ответ пользователю
            bot.reply_to(message, ai_response)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Ответ отправлен за {elapsed_time:.2f}с")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Ошибка при обработке сообщения: {e}")
            bot.reply_to(message, Messages.ERROR_GENERAL)

