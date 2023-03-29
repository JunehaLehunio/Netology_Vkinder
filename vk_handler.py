import requests
from vk_api import VkApi
from vk_api.upload import VkUpload
from io import BytesIO
from vk_api.utils import get_random_id
import json
from data_db import check_insert_user_table
from operator import itemgetter

""" ОТПРАВКА СООБЩЕНИЙ"""


def send_message(message, attachment, for_the_user_id, token_group):
    vk_session = VkApi(token=token_group)
    vk = vk_session.get_api()
    vk.messages.send(
        random_id=get_random_id(),
        peer_id=for_the_user_id,
        attachment=attachment,
        message=message
    )
    # return


"""КЛАСС ПОИСКА ПОЛЬЗОВАТЕЛЕЙ"""


class cl_find_all_user():
    def __init__(self, token_user, token_group, for_the_user_id, password, query_city):
        self.token_user = token_user
        self.password = password
        self.token_group = token_group
        self.for_the_user_id = for_the_user_id
        self.query_city = query_city

    """СБОР ИНФОРМАЦИИ О ПОЛЬЗОВАТЕЛЕ, ДЛЯ КОТОРОГО БУДЕТ ВЕСТИСЬ ПОИСК"""

    def user_info(self):
        params = {
            "access_token": self.token_user,
            "user_ids": self.for_the_user_id,
            "fields": 'sex',
            "v": "5.131"
        }
        perform = requests.get("https://api.vk.com/method/users.get", params)
        try:
            response_data = perform.json()["response"][0]
            data = [{'sex': 3 - response_data['sex']}]
            with open(f'find_id{self.for_the_user_id}.json', 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile)
            first_name = response_data['first_name']
        except Exception as err:
            print("Возникла ошибка проверки данных пользователя", err)
            return False
        return first_name

    """ПОИСК КОДА ГОРОДА ПО ЗАПРОСУ ИЗ ТЕЛА СООБЩЕНИЯ"""

    def find_city(self):
        param = {'access_token': self.token_user,
                 'q': self.query_city,
                 'count': 1,
                 'v': 5.131
                 }
        rec_city = requests.get("https://api.vk.com/method/database.getCities", param)
        print(rec_city.json())
        try:
            city_id = rec_city.json()["response"]["items"][0]['id']
            return city_id
        except Exception as err:
            print("Возникла ошибка поиска города", err)
            return False

    """ПОИСК ПОЛЬЗОВАТЕЛЕЙ ПО КРИТЕРИЯМ"""

    def find_new_user(self):
        # =============Читаем данные из файла, изменяем офсет и записываем снова в файл=====================
        with open(f'find_id{self.for_the_user_id}.json', 'r') as file_j:
            read_json = file_j.read()
        find_vk_offset = json.loads(read_json)
        city_id = find_vk_offset[0]['city_id']
        birth_year = find_vk_offset[0]['birth_year']
        offset = find_vk_offset[0]['offset']
        sex = find_vk_offset[0]['sex']

        params = {
            "sort": 0,
            "offset": offset,
            "city_id": city_id,
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
        perform = requests.get("https://api.vk.com/method/users.search", params)
        # print(perform.json())
        try:
            response_data = perform.json()["response"]["items"]
        except Exception as err:
            print("Возникла ошибка поиска пользователей", err)
            return False

        # Получаем информацию о найденном пользователе
        is_closed = response_data[0]["is_closed"]
        user_id = response_data[0]["id"]
        last_name = response_data[0]["last_name"]
        first_name = response_data[0]["first_name"]

        # Проверяем ID найденного пользователя в БД
        check_user_in_db = check_insert_user_table(int(self.password), user_id, first_name,
                                                   last_name).check_users()

        # Если профиль пользователя закрыт или уже был добавлен в БД, то делаем смещение поиска и начинаем новый поиск
        if is_closed == True or check_user_in_db == "available":
            data = [{
                'city_id': city_id,
                'birth_year': birth_year,
                'offset': int(offset) + 1,
                'sex': sex
            }]
            with open(f'find_id{self.for_the_user_id}.json', 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile)
            user_id, first_name, last_name = cl_find_all_user(self.token_user, self.token_group, self.for_the_user_id,
                                                              self.password, self.query_city).find_new_user()

        # Если профиль пользователя открыт или отсутствует в БД, то добавляем нового пользователя в таблицу
        elif check_user_in_db == "absent":
            check_insert_user_table(int(self.password), user_id, first_name, last_name).insert_users()
        return user_id, first_name, last_name


# Получаем идентификаторы всех альбомов найденного пользователя. Ищем фото и выбираем топ 3
def find_all_album(token_user, token_group, user_id, message, for_the_user_id):
    vk_session = VkApi(token=token_group)
    vk = vk_session.get_api()
    upload = VkUpload(vk)

    params_album = {
        "owner_id": user_id,
        "need_system": 1,
        "album_ids": "size",
        "access_token": token_user,
        "v": "5.131"
    }

    resp = requests.get("https://api.vk.com/method/photos.getAlbums", params_album)
    response_data = resp.json()["response"]["items"]
    album_list = []
    for iter_user in range(len(response_data)):  # получаем количество альбомов
        id_album = response_data[iter_user]["id"]
        size = response_data[iter_user]["size"]
        title = response_data[iter_user]["title"]
        album = {"id_album": int(id_album), "size": size, "title": title}
        album_list.append(album)

    like_and_comments = []
    for numerator_album_list in range(len(album_list)):
        response_album = album_list[numerator_album_list]['id_album']

        # Получаем все фото по найденным id альбомов
        params = {
            "owner_id": user_id,
            "album_id": response_album,
            "extended": 1,
            "no_service_albums": 0,
            "access_token": token_user,
            "v": "5.131"
        }

        resp = requests.get("https://api.vk.com/method/photos.get", params).json()
        response_data = resp["response"]["items"]

        # Получаем максимальный размер фото
        for numerator_response_data in range(len(response_data)):
            quantity = []
            for numerator_sizes in range(len(response_data[numerator_response_data]["sizes"])):
                quantity.append(numerator_sizes)
            max_size_photo = max(quantity)
            raw_url_photo_vk = response_data[numerator_response_data]["sizes"][max_size_photo]["url"]
            likes = response_data[numerator_response_data]["likes"]["count"]
            comments = response_data[numerator_response_data]["comments"]["count"]
            like_and_comments.append({"likes_comments_summ": (likes + comments), "raw_url_photo_vk": raw_url_photo_vk})

    # Получаем 3 фото с максимальным суммарным количеством лайков и комментариев
    prepared_dictionary_attach = []
    sorted_glossary = sorted(like_and_comments, key=itemgetter('likes_comments_summ'), reverse=True)
    prepared_dictionary_attach.append(sorted_glossary[:3])

    # Преобразуем полученные ссылки фото и формируем список с последующей отправкой пользователю
    attachment = []
    for numerator in prepared_dictionary_attach[0]:
        url = numerator['raw_url_photo_vk']
        print(url)
        img = requests.get(url).content
        resave_bytes_photo = BytesIO(img)
        response = upload.photo_messages(resave_bytes_photo)[0]
        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']
        url_attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        print(url_attachment)
        attachment.append(url_attachment)
    return send_message(message, attachment, for_the_user_id, token_group)
