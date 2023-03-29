import json
import requests
from vk_handler import send_message
from data_db import create
from message_request_processing import processing_message

print('', '= ' * 21, '\n', (' ' * 9), '  VKinder bot start  \n', ('= ' * 21))

"""ЧТЕНИЕ ИЗ ФАЙЛА КЛЮЧЕЙ"""
with open("customizing_setting.json", 'r') as file:
    read_json = file.read()
key_data_json = json.loads(read_json)

token_group = key_data_json['token_group']
token_user = key_data_json['token_user']
group_id = key_data_json['group_id']
password = key_data_json['password']

"""СОЗДАЕМ БД И ТАБЛИЦЫ"""
create_data_base = create(int(password)).create_db()
create_table = create(int(password)).create_table()
print(create_data_base, create_table)


"""ПОЛУЧЕНИЕ ДАННЫХ ДЛЯ ПОДКЛЮЧЕНИЯ К СЕРВЕРУ"""
def connect_bot():
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


"""СОЕДИНЕНИЕ С СЕРВЕРОМ И ОЖИДАНИЕ СООБЩЕНИЯ"""
def bots_longpoll_api(ts, key, server):
    params_bots_longpoll_api = {
        "act": 'a_check',
        "key": key,
        "ts": ts,
        "wait": 25
    }

    bot_create_connect = requests.get(server, params=params_bots_longpoll_api)
    server_response = bot_create_connect.json()['updates']

    """ смотрим, что пришло в сообщении от сервера
    если во время ожидания сервера ("wait": 25) пришло сообщение, то проверяем отправителя и тело сообщения, 
    перезагружаем соединение со смещенным ts"""
    if server_response:
        input_message_serv = server_response[0]['type']
        if input_message_serv == 'message_new':  # Тип сообщения - от пользователя

            # Смотрим id пользователя, который написал сообщение. Нужен для вставки в параметры и ответа ему же
            for_the_user_id = server_response[0]['object']['message']['from_id']
            message_in = server_response[0]['object']['message']['text']  # смотрим тело сообщения

            # заменяем двоеточие на запятую и делаем буквы прописью, убираем все пробелы, разделяем все запятой
            converting_message = message_in.lower().replace(' ', '').split(sep=',', maxsplit=-1)

            # проверяем первые символы сообщения, если число, то отправляем True
            age_converting_message = message_in[:2]

            # Проверяем является ли значение возраста числом
            if age_converting_message.isdigit() is True:

                # Проверяем возраст. Больше или равен 18 и меньше 100
                if 18 <= int(age_converting_message) < 100:

                    # Проверяем длину сообщения:
                    quantity = []
                    for quantity_iter in range(len(converting_message)):
                        quantity.append(quantity_iter)
                    if len(quantity) == 2:
                        age_converting_message = True

                        # полученный результат отправляем в файл с функцией обработки текста сообщения
                        processing_message(age_converting_message, converting_message, token_group, token_user,
                                           for_the_user_id, password)
                    else:
                        attachment = ''
                        message = 'Неверно введены данные.'
                        send_message(message, attachment, for_the_user_id, token_group)
                else:
                    attachment = ''
                    message = 'Неверно указан возраст.'
                    send_message(message, attachment, for_the_user_id, token_group)
            else:
                age_converting_message = False
                processing_message(age_converting_message, converting_message, token_group, token_user, for_the_user_id,
                                   password)
            # перезагружаем соединение с сервером с изменением параметра ts
            ts = int(ts) + 1
            bots_longpoll_api(ts, key, server)

        # если тип сообщения - новое сообщение от сообщества(чтобы не реагировал на свои сообщения)
        elif input_message_serv == 'message_reply':
            # перезагружаем соединение с сервером с изменением параметра ts
            ts = int(ts) + 1
            bots_longpoll_api(ts, key, server)

    # #если время ожидания сервера ("wait": 25) истекло и не пришло ответа, то перезагружаем соединение не изменяя ts
    else:
        bots_longpoll_api(ts, key, server)


connect_bot()
