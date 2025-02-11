# utils/data_manager.py
import json
import os

CONFIG_FILE = "Video_Storage_Bot/config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
        json.dump(config, file, ensure_ascii=False, indent=4)
    
def load_data():
    DATA_FILE = load_config()['DATA_FILE']
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data(data):
    DATA_FILE = load_config()['DATA_FILE']
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def init_user(data, user_id):
    if user_id not in data["users"]:
    # Инициализация пользователя, если он ещё не существует
        data["users"][user_id] = {
            "videos": [
                {"file_id": "", "caption": ""},
            ]
        }
        data["users"][user_id] = []