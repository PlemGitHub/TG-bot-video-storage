# handlers/message_handlers.py
from telebot.types import Message
from utils.data_manager import load_config, load_data, save_data, init_user
#from utils.navigation import navigate_to_path
import telebot
import uuid  # Для генерации уникальных short_id
import logging

logger = logging.getLogger(__name__)

def register_message_handlers(bot: telebot.TeleBot):
    @bot.message_handler(content_types=['video'])
    def handle_message(message: Message):
        user_id = str(message.chat.id)
        config = load_config()
        if user_id in config["ADMINS"]:
            data = load_data()
            init_user(data, user_id)
            caption = message.caption
            # Проверяем, что это не команда
            if message.content_type == 'text' and message.text.startswith('/'):
                return

            if message.content_type == 'video':
                file_id = message.video.file_id
                data['users'][user_id]['videos'].append({
                    'file_id': file_id,
                    'caption': caption
                })
                save_data(data)
                bot.reply_to(message, 'Видео сохранено.')