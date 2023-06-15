import sqlite3
from pyrogram import Client, idle, filters
from pyrogram.enums import UserStatus, ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, BotCommand, ReplyKeyboardMarkup, KeyboardButton
from data import *
import time

token = bot_token

app = Client(name='my_acc_commands_test', api_id=api_id, api_hash=api_hash, parse_mode=ParseMode.HTML)

reply_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Внести нового юзера'
        ),
        KeyboardButton(
            text='Удалить юзера'
        )
    ],
    [
        KeyboardButton(
            text='График онлайна всех юзеров'
        ),
        KeyboardButton(
            text='Список всех юзеров'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True, placeholder='Press any button')

users = ['Markthewriter', 'Jimmythedoc']
online_time = {}
last_bot_msg = ''
chat_id = 734357667

for person in users:
    online_time.update({person: {0.0: 0.0}})  # [online_start, online_end]


def command_start(client: app, message: Message):
    message.reply('Приветствую в SpyBot!', reply_markup=reply_keyboard)


def key_add(_, message: Message):
    message.reply('Введите ник юзера вместе с "@" для добавления')

    if message.text.startswith("@"):
        username = message.text[1:]  # Удаление символа "@" из юзернейма
        # Проверка наличия аккаунта с указанным юзернеймом
        user = app.get_users(username)
        if user:
            message.reply(f"Аккаунт {username} найден в Telegram")
        else:
            message.reply(f"Аккаунт {username} не найден в Telegram")


def key_delete(_, message: Message):
    message.reply('Введите ник юзера вместе с "@" для удаления')


def key_schedule(_, message: Message):
    message.reply('График на текущий момент:')


def key_list(_, message: Message):
    message.reply(f'Список пользователей для отслеживания:')
    msg = '\n'.join(user for user in users)
    message.reply(msg)


# можно сделать изящнее, если проверять через тексты кнопок, а не список
def all_reply(_, message):
    texts = ['Внести нового юзера', 'Удалить юзера', 'График онлайна всех юзеров', 'Список всех юзеров']
    if message.text not in texts:
        message.reply('Используйте кнопки')


@app.on_message(filters.command(commands=['start']))
def handle_command_start(client, message):
    command_start(client, message)


@app.on_message(filters.text & filters.regex('^Внести нового юзера$'))
def handle_key_add(client, message):
    key_add(client, message)


@app.on_message(filters.text & filters.regex('^Удалить юзера$'))
def handle_key_delete(client, message):
    key_delete(client, message)


@app.on_message(filters.text & filters.regex('^График онлайна всех юзеров$'))
def handle_key_schedule(client, message):
    key_schedule(client, message)


@app.on_message(filters.text & filters.regex('^Список всех юзеров$'))
def handle_key_list(client, message):
    key_list(client, message)


app.add_handler(MessageHandler(command_start, filters.command(commands='start')))
app.add_handler(MessageHandler(all_reply))
app.add_handler(MessageHandler(key_add))
app.add_handler(MessageHandler(key_delete))
app.add_handler(MessageHandler(key_list))
app.add_handler(MessageHandler(key_schedule))

bot_commands = [
    BotCommand(
        command='start',
        description='перезапуск бота'
    )
]


def is_user_online(username):
    user = app.get_users(username)
    return user.status is UserStatus.ONLINE


def save_to_database(username, online_start, online_end):
    conn = sqlite3.connect('online_time.db')
    c = conn.cursor()

    c.execute("INSERT INTO online_time (username, online_start, online_end) VALUES (?, ?, ?)",
              (username, online_start, online_end))

    conn.commit()
    conn.close()


def execute_last_seen(username):
    conn = sqlite3.connect('online_time.db')
    c = conn.cursor()

    c.execute('SELECT * FROM online_time WHERE username = ? ORDER BY id DESC LIMIT 1', (username,))

    row = c.fetchone()

    conn.close()

    if row:
        last_online_start = row[2]
        last_seen = row[3]

        return last_online_start, last_seen


def is_database_empty():
    conn = sqlite3.connect('online_time.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM online_time')

    result = c.fetchone()
    count = result[0]

    conn.close()

    return count == 0


def create_table_if_not_exists():
    conn = sqlite3.connect('online_time.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS online_time
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT,
               online_start REAL,
               online_end REAL)''')

    conn.commit()
    conn.close()


def online_handler():
    global online_time
    create_table_if_not_exists()
    while True:
        for username in users:
            if is_user_online(username) and not online_time[username][0]:
                online_time[username][0] = time.time()
                print(f'{username} онлайн!')
            elif not is_user_online(username):
                if not online_time[username][0]:
                    if not is_database_empty():
                        _, last_seen = execute_last_seen(username)
                        print(f'{username} пока не заходил в сеть. Последний раз был в сети: {last_seen}')
                    else:
                        print(f'{username} пока не заходил в сеть.')
                else:
                    online_time[username][1] = time.time()

                    struct = time.localtime(online_time[username][0])
                    good_format = time.strftime('%d.%m.%Y %H:%M:%S', struct)

                    struct1 = time.localtime(online_time[username][1])
                    good_format1 = time.strftime('%d.%m.%Y %H:%M:%S', struct1)

                    print(f'{username} вышел из онлайн, зашел в {good_format}, вышел в {good_format1}')

                    save_to_database(username, good_format, good_format1)
                    online_time[username].update({0.0: 0.0})
        time.sleep(1)


"""with app:
    online_handler()"""

#app.run()
app.start()
app.set_bot_commands(bot_commands)
idle()
app.stop()
