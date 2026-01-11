"""
Модуль с клавиатурами и кнопками бота
"""
from telebot import types


def get_main_keyboard():
    """
    Создает основную клавиатуру бота
    
    Returns:
        ReplyKeyboardMarkup: Основная клавиатура
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Здесь можно добавить кнопки, если они понадобятся
    # Например:
    # button_help = types.KeyboardButton("📚 Помощь")
    # keyboard.add(button_help)
    
    return keyboard


def get_inline_keyboard():
    """
    Создает inline клавиатуру (если понадобится)
    
    Returns:
        InlineKeyboardMarkup: Inline клавиатура
    """
    keyboard = types.InlineKeyboardMarkup()
    
    # Здесь можно добавить inline кнопки, если они понадобятся
    # Например:
    # button = types.InlineKeyboardButton("Текст", callback_data="data")
    # keyboard.add(button)
    
    return keyboard

