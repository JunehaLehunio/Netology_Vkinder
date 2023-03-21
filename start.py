from pprint import pprint
import requests
from datetime import datetime  # для получения даты рождения
import json

# ----------------------------------------------------------------
from find_user_0 import cl_find_all_user, cl_send_message, cl_send_Photo

# ----------------------------------------------------------------
from vk_api import VkApi
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
from io import BytesIO

with open("C:/Users/Sus/PycharmProjects/All/key.json", 'r') as file:
    read_json = file.read()
key_json = json.loads(read_json)
token_group = key_json['token_group']
token_user = key_json['token_user']
# ================================================================
print('start')


# ================================================================================================================================================================================================


# ----------------------------------------------------------------
def start():
    params = {
        "access_token": token_group,
        "group_id": 106338460,
        "v": "5.131"}

    resp_all_album = requests.get('https://api.vk.com/method/groups.getLongPollServer', params)
    response_all_album = resp_all_album.json()['response']
    server = response_all_album['server']
    key = response_all_album['key']
    ts = response_all_album['ts']
    bots_longpoll_api(ts, key, server)


# ----------------------------------------------------------------


def bots_longpoll_api(ts, key, server):
    # ----------------------------------------------------------------
    para = {
        "act": 'a_check',
        "key": key,
        "ts": ts,
        "wait": 25
    }

    resp = requests.get(server, params=para)
    bum = resp.json()
    pprint(bum)

    # смотрим, что пришло в сообщении от сервера
    if resp.json()['updates']:
        input_message_serv = resp.json()['updates'][0]['type']
        print(input_message_serv)
        if input_message_serv == 'message_new':  # если тип сообщения - новое сообщение от пользователя
            message_from_id = resp.json()['updates'][0]['object']['message'][
                'from_id']  # смотрим id пользователя, который написал сообщение. Нужен для вставки в параметры и ответа ему же
            message_in = resp.json()['updates'][0]['object']['message']['text']  # смотрим тело сообщения
            pprint(message_from_id)
            # revue(rere, message_in,message_from_id)
            pprint(message_in)
            temp = resp.json()['updates'][0]
            pprint(f'in mess {temp}')
            # преобразуем все символы текста в строчные
            # low = message_in.lower()

            # преобразуем полученный текст в список
            # first_simbol_message = low[0:3]                                                # проверяем первые три символа вошедшего сообщенияб потом сравниваем с шаблонами
            # print(first_simbol_message)

            # заменяем двоеточие на запятую и делаем буквы прописью, убираем все пробелы, разделяем все запятой
            converting_message = message_in.replace(':', ',').lower().replace(' ', '').split(sep=',', maxsplit=-1)

            # ----------------------------------------------------------------
            if 'еще' in converting_message:  # заменить                 # если первые символы начинаются на "при", то сравним с шаблоном

                with open('find_vk_data.json', encoding='utf-8') as json_file:
                    vk_data = json.load(json_file)

                    print(vk_data)
                    old_token_user = vk_data['token_user']
                    old_token_group = vk_data['token_group']
                    old_hometown = vk_data['hometown']
                    old_birth_year = vk_data['birth_year']
                    old_sex = vk_data['sex']
                    old_status = vk_data['status']
                    old_offset = vk_data['offset']
                    print(old_offset)

                # ***********************************************
                find_user = cl_find_all_user(token_user=old_token_user, hometown=old_hometown,
                                             birth_year=old_birth_year, sex=old_sex, status=old_status,
                                             offset=old_offset).find
                print(find_user)

                last_name = find_user[0]["last_name"]
                first_name = find_user[0]["first_name"]
                photo_max = find_user[0]["photo_max"]
                offset = int(find_user[0]["offset"]) + 1
                user_id = find_user[0]["user_id"]
                print(offset)

                # **********************************************
                vk_data = {"token_user": f"{token_user}",
                           "token_group": f"{token_group}",
                           "hometown": f"{old_hometown}",
                           "birth_year": f"{old_birth_year}",
                           "sex": f"{old_sex}",
                           "status": f"{old_status}",
                           "offset": f"{int(offset) + 1}"
                           }
                with open('find_vk_data.json', 'w') as outfile:
                    json.dump(vk_data, outfile)

                # ***********************************************
                # ==========ОТПРАВЛЯЕМ ФОТО===========
                # # получаем ссылку для загрузки

                # + делаем фото
                vk_session = VkApi(token=token_group)
                vk = vk_session.get_api()
                upload = VkUpload(vk)
                img = requests.get(photo_max).content
                f = BytesIO(img)
                response = upload.photo_messages(f)[0]
                owner_id = response['owner_id']
                photo_id = response['id']
                access_key = response['access_key']

                message_out = f'@id{user_id}({last_name} {first_name})'
                attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                # +

                cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                                token_group=old_token_group).message_

                # ***********************************************

                message_out = f'@id{user_id}({last_name} {first_name})'
                # message_out = f'https://vk.com/id{user_id} {last_name} {first_name}\n{photo_max}'
                # cl_send_message(message_from_id=message_from_id, message=message_out,
                #                 token_group=old_token_group).message_
            # ----------------------------------------------------------------

            elif 'старт' in converting_message:
                print(converting_message)

                message = 'пиши  найди: через запятую возраст, пол(м/ж), город, семейное положение. Пример:\n' \
                          'найди: 20, ж, Москва, 1'
                send = cl_send_message(message_from_id=message_from_id, message=message,
                                       token_group=token_group).message_
                print(send)
                # else:
                #     message = 'Возможно, вы имели в виду "старт"?\n' \
                #               'Введите запрос еще раз.'
                #     send = cl_send_message(message_from_id=message_from_id, message=message, token_group=token_group).message_
                #     print(send)

            # ----------------------------------------------------------------

            elif 'найди' in converting_message:

                # ======================          ПРОВЕРКИ ВХОДЯЩИХ ДАННЫХ     =====================
                # проверяем итераций в полученном списке и записываем их в список длины
                quantity = []
                for quantity_iter in range(len(converting_message)):
                    quantity.append(quantity_iter)

                # print(f'len {len(quantity)} li_message {li_message[0]}') # ---------------

                # делаем триггеры, запускающий поиск. Во время проверок его значение изменяется на истину или остается ложью. Если одно из значений будет ложью, то не запустится поиск
                in_age = False
                in_sex = False
                in_city = False
                family_status = False

                if len(quantity) == 5:  # если длина стала 5'
                    # проверяем тип вошедших данных.
                    # проверяем яаляется ли значение возраста числом
                    if converting_message[1].isdigit() is True:
                        in_age = True
                        # print(converting_message[1].isdigit())
                    else:
                        message = f'Неверно введены данные: < {converting_message[1]} >\nПопробуйте еще раз.'
                        send = cl_send_message(message_from_id=message_from_id, message=message,
                                               token_group=token_group).message_
                        # print(send)

                    # проверяем яаляется ли значение пола строкой
                    if converting_message[2].isdigit() is False:
                        in_sex = True
                        # print(converting_message[2].isdigit())
                    else:
                        message = f'Неверно введены данные: < {converting_message[2]} >\nПопробуйте еще раз.'
                        send = cl_send_message(message_from_id=message_from_id, message=message,
                                               token_group=token_group).message_
                        # print(send)

                    # проверяем яаляется ли значение города строкой
                    if converting_message[3].isdigit() is False:
                        in_city = True
                        # print(converting_message[3].isdigit())
                    else:
                        message = f'Неверно введены данные: < {converting_message[3]} >\nПопробуйте еще раз.'
                        send = cl_send_message(message_from_id=message_from_id, message=message,
                                               token_group=token_group).message_
                        # print(send)

                    # проверяем яаляется ли значение пола числом
                    if converting_message[4].isdigit() is True:
                        family_status = True
                        # print(converting_message[4].isdigit())
                    else:
                        message = f'Неверно введены данные: < {converting_message[4]} >\nПопробуйте еще раз.'
                        send = cl_send_message(message_from_id=message_from_id, message=message,
                                               token_group=token_group).message_
                        # print(send)

                    # если все значения являются истиной то начинаем поиск
                    if in_age and in_sex and in_city and family_status is True:
                        # отправляем преобразованные данные на поиск юзеров
                        # find_user = cl_find_all_user(user_list=None, token_user=token_user).find
                        # полученные данные вставляем в сообщение и отправляем пользователю в ответе
                        print(
                            f'Значение {converting_message[0]}, возраст {converting_message[1]}, пол {converting_message[2]}, Город {converting_message[3].title()}, положение {converting_message[4]}')

                        # из полученного значения возраста получаем год рождения
                        current_datetime = datetime.now().year  # определяем текущий год
                        birth_year = int(current_datetime) - int(converting_message[1])  # получаем год рождения

                        hometown = converting_message[3].title()

                        # смотрим значение пола М или Ж и меняем его на число 1 — женщина, 2 — мужчина, 0 — любой (по умолчанию).
                        sex = 0
                        if converting_message[2] == 'м':
                            sex = 2
                        elif converting_message[2] == 'ж':
                            sex = 1

                        offset = 0
                        status = int(converting_message[4])
                        # message = (f'Значение {converting_message[0]}, возраст {converting_message[1]}, пол {converting_message[2]}, Город {converting_message[3].title()}, положение {converting_message[4]}, год рождения {birth_year}')
                        # print(send)
                        find_user = cl_find_all_user(token_user=token_user, hometown=hometown, birth_year=birth_year,
                                                     sex=sex, status=status, offset=offset).find

                        print(f' non {find_user[0]}')
                        print()
                        print(f' NO non {find_user}')
                        # ++++++++++++++
                        if find_user is None:
                            print(f'len = none')
                            # offset = int(find_user) + 1
                            offset = int(find_user[0]["offset"]) + 1
                            print(f'offset  {offset}')
                            # print(offset)
                            # find_user = cl_find_all_user(token_user=token_user, hometown=hometown, birth_year=birth_year, sex=sex, status=status, offset=offset).find
                        #
                        else:
                            print(f'len = not none')
                            print(f'len = {len(find_user)}')
                            last_name = find_user[0]["last_name"]
                            first_name = find_user[0]["first_name"]
                            photo_max = find_user[0]["photo_max"]
                            offset = find_user[0]["offset"]
                            user_id = find_user[0]["user_id"]
                            print(last_name)
                            # **********************************************
                            vk_data = {"token_user": f"{token_user}",
                                       "token_group": f"{token_group}",
                                       "hometown": f"{hometown}",
                                       "birth_year": f"{birth_year}",
                                       "sex": f"{sex}",
                                       "status": f"{status}",
                                       "offset": f"{int(offset) + 1}"
                                       }
                            with open('find_vk_data.json', 'w', encoding='utf-8') as outfile:
                                json.dump(vk_data, outfile)
                            # ***********************************************
                            # ==========ОТПРАВЛЯЕМ ФОТО===========
                            # # получаем ссылку для загрузки

                            # + делаем фото
                            vk_session = VkApi(token=token_group)
                            vk = vk_session.get_api()
                            upload = VkUpload(vk)
                            img = requests.get(photo_max).content
                            f = BytesIO(img)
                            response = upload.photo_messages(f)[0]
                            owner_id = response['owner_id']
                            photo_id = response['id']
                            access_key = response['access_key']

                            message_out = f'@id{user_id}({last_name} {first_name})'
                            attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                            # +
                            cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                                            token_group=token_group).message_
                            # ***********************************************

                        # +++++++++++++++++++++++++++++++++++++++++++++++++
                        # print(f'2 f_u {find_user}')
                        # print(find_user)
                        print()
                        start()




                    else:
                        start()



                else:
                    message = '+Неверно введены данные\n' \
                              'Попробуйте еще раз.'
                    send = cl_send_message(message_from_id=message_from_id, message=message,
                                           token_group=token_group).message_
                    print(send)
            else:
                message = 'Возможные команды "найди", "старт"\n' \
                          'Введите запрос еще раз.'
                send = cl_send_message(message_from_id=message_from_id, message=message,
                                       token_group=token_group).message_
                print(send)

            # ----------------------------------------------------------------

            # ----------------------------------------------------------------
            # # print(f'Значение {message_in[0]}, возраст {message_in[1]}, пол {message_in[2]}, Город {message_in[3]}')
            # colon = message_in.replace(':', ',')   #заменяем двоеточие на запятую
            # space_character = colon.replace(' ', '')  #убираем все пробелы
            # li_message = space_character.split(sep=',', maxsplit=-1)
            # print(f'Преобразовали в {li_message}')
            # print(li_message[0:3])
            # #проверяем длину входящего сообщения

            # if message_in == 'привет':
            #     find_user = cl_find_all_user(user_list=None, token_user=token_user).find
            #     print(find_user)
            # elif message_in == 'старт':                                                   # если тело сообщения 'поиск'
            #     message = 'пиши  НАЙДИ: через запятую возраст, пол(м/ж), город, семейное положение. Пример:\n' \
            #               'НАЙДИ: 20, ж, Москва, 1'
            #     send = cl_send_message(message_from_id=message_from_id, message=message, token_group=token_group).message_
            #     print(send)
            ts = int(ts) + 1
            bots_longpoll_api(ts, key, server)  # DEL-----


        # ----------------------------------------------------------------
        elif input_message_serv == 'message_reply':  # если тип сообщения - новое сообщение от сообщества(чтобы не реагировал на свои сообщения)
            message_out = resp.json()['updates'][0]['object']['text']
            print(message_out)
            temp_0 = resp.json()['updates'][0]
            pprint(f'out mess {temp_0}')
            ts = int(ts) + 1
            print(ts)
            bots_longpoll_api(ts, key, server)
            # start() # DEL-----
    # если не пришло сообщение или таймер в параметрах "wait": 25(сек) истек, то перезагружаем сервер
    else:
        pprint(bum)
        print('restart server')
        bots_longpoll_api(ts, key, server)
        # start()
    # #----------------------------------------------------------------


start()
