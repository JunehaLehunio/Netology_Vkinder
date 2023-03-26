import json
import requests
from pprint import pprint

"""ПОДКЛЮЧЕНИЕ ФАЙЛОВ"""
from data_db import create
from temp_message_request_processing import processing_message

# ****************************************************************
print('', '= ' * 21, '\n', (' ' * 9), '  VKinder bot start  \n', ('= ' * 21))

"""ЧТЕНИЕ ИЗ ФАЙЛА КЛЮЧЕЙ"""
"""ИЗМЕНИТЬ key_json"""
with open("C:/Users/Sus/PycharmProjects/All/key.json", 'r') as file:
    read_json = file.read()
key_data_json = json.loads(read_json)

token_group = key_data_json['token_group']
token_user = key_data_json['token_user']
group_id = key_data_json['group_id']
password = key_data_json['password']
database = key_data_json['database']

# ****************************************************************
#                      СОЗДАЕМ БД И ТАБЛИЦЫ
create_data_base = create(int(password)).create_db()
create_table = create(int(password)).create_table()
print(create_data_base, create_table)


# ======================================================================================================================


# ----------------------------------------------------------------
def connect_bot():
    print('Подключение к VK')
    params_long_poll_server = {
        "access_token": token_group,
        "group_id": group_id,
        "v": "5.131"}

    long_poll_server = requests.get('https://api.vk.com/method/groups.getLongPollServer', params_long_poll_server)
    data_long_poll_server = long_poll_server.json()['response']
    server = data_long_poll_server['server']
    key = data_long_poll_server['key']
    ts = data_long_poll_server['ts']
    bots_longpoll_api(ts, key, server)


def bots_longpoll_api(ts, key, server):
    params_bots_longpoll_api = {
        "act": 'a_check',
        "key": key,
        "ts": ts,
        "wait": 25
    }

    bot_create_connect = requests.get(server, params=params_bots_longpoll_api)
    server_response = bot_create_connect.json()['updates']

    # смотрим, что пришло в сообщении от сервера
    # если время ожидания сервера ("wait": 25) пришло сообщение, то выполним код и в конце перезагружаем соединение с измененным ts
    if server_response:
        input_message_serv = server_response[0]['type']

        if input_message_serv == 'message_new':  # если тип сообщения - новое сообщение от пользователя
            message_from_id = server_response[0]['object']['message'][
                'from_id']  # смотрим id пользователя, который написал сообщение. Нужен для вставки в параметры и ответа ему же
            message_in = server_response[0]['object']['message']['text']  # смотрим тело сообщения

            # заменяем двоеточие на запятую и делаем буквы прописью, убираем все пробелы, разделяем все запятой
            converting_message = message_in.replace(':', ',').lower().replace(' ', '').split(sep=',', maxsplit=-1)

            # полученный результат отправляем в файл с функцией обработки текста сообщения
            processing_message(converting_message, token_group, token_user, message_from_id, password)
            # перезагружаем соединение с сервером с изменением параметра ts
            ts = int(ts) + 1
            bots_longpoll_api(ts, key, server)

        # если тип сообщения - новое сообщение от сообщества(чтобы не реагировал на свои сообщения)
        elif input_message_serv == 'message_reply':
            # перезагружаем соединение с сервером с изменением параметра ts
            ts = int(ts) + 1
            print(ts)
            bots_longpoll_api(ts, key, server)

    # #если время ожидания сервера ("wait": 25) истекло и не пришло ответа, то перезагружаем соединение с теми же параметрами
    else:
        pprint(server_response)
        print('restart server')
        bots_longpoll_api(ts, key, server)


connect_bot()
