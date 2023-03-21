from random import randrange
import requests
import datetime
import json
from pprint import pprint


class cl_find_all_user():
    def __init__(self, token_user, hometown, birth_year, sex, status, offset):
        # self.user_list = user_list
        self.token_user = token_user
        self.hometown = hometown
        self.birth_year = birth_year
        self.sex = sex
        self.status = status
        self.offset = offset

    # парсим API поиск по VK
    @property
    def find(self):
        params = {
            "sort": 0,  # Сортировка результатов. Возможные значения: 1 — по дате регистрации, 0 — по популярности.
            "offset": self.offset,  # смещение
            # "city_id": 158,  # id г.Челябинск
            "hometown": self.hometown,  # название города буквами
            # "age_from": 28,                                 # возраст ОТ
            # "age_to": 30,                                   # возраст ДО
            'birth_year': self.birth_year,  # год рождения
            "has_photo": 1,  # 1 — искать пользователей только с фотографией
            "count": 1,  # + какое количество записей получить
            "sex": self.sex,  # + пол 0 — пол не указан. 1 — женский, 2 — мужской
            "online": 0,  # 1 — искать только пользователей онлайн, 0 — искать по всем пользователям.
            "status": self.status,  # статус семейное положение
            "fields": "blacklisted, blacklisted_by_me, bdate, city, domain, friend_status, has_photo, photo_max, is_closed",
            "access_token": self.token_user,
            "v": "5.131"
        }
        pprint(f" hometown {self.hometown} birth_year {self.birth_year} sex {self.sex} status {self.status}")

        resp = requests.get("https://api.vk.com/method/users.search", params)
        response_data = resp.json()["response"]["items"]
        pprint(response_data)
        # ===========   итерация по вытаскиванию отдельных полей по пользователю  ==================
        # user_list = []
        is_closed = response_data[0]["is_closed"]  # Скрыт ли профиль пользователя настройками приватности.
        print(is_closed)
        # blacklisted = response_data[0]["blacklisted"]                   # находится ли текущий пользователь в черном списке.
        # blacklisted_by_me = response_data[0]["blacklisted_by_me"]       # находится ли пользователь в черном списке у текущего пользователя
        friend_status = response_data[0][
            "friend_status"]  # Статус дружбы с пользователем 0 — не является другом, 1 — отправлена заявка/подписка пользователю,2 — имеется входящая заявка/подписка от пользователя,3 — является другом.
        has_photo = response_data[0][
            "has_photo"]  # Информация о том, установил ли пользователь фотографию для профиля. 1 — установил, 0 — не установил.
        user_id = response_data[0]["id"]  # id
        last_name = response_data[0]["last_name"]  # Фамилия
        first_name = response_data[0]["first_name"]  # Имя
        bdate = response_data[0]["bdate"]  # Дата рождения
        # city = response_data[iter_user]["city"]  #  Информация о городе (доработать. Лезет ошибка, тк не у всех указан город)
        # domain = response_data[0]["domain"]  # Короткий адрес страницы
        photo_max = response_data[0]["photo_max"]  # URL квадратной фотографии с максимальной шириной.

        user_id_li = []
        if is_closed == True:
            # cl_find_all_user.find(self.token_user, self.hometown, self.birth_year, self.sex, self.status, self.offset)

            self.offset += 1
            return cl_find_all_user(self.token_user, self.hometown, self.birth_year, self.sex, self.status,
                                    self.offset).find

        elif is_closed == False:

            user = {"last_name": last_name, "first_name": first_name, "is_closed": is_closed, "bdate": bdate,
                    "user_id": user_id, "photo_max": photo_max, "offset": self.offset}

            print(f'1_fu  {user}')
            user_id_li.append(user)
            print(user_id_li)
            print("возвращаем значение")
            return user_id_li

        else:
            print('ERROR')
        # else:
        #         self.offset += 1
        #         cl_find_all_user(self.token_user, self.hometown, self.birth_year, self.sex, self.status, self.offset)
        # print(user_list)

        # with open('find_vk.json','w', encoding='utf-8') as outfile:                 #записываем все в find_vk.json
        #     json.dump(user_list, outfile, ensure_ascii=False)                       #ensure_ascii=False для того, чтобы не ломалась кириллическая кодировка

        # return self.user_list


class cl_send_message():
    def __init__(self, message_from_id, message, attachment, token_group):
        self.message_from_id = message_from_id
        self.message = message
        self.attachment = attachment
        self.token_group = token_group

    @property
    def message_(self):
        random_id = randrange(10 ** 7)

        param_messages = {
            "access_token": self.token_group,
            "user_id": self.message_from_id,
            "message": self.message,
            "attachment": self.attachment,
            "dont_parse_links": 0,
            # "content_source": 'FFFfFF',
            # "intent": 'default',
            "random_id": random_id,
            "v": "5.131"
        }

        respu = requests.get('https://api.vk.com/method/messages.send', params=param_messages)
        print(respu)
        return f'ОК'


class cl_send_Photo():
    def __init__(self, peer_id, access_token):
        self.peer_id = peer_id
        self.access_token = access_token

    @property
    def start_UploadServer(self):
        param_messages = {
            "access_token": self.access_token,
            "peer_id": self.peer_id,
            "v": "5.131"
        }

        respu = requests.get('https://api.vk.com/method/photos.getMessagesUploadServer', params=param_messages)
        answer_server = respu.json()
        # print(answer_server)
        return answer_server
        # pprint(message)
