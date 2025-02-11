# bot.py
import telebot
from utils.data_manager import load_config
from handlers.command_handlers import register_command_handlers
#from handlers.callback_handlers import register_callback_handlers
from handlers.message_handlers import register_message_handlers
import time
import requests

def start_bot():
    config = load_config()
    bot = telebot.TeleBot(config["BOT_TOKEN"])

    # Регистрация обработчиков
    register_command_handlers(bot)
    #register_callback_handlers(bot)
    register_message_handlers(bot)

    # Запуск бота с обработкой возможных исключений
    while True:
        try:
            #logger.info("Бот запущен и ожидает обновлений...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except requests.exceptions.ReadTimeout:
            #logger.warning("Превышено время ожидания. Перезапуск...")
            time.sleep(5)
        except Exception as e:
            #logger.error(f"Произошла ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_bot()