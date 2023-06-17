import sqlite3
from pyrogram.enums import UserStatus
from pyrogram import Client
from data import *
import time
import schedule

app = Client(name='my_acc', api_id=api_id, api_hash=api_hash)

users = ['shalimov_k', 'reilon', 'Jimmythedoc']


def is_user_online(username):
    user = app.get_users(username)
    return user.status is UserStatus.ONLINE


def save_to_database(username, time, is_online):
    conn = sqlite3.connect('online_time.db')
    c = conn.cursor()

    c.execute("INSERT INTO online_time (username, time, is_online) VALUES (?, ?, ?)",
              (username, time, is_online))

    conn.commit()


def is_database_empty():
    conn = sqlite3.connect('online_time.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM online_time')

    result = c.fetchone()
    count = result[0]
    return count == 0


def create_table_if_not_exists():
    conn = sqlite3.connect('online_time.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS online_time
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT,
               time REAL,
               is_online INTEGER)''')

    conn.commit()


def online_handler():
    create_table_if_not_exists()
    for username in users:
        struct = time.localtime(time.time())
        good_format = time.strftime('%d.%m.%Y %H:%M:%S', struct)

        is_online = int(is_user_online(username))
        save_to_database(username, good_format, is_online)
        print(username, is_online)


with app:
    schedule.every(1).minutes.do(online_handler)

    while True:
        schedule.run_pending()
        time.sleep(1)

