"""
Модуль для управления памятью диалогов (единый экземпляр)
"""
from utils.memory import ConversationMemory
from config.settings import Settings

# Единый экземпляр памяти для всего приложения
memory = ConversationMemory(max_messages=Settings.MAX_MESSAGES_HISTORY)

