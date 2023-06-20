from pyrogram.enums import UserStatus
from pyrogram import Client
from data import *
import time
import gspread
from google.oauth2 import service_account

cell_name_flag = False
app = Client(name='my_acc', api_id=api_id, api_hash=api_hash)
row_index = 2
# Установка учетных данных и доступа к Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file('cred.json', scopes=scope)

users = [
    'DanilaGrischenko',
    'mrsex001',
    'Ded_l33t',
    'shalimov_k',
    'Yandex6'
]


def is_user_online(username):
    user = app.get_users(username)
    return int(user.status is UserStatus.ONLINE)


# заполнение первой строки таблицы именами
def cell_name(usernames):
    global cell_name_flag
    spreadsheet = gspread.authorize(credentials)
    worksheet = spreadsheet.open('online_spy').worksheet('first_list')

    first_row = ['Дата и время']

    for name in usernames:
        first_row.append(name)

    worksheet.insert_row(first_row, 1)
    cell_name_flag = True

    return cell_name_flag


# внос статусов
def insert_row(my_list):
    spreadsheet = gspread.authorize(credentials)
    worksheet = spreadsheet.open('online_spy').worksheet('first_list')

    worksheet.insert_row(my_list, row_index)


def online_handler():
    global row_index
    row_list = []
    # внос времени проверки в лист со статусами
    struct = time.localtime(time.time())
    good_format = time.strftime('%d.%m.%Y %H:%M', struct)
    row_list.append(good_format)
    # внос имен должен срабатывать только 1 раз
    if not cell_name_flag:
        cell_name(users)
    # формирование листа статусами
    for username in users:
        status = is_user_online(username)
        row_list.append(status)
    insert_row(row_list)
    print('inserted')
    row_index += 1


with app:
    while True:
        online_handler()
        time.sleep(60)
