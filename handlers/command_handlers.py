# handlers/command_handlers.py
import re
import string
from telebot import types
from telebot.types import Message
from utils.data_manager import load_config, save_config, load_data, save_data
#from utils.navigation import navigate_to_path
#from utils.keyboards import generate_markup
import hashlib
import telebot

########################################################################

# Функция для обработки поиска по хэштегам
def search_caption(bot, message, need_all_tags):
    data = load_data()
    # Записываем ответ пользователя в переменную, убираем запятые и разделяем слова
    caption_to_search = (message.text).replace(",", " ").split()
    
    # Очищаем ввод: удаляем лишние пробелы, убираем значки хэштегов
    caption_to_search = [word.strip().strip('#') for word in caption_to_search]
    
    # Ищем видео по хэштегам
    found_videos_data = []
    for user, user_data in data["users"].items():
        for video in user_data["videos"]:
            if need_all_tags:
                # Проверяем, содержатся ли все указанные хэштеги в видео
                if all(word in video["caption"] for word in caption_to_search):
                    found_videos_data.append({
                        "file_id": video["file_id"],
                        "caption": video["caption"]
                    })
            else:
                if any(word in video["caption"] for word in caption_to_search):
                    found_videos_data.append({
                        "file_id": video["file_id"],
                        "caption": video["caption"]
                    })

    # Отправляем результат пользователю
    if found_videos_data:
        #i = 0
        for video in found_videos_data:
            bot.send_video(message.chat.id, video["file_id"], caption=video["caption"])

            # СДЕЛАТЬ ПРОВЕРКУ НА БОЛЬШОК КОЛИЧЕСТВО ВЫВОДИМЫХ ВИДЕО
            '''i = i+1
            if (i) == 10:'''
    else:
        bot.reply_to(message, "Видео с указанными ключевыми словами не найдены.")


########################################################################

# Функция проверки пароля админа

def check_admin_pswrd(bot: telebot.TeleBot, message: Message):
    config = load_config()
    pswrd_to_check = str(message.text)

    pswrd_to_check_md5 = hashlib.md5((pswrd_to_check+config["SALT"]).encode()).hexdigest()

    if pswrd_to_check_md5 == config["PSWRD_MD5"]:
        new_admin_id = message.chat.id
        if str(new_admin_id) not in config["ADMINS"]:
            config["ADMINS"].append(str(new_admin_id))
            bot.send_message(message.chat.id, 'Теперь вам открыта возможность добавлять видео. Нажмите /start')
            save_config(config)
        else:
            bot.send_message(message.chat.id, 'Вам уже доступна возможность добавлять видео. Нажмите /start')
    else:
        bot.send_message(message.chat.id, 'Пароль неверный.')

########################################################################

# Функция поиска и редактирования описания к видео в библиотеке

def find_and_edit_caption(bot: telebot.TeleBot, replied_message: Message, new_caption_msg: Message):
    data = load_data()
    video_id_to_find = replied_message.video.file_id

    for user, user_data in data["users"].items():
        for video in user_data["videos"]:
            if video["file_id"] == video_id_to_find:
                bot.send_message(replied_message.chat.id, "Видео найдено в библиотеке.\n"
                                                            "Его описание = " + video["caption"]+'\n'
                                                            "Новое описание = " + new_caption_msg.text)
                video['caption'] = new_caption_msg.text
                save_data(data)
                return
    bot.send_message(replied_message.chat.id, 'Видео не найдено в библиотеке.')
    
########################################################################
# Функция для обработки команды /start

def register_command_handlers(bot: telebot.TeleBot):
    @bot.message_handler(commands=['start'])
    def handle_start(message: Message):
        user_id = message.chat.id
        if not str(user_id).startswith('-100'):
            config = load_config()
            if str(user_id) in config["ADMINS"]:
                bot.send_message(message.chat.id, "Добро пожаловать! Я умею сохранять видео:\n\n"
                                                "Загрузи видео, подписав его ключевыми словами (например, хэштегами #stand #Tutorial, #SpInnInG "
                                                "или просто словами).\n"
                                                "Регистр не важен.\n\n"
                                                "Используй команды:\n"
                                                "/start - для перезапуска бота\n"
                                                "/find_and - для поиска видео, в подписи которого будут все ключевые слова\n"
                                                "/find_or - для поиска видео, в подписи которого будет хотя бы одно ключевое слов\n"
                                                "/edit - изменить описание к видео\n"
                                                "/list - показать список всех ключевых слов"
                                                )
            else:
                bot.send_message(message.chat.id, "Добро пожаловать!\n\n"
                                                "Используй команды:\n"
                                                "/start - для перезапуска бота\n"
                                                "/find_and - для поиска видео, в подписи которого будут все ключевые слова\n"
                                                "/find_or - для поиска видео, в подписи которого будет хотя бы одно ключевое слов\n"
                                                "/list - показать список всех ключевых слов"
                                                )
                
