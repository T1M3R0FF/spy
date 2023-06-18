import sqlite3
from pyrogram.enums import UserStatus
from pyrogram import Client
from data import *
import time
import schedule
import gspread
from google.oauth2 import service_account

cell_index = 2
app = Client(name='my_acc', api_id=api_id, api_hash=api_hash)

# Установка учетных данных и доступа к Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file('cred.json', scopes=scope)

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


def sheet_insert(status):
    global cell_index
    username = 'shalimov_k'

    spreadsheet = gspread.authorize(credentials)
    worksheet = spreadsheet.open('online_spy').worksheet('first_list')
    # Запись данных в именованный столбец
    column_name = username
    data = status  # Здесь можно указать ваши данные

    # Получение диапазона ячеек для именованного столбца

    range_start = f'B{cell_index}'
    named_range = worksheet.range(range_start)
    # Запись данных в ячейки диапазона
    for _, cell in enumerate(named_range):
        cell.value = data
        worksheet.update_cells(named_range)
    print('updated')
    cell_index += 1


def online_handler():
    create_table_if_not_exists()
    for username in users:
        struct = time.localtime(time.time())
        good_format = time.strftime('%d.%m.%Y %H:%M:%S', struct)

        is_online = int(is_user_online(username))
        save_to_database(username, good_format, is_online)
        sheet_insert(is_online)


with app:
    schedule.every(5).seconds.do(online_handler)

    while True:
        schedule.run_pending()
        time.sleep(1)
