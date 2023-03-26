from random import randrange
import requests
import vk_api
from pprint import pprint
import json
from data_db import check_insert_user_table

"""КЛАСС ОТПРАВКИ СООБЩЕНИЙ"""


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
            "random_id": random_id,
            "v": "5.131"
        }

        respu = requests.get('https://api.vk.com/method/messages.send', params=param_messages)
        print(respu)
        return f'ОК'


"""КЛАСС ПОИСКА ПОЛЬЗОВАТЕЛЕЙ"""


class cl_find_all_user():
    def __init__(self, token_user, password):
        self.token_user = token_user
        self.password = password

    def find(self):
        # =============Читаем данные из файла, изменяем офсет и записываем снова в файл=====================
        with open('find_vk_offset.json', 'r') as file_j:
            read_json = file_j.read()
        find_vk_offset = json.loads(read_json)
        hometown = find_vk_offset[0]['hometown']
        birth_year = find_vk_offset[0]['birth_year']
        offset = find_vk_offset[0]['offset']
        sex = find_vk_offset[0]['sex']

        params = {
            "sort": 0,
            "offset": offset,
            "hometown": hometown,
            'birth_year': birth_year,
            "has_photo": 0,
            "count": 1,
            "sex": sex,
            "online": 0,
            "status": 6,
            "fields": "bdate, friend_status, has_photo, photo_max, is_closed",
            "access_token": self.token_user,
            "v": "5.131"
        }
        # print(f" offset {self.offset}, hometown {self.hometown}, birth_year {self.birth_year}, sex {self.sex}, access_token {self.token_user}")

        perform = requests.get("https://api.vk.com/method/users.search", params)
        # print(perform.json())
        response_data = perform.json()["response"]["items"]
        # pprint(response_data)
        # ===========   итерация по вытаскиванию отдельных полей по пользователю  ==================
        is_closed = response_data[0]["is_closed"]
        print(is_closed)
        user_id = response_data[0]["id"]
        last_name = response_data[0]["last_name"]
        first_name = response_data[0]["first_name"]
        bdate = response_data[0]["bdate"]
        photo_max = response_data[0]["photo_max"]

        print(f'----------\nlast_name: {last_name}\nfirst_name: {first_name}\nis_closed: {is_closed}\n')

        check_user_in_db = check_insert_user_table(int(self.password), user_id, first_name,
                                                   last_name).check_users()
        print("check_user_in_db: ")
        print(check_user_in_db)

        if is_closed == True or check_user_in_db == "CLOSED":
            # =============Читаем данные из файла, изменяем офсет и записываем снова в файл=====================
            data = []
            data.append({
                'hometown': hometown,
                'birth_year': birth_year,
                'offset': int(offset) + 1,
                'sex': sex
            })
            with open('find_vk_offset.json', 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile)
            # =================================================================================================

            user_id, first_name, last_name = cl_find_all_user(token_user=self.token_user, password=self.password).find()

        elif check_user_in_db == "OPEN":
            print("возвращаем значение")
            check_insert_user_table(int(self.password), user_id, first_name, last_name).insert_users()
            print("check_user_in_db: ")
            # print(check_user_in_db)
            print(('---' * 10), 'отправляем', ('---') * 10)
            print(
                f'last_name: {last_name}\nfirst_name: {first_name}\nuser_id: https://vk.com/id{user_id}\n=================')
        return user_id, first_name, last_name


# =============================================================================================================================================

# ==================  получаем идентификаторы всех альбомов  ====================
def find_all_album():
    """ЧТЕНИЕ ИЗ ФАЙЛА КЛЮЧЕЙ"""
    """ИЗМЕНИТЬ key_json"""
    with open("C:/Users/Sus/PycharmProjects/All/key.json", 'r') as file:
        read_json = file.read()
    key_data_json = json.loads(read_json)
    token_user = key_data_json['token_user']

    params1 = {
        "owner_id": 472579328,
        "need_system": 1,
        "album_ids": "title, size",
        # "count": 1,
        "access_token": token_user,
        "v": "5.131"
    }

    resp = requests.get("https://api.vk.com/method/photos.getAlbums", params1)
    response_data = resp.json()["response"]["items"]
    pprint(response_data)
    album_list = []
    for iter_user in range(len(response_data)):  # получаем количество альбомов
        id_album = response_data[iter_user]["id"]  # Скрыт ли профиль пользователя настройками приватности.
        size = response_data[iter_user]["size"]  # находится ли текущий пользователь в черном списке.
        title = response_data[iter_user]["title"]
        album = {"id_album": int(id_album), "size": size, "title": title}
        album_list.append(album)
    pprint(album_list)
    print('# ===============')
    # find_all_album()
    photo_list = []
    for s in range(len(album_list)):
        response_a = album_list[s]['id_album']
        print(s)
        # ==================  получаем все фото по найденному id альбома  ====================

        params = {
            "owner_id": 472579328,  # Идентификатор владельца альбома.
            "album_id": response_a,  # Идентификатор альбома
            "extended": 1,  # возраст ОТ
            # "count": 3,                                     #+ какое количество записей получить
            "no_service_albums": 0,
            "access_token": token_user,
            "v": "5.131"
        }

        resp = requests.get("https://api.vk.com/method/photos.get", params).json()
        response_data = resp["response"]["items"]

        # ===========   ПОЛУЧАЕМ МАКСИМАЛЬНЫЙ РАЗМЕР ФОТО И ССЫЛКУ   ==================

        for i_0 in range(len(response_data)):
            quantity = []
            for x_2 in range(len(response_data[i_0]["sizes"])):
                quantity.append(x_2)
            mmm = max(quantity)
            in_url = response_data[i_0]["sizes"][mmm]["url"]
            likes = response_data[i_0]["likes"]["count"]
            comments = response_data[i_0]["comments"]["count"]
            if likes > 0:
                PU_OUT = {"likes": likes, "in_url": in_url, "comments": comments}
                photo_list.append(PU_OUT)

    pprint(photo_list)