########################################################################
# Функция для обработки команды /find_and

    @bot.message_handler(commands=['find_and'])
    def handle_find_and(message: Message):
        if not str(message.chat.id).startswith('-100'):
            bot.send_message(message.chat.id, "Укажите ключевые слова через пробел или запятую.\n"
                                               "Будут найдены видео, в подписи которых есть все указанные слова.")
            # Регистрируем следующий шаг — ожидание ответа пользователя
            bot.register_next_step_handler(
                message, 
                lambda msg: search_caption(bot, msg, need_all_tags=True)  # Лямбда-функция
            )

########################################################################
# Функция для обработки команды /find_or

    @bot.message_handler(commands=['find_or'])
    def handle_find_and(message: Message):
        if not str(message.chat.id).startswith('-100'):
            bot.send_message(message.chat.id, "Укажите ключевые слова через пробел или запятую.\n"
                                               "Будут найдены видео, в подписи которых есть любое из указанных слов.")
            # Регистрируем следующий шаг — ожидание ответа пользователя
            bot.register_next_step_handler(
                message, 
                lambda msg: search_caption(bot, msg, need_all_tags=False)  # Лямбда-функция
            )

########################################################################
# Функция для обработки команды /admin

    @bot.message_handler(commands=['admin'])
    def handle_find_and(message: Message):
        if not str(message.chat.id).startswith('-100'):
            bot.send_message(message.chat.id, "Введите пароль администратора")
            # Регистрируем следующий шаг — ожидание ответа пользователя
            bot.register_next_step_handler(
                message, 
                lambda msg: check_admin_pswrd(bot, msg)  # Лямбда-функция
            )

########################################################################
# Функция для обработки команды /edit

    @bot.message_handler(commands=['edit'])
    def handle_find_and(message: Message):
        if not str(message.chat.id).startswith('-100'):
            user_id = message.chat.id
            config = load_config()
            if str(user_id) in config["ADMINS"]:
                replied_message = message.reply_to_message
                if replied_message and replied_message.content_type  == 'video':
                    bot.send_message(message.chat.id, "Введите новое описание для этого видео.")
                    # Регистрируем следующий шаг — ожидание ответа пользователя
                    bot.register_next_step_handler(
                        message, 
                        lambda msg: find_and_edit_caption(bot, replied_message, msg)  # Лямбда-функция
                    )
                else:
                    bot.send_message(message.chat.id, "Отправьте команду в ответ на видео, описание к которому вы хотите отредактировать.")
            else:
                bot.send_message(message.chat.id, "У вас нет прав для редктирования описаний к видео.")

########################################################################
# Функция для обработки команды /list

    @bot.message_handler(commands=['list'])
    def handle_find_and(message: Message):
        if not str(message.chat.id).startswith('-100'):
            data = load_data()
            caption_words_set = set()

            for user, user_data in data["users"].items():
                for video in user_data["videos"]:
                    current_caption = video["caption"]
                    # убираем запятые и разделяем слова
                    # escape экранирует специальные символы, чтобы они корректно обрабатывались в регулярном выражении
                    # f"[{результат re.escape}]+" - квдратные скобки - regexp, + - любое кол-во символов
                    words = re.sub(f"[{re.escape(string.punctuation + string.whitespace)}]+", " ", current_caption).split()
                    #.strip('#').split()
                    for word in words:
                        #if word not in caption_words_list:
                        caption_words_set.add(word)
            caption_words_list = sorted(caption_words_set)

            if len(caption_words_list) > 0:
                bot.send_message(message.chat.id, "Слова, которые есть в описаниях к видео:\n\n"
                                                + ", ".join(caption_words_list))  # Преобразуем элементы списка в строки)
            else:
                bot.send_message(message.chat.id, "В библиотеке нет ни одного видео с описанием.")

