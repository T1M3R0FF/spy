import time
import gspread
import os
from pyrogram.enums import UserStatus
from pyrogram import Client
from google.oauth2 import service_account
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = Client(name='my_acc', api_id=os.getenv('api_id'), api_hash=os.getenv('api_hash'))

# Установка учетных данных и доступа к Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file('cred.json', scopes=scope)

users = os.getenv('users').split(',')


def is_user_online(username):
    user = app.get_users(username)
    return int(user.status is UserStatus.ONLINE)


# заполнение первой строки таблицы именами
def cell_name(usernames):
    spreadsheet = gspread.authorize(credentials)
    worksheet = spreadsheet.open('online_spy').worksheet('first_list')

    first_row = ['Дата и время'] + usernames

    # обновление строки новыми именами
    row_data = [first_row]

    worksheet.update('A1', row_data)


# внос статусов
def append_statuses(my_list):
    spreadsheet = gspread.authorize(credentials)
    worksheet = spreadsheet.open('online_spy').worksheet('first_list')

    worksheet.append_row(my_list)


def online_handler():
    row_list = []
    # внос времени проверки в лист со статусами
    good_format = time.strftime('%d.%m.%Y %H:%M')
    row_list.append(good_format)

    # формирование листа статусами
    for username in users:
        status = is_user_online(username)
        row_list.append(status)
    append_statuses(row_list)
    print('inserted')


with app:
    cell_name(users)
    while True:
        online_handler()
        time.sleep(60)
