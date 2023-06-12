from pyrogram import Client
from data import *
import time

app = Client(name='my_acc', api_id=api_id, api_hash=api_hash)
online_start_time = None

users = {
    'Markthewriter': {},
    'clown000001': {}
}

with app:
    for user in users:
        chel = app.get_users(user)
        user_id = chel.id
        users[user].update({user_id: 0})


def online_handler(client, update):
    global online_start_time
    if str(update.status) == "UserStatus.ONLINE" and update.id != client.get_me().id:
        if online_start_time is None:
            online_start_time = time.time()
        print(f'{user} вошел в онлайн!')
    elif str(update.status) == "UserStatus.OFFLINE" and update.id != client.get_me().id:
        if online_start_time is not None:

            struct = time.localtime(online_start_time)
            good_format = time.strftime('%d.%m.%Y %H:%M', struct)

            online_end_time = time.time()
            online_duration = online_end_time - online_start_time

            struct1 = time.localtime(online_end_time)
            good_format1 = time.strftime('%d.%m.%Y %H:%M', struct1)

            if online_duration >= 60:
                mins = online_duration // 60
                if mins >= 60:
                    hrs = mins // 60
                    mins -= hrs * 60
                else:
                    hrs = 0
                online_duration -= mins * 60
            else:
                mins = 0
                hrs = 0
            print(f'{user} вышел из онлайн, зашел в {good_format}, вышел в {good_format1},'
                  f' время в сети: {hrs} ч {mins} мин {int(online_duration)} сек')
            users[user][user_id] += int(online_duration)
            print(users)
        else:
            print('Юзер пока не заходил в сеть')
        online_start_time = None


app.on_user_status('UserStatus.ONLINE')(online_handler)

app.run()
