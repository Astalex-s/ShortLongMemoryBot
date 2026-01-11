"""
Основной файл запуска Telegram бота
"""
import traceback
import logging
from datetime import datetime
from telebot import TeleBot

from config.logging_config import setup_logging
from config.settings import Settings
from handlers.commands import register_command_handlers
from handlers.messages import register_message_handlers

# Настройка логирования
logger = setup_logging(Settings.LOG_DIR)

# Валидация настроек
Settings.validate()

# Инициализация Telegram бота
bot = TeleBot(Settings.TELEGRAM_BOT_TOKEN)

# Регистрация обработчиков
register_command_handlers(bot)
register_message_handlers(bot)


def main():
    """Основная функция запуска бота"""
    logger.info("=" * 50)
    logger.info("Запуск Telegram бота")
    logger.info(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    try:
        # Получаем информацию о боте
        bot_info = bot.get_me()
        logger.info(f"Бот успешно подключен: @{bot_info.username} (ID: {bot_info.id})")
        logger.info("Ожидание сообщений...")
        
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
        
    except KeyboardInterrupt:
        logger.info("=" * 50)
        logger.info("Получен сигнал остановки (KeyboardInterrupt)")
        logger.info("Остановка бота...")
        logger.info("=" * 50)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.critical(
            f"Критическая ошибка при работе бота: {e}\n"
            f"Traceback:\n{error_traceback}"
        )
        logger.info("Бот остановлен из-за критической ошибки")
    finally:
        logger.info("Бот завершил работу")


if __name__ == '__main__':
    main()
