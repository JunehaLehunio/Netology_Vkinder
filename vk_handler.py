import requests
from vk_api import VkApi
from vk_api.upload import VkUpload
from io import BytesIO
from vk_api.utils import get_random_id
import json
from data_db import check_insert_user_table
from operator import itemgetter
from datetime import datetime

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
    print('Отправлено сообщение пользователю')


def check_data_user(for_the_user_id, token_group):
    # =============Читаем данные из файла, изменяем офсет и записываем снова в файл=====================
    with open(f'find_id{for_the_user_id}.json', 'r') as file_j:
        read_json = file_j.read()
    find_vk_offset = json.loads(read_json)
    city_id = find_vk_offset[0]['city_id']
    birth_year = find_vk_offset[0]['birth_year']
    check = False
    attachment = ''
    if city_id == "None":
        message = 'Введите слово "город" и название города, в котором будет происходить поиск.\nНапример: "город Чита"'

    elif birth_year == "None":
        message = 'Введите слово "год" и год своего рождения.\nНапример: "год 1990"'
    else:
        check = True
        message = "Начинаем поиск. Это может занять какое-то время."
    send_message(message, attachment, for_the_user_id, token_group)
    return check


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
            "fields": 'sex, bdate, city',
            "v": "5.131"
        }
        perform = requests.get("https://api.vk.com/method/users.get", params)
        try:
            response_data = perform.json()["response"][0]
            first_name = response_data['first_name']
            if 'city' in response_data:
                city_id = response_data['city']['id']
            else:
                city_id = 'None'
            if 'bdate' in response_data:
                bdate = int(response_data['bdate'][-4:])
            else:
                bdate = 'None'

            data = [{'sex': 3 - response_data['sex'],
                     'city_id': city_id,
                     'birth_year': bdate,
                     "offset": 0
                     }]

            with open(f'find_id{self.for_the_user_id}.json', 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile)

        except KeyError as err:
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
        try:
            city_id = rec_city.json()["response"]["items"][0]['id']
            return city_id
        except Exception as err:
            print("Возникла ошибка поиска города", err)
            return False

    """ПОИСК ПОЛЬЗОВАТЕЛЕЙ ПО КРИТЕРИЯМ"""

    def find_new_user(self):

        with open(f'find_id{self.for_the_user_id}.json', 'r') as file_j:
            read_json = file_j.read()
        find_vk_offset = json.loads(read_json)
        city_id = find_vk_offset[0]['city_id']
        birth_year = find_vk_offset[0]['birth_year']
        offset = find_vk_offset[0]['offset']
        sex = find_vk_offset[0]['sex']

        current_datetime = datetime.now().year
        params = {
            "sort": 0,
            "offset": offset,
            "city": city_id,
            "age_from": (current_datetime - birth_year) - 3,
            "age_to": (current_datetime - birth_year) + 3,
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

        check_list = True
        try:
            response_data = perform.json()["response"]["items"]
        except Exception as err:
            print("Возникла ошибка поиска пользователей", err)
            check_list = False
            user_id = False
            first_name = False
            last_name = False
            return user_id, first_name, last_name, check_list
        # Получаем информацию о найденном пользователе
        try:
            is_closed = response_data[0]["is_closed"]
            user_id = response_data[0]["id"]
            last_name = response_data[0]["last_name"]
            first_name = response_data[0]["first_name"]
        except Exception as err:
            print("Список пуст", err)
            check_list = False
            user_id = False
            first_name = False
            last_name = False
            return user_id, first_name, last_name, check_list
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
            user_id, first_name, last_name, check_list = cl_find_all_user(self.token_user, self.token_group,
                                                                          self.for_the_user_id,
                                                                          self.password,
                                                                          self.query_city).find_new_user()

        # Если профиль пользователя открыт или отсутствует в БД, то добавляем нового пользователя в таблицу
        elif check_user_in_db == "absent":
            check_insert_user_table(int(self.password), user_id, first_name, last_name).insert_users()
        return user_id, first_name, last_name, check_list


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
    try:
        response_data = resp.json()["response"]["items"]
        album_list = []
        for iter_user in range(len(response_data)):  # получаем количество альбомов
            id_album = response_data[iter_user]["id"]
            size = response_data[iter_user]["size"]
            title = response_data[iter_user]["title"]
            album = {"id_album": int(id_album), "size": size, "title": title}
            album_list.append(album)
    except Exception as err:
        print(err)
        return False

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
        try:
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
                like_and_comments.append(
                    {"likes_comments_summ": (likes + comments), "raw_url_photo_vk": raw_url_photo_vk})
        except Exception as err:
            print(err)
            return False

    # Получаем 3 фото с максимальным суммарным количеством лайков и комментариев
    prepared_dictionary_attach = []
    sorted_glossary = sorted(like_and_comments, key=itemgetter('likes_comments_summ'), reverse=True)
    prepared_dictionary_attach.append(sorted_glossary[:3])

    # Преобразуем полученные ссылки фото и формируем список с последующей отправкой пользователю
    attachment = []
    num_photo = 1
    for numerator in prepared_dictionary_attach[0]:
        url = numerator['raw_url_photo_vk']
        img = requests.get(url).content
        resave_bytes_photo = BytesIO(img)
        response = upload.photo_messages(resave_bytes_photo)[0]
        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']
        url_attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        attachment.append(url_attachment)
        print(f'Получено фото {num_photo}: {url_attachment}')
        num_photo += 1
    return send_message(message, attachment, for_the_user_id, token_group)
