from pyrogram.enums import UserStatus
from pyrogram import Client
from data import *
import time
import gspread
from google.oauth2 import service_account

cell_name_flag = False
app = Client(name='my_acc', api_id=api_id, api_hash=api_hash)
time_index = 2
# Установка учетных данных и доступа к Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file('cred.json', scopes=scope)

# пользователь : {буква ячейки: номер ячейки}
users = {
    'DanilaGrischenko': {
        '': 2
    },
    'mrsex001': {
        '': 2
    },
    'Ded_l33t': {
        '': 2
    }
}


def is_user_online(username):
    user = app.get_users(username)
    return username, int(user.status is UserStatus.ONLINE)


# запись имени в таблицу и получение буквы ячейки юзера
def cell_name(usernames):
    global cell_name_flag
    spreadsheet = gspread.authorize(credentials)
    worksheet = spreadsheet.open('online_spy').worksheet('first_list')
    my_set = set()  # сет для проверки вноса всех имен из users
    # первая ячейка - время
    worksheet.update('A1', 'Дата и время')
    # проверка на наличие юзернейма в ячейке
    for username in usernames:
        for char in range(66, 90):
            str_range = f'{chr(char)}1'
            row_range = worksheet.range(str_range)
            cell_value = [cell.value for cell in row_range]
            if cell_value != [''] and cell_value == [f'{username}']:
                print('already in')
                users[username][str_range[:1]] = 2
                del users[username]['']
                my_set.add(username)
                break
            elif cell_value == ['']:
                for _, cell in enumerate(row_range):
                    cell.value = username
                    worksheet.update_cells(row_range)
                    users[username][str_range[:1]] = 2
                    del users[username]['']
                    print('wrote a name')
                    my_set.add(username)
                    break
                break
        # смотрим, все ли имена внесли в таблицу
        if len(my_set) == len(users):
            cell_name_flag = True


def sheet_clear():
    client = gspread.authorize(credentials)
    spreadsheet = client.open('online_spy')
    worksheet = spreadsheet.worksheet('first_list')
    start_col = 1  # Начальный столбец (А)
    end_col = 26  # Конечный столбец (Z)
    start_row = 1  # Начальная строка
    end_row = 500  # Конечная строка

    # Очистка диапазона ячеек
    for col in range(start_col, end_col + 1):
        cell_range = worksheet.range(start_row, col, end_row, col)
        for cell in cell_range:
            cell.value = ''
        worksheet.update_cells(cell_range)

    print('Cleared')


def time_insert():
    global time_index
    spreadsheet = gspread.authorize(credentials)
    worksheet = spreadsheet.open('online_spy').worksheet('first_list')

    struct = time.localtime(time.time())
    good_format = time.strftime('%d.%m.%Y %H:%M', struct)

    range_start = f'A{time_index}'
    named_range = worksheet.range(range_start)
    for _, cell in enumerate(named_range):
        cell.value = good_format
        worksheet.update_cells(named_range)


def sheet_insert(name, status):
    spreadsheet = gspread.authorize(credentials)
    worksheet = spreadsheet.open('online_spy').worksheet('first_list')
    # Запись данных в именованный столбец
    for key in users[name]:
        range_start = f'{key}{users[name][key]}'
        named_range = worksheet.range(range_start)
        # Запись данных в ячейки диапазона
        for _, cell in enumerate(named_range):
            cell.value = status
            worksheet.update_cells(named_range)
        print(users)
        print('updated')
        if users[name][key] < 500:
            users[name][key] += 1
        else:
            print('сутки закончились')
            users[name][key] = 2
            sheet_clear()


def online_handler():
    global time_index
    if not cell_name_flag:
        cell_name(users)
    time_insert()
    for username in users:
        name, status = is_user_online(username)
        sheet_insert(name, status)
    time_index += 1


with app:
    while True:
        online_handler()
        time.sleep(60)
