import sqlite3
from pyrogram.enums import UserStatus
from pyrogram import Client
from data import *
import time

app = Client(name='my_acc', api_id=api_id, api_hash=api_hash)

users = ['Markthewriter', 'Jimmythedoc']
online_time = {}

for person in users:
    online_time.update({person: {0.0: 0.0}})  # [online_start, online_end]


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


with app:
    online_handler()

app.run()
