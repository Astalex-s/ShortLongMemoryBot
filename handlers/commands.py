"""
Обработчики команд бота
"""
import logging
from telebot import TeleBot
from utils.messages import Messages
from utils.memory_manager import memory
from utils.db_manager import DBManager

logger = logging.getLogger(__name__)

# Инициализируем менеджер БД
db_manager = DBManager()


def register_command_handlers(bot: TeleBot):
    """
    Регистрирует обработчики команд
    
    Args:
        bot: Экземпляр TeleBot
    """
    
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        """Обработчик команды /start"""
        user = message.from_user
        user_info = f"ID: {user.id}, Username: @{user.username or 'N/A'}, Имя: {user.first_name or 'N/A'}"
        
        logger.info(f"Команда /start от пользователя {user_info}")
        
        bot.reply_to(message, Messages.WELCOME)
        
        logger.debug(f"Приветственное сообщение отправлено пользователю {user.id}")
    
    @bot.message_handler(commands=['help'])
    def send_help(message):
        """Обработчик команды /help"""
        user = message.from_user
        logger.info(f"Команда /help от пользователя ID: {user.id}")
        
        bot.reply_to(message, Messages.HELP)
        
        logger.debug(f"Справка отправлена пользователю {user.id}")
    
    @bot.message_handler(commands=['clear'])
    def clear_history(message):
        """Обработчик команды /clear - очистка истории диалога"""
        user = message.from_user
        user_id = user.id
        logger.info(f"Команда /clear от пользователя ID: {user_id}")
        
        # Очищаем оперативную память
        memory.clear_history(user_id)
        # Очищаем базу данных
        db_manager.clear_all_history(user_id)
        
        bot.reply_to(message, Messages.HISTORY_CLEARED)
        
        logger.debug(f"История диалога пользователя {user_id} полностью очищена")

