import json

from data_db import create
from vk_handler import cl_find_all_user, find_all_album, send_message, check_data_user
from datetime import datetime  # для получения даты рождения


def processing_message(converting_message, token_group, token_user, for_the_user_id, password):
    global hello_time

    if 'начать' in converting_message:
        attachment = ''
        # определяем текущее время суток для приветствия
        time_now = datetime.today()
        if 22 < time_now.hour <= 24 or 0 < time_now.hour <= 5:
            hello_time = 'Доброй ночи'
        elif 5 < time_now.hour <= 11:
            hello_time = 'Доброе утро'
        elif 11 < time_now.hour <= 15:
            hello_time = 'Добрый день'
        elif 15 < time_now.hour <= 22:
            hello_time = 'Добрый вечер'
        else:
            hello_time = "Приветствую"

        # Собираем информацию о пользователе(пол, имя), для которого ищем партнера
        first_name = cl_find_all_user(token_user=token_user, password=password, token_group=token_group,
                                      for_the_user_id=for_the_user_id, query_city=None).user_info()
        message = f'{hello_time}, {first_name}!\n' \
                  'Вас приветствует бот поиска партнера.\n'
        send_message(message, attachment, for_the_user_id, token_group)
        # Проверяем наличие всех данных о пользователе
        check = check_data_user(for_the_user_id, token_group)
        if check == True:
            user_id, first_name, last_name, check_list = cl_find_all_user(token_user=token_user,
                                                                          password=password,
                                                                          token_group=token_group,
                                                                          for_the_user_id=for_the_user_id,
                                                                          query_city=None).find_new_user()
            # Проверка ошибок в ответе из поиска
            if check_list == False:
                message = 'По данному запросу ничего не найдено.'
                attachment = ''
                send_message(message, attachment, for_the_user_id, token_group)
            else:
                # Собираем все данные найденного пользователя и отправляем сообщение
                message = f'@id{user_id}({last_name} {first_name})\n' \
                          f'Чтобы продолжить поиск, напиши в сообщении слово "да"'
                find_all_album(token_user, token_group, user_id, message, for_the_user_id)


    elif 'город' in converting_message:
        # Проверяем является ли значение города строкой
        if converting_message[1].isdigit() is False:
            query_city = converting_message[1].replace(' ', '').title()

            # Проверяем, существует ли название города в базе данных городов. Если да, то получаем его идентификатор
            city_id = cl_find_all_user(token_user, token_group, for_the_user_id, password, query_city).find_city()
            if city_id:
                with open(f'find_id{for_the_user_id}.json', 'r') as file_j:
                    read_json = file_j.read()
                find_vk_offset = json.loads(read_json)
                birth_year = find_vk_offset[0]['birth_year']
                sex = find_vk_offset[0]['sex']
                data = [{
                    'city_id': city_id,
                    'birth_year': birth_year,
                    'sex': sex,
                    "offset": 0
                }]
                with open(f'find_id{for_the_user_id}.json', 'w', encoding='utf-8') as outfile:
                    json.dump(data, outfile)

                # Проверяем наличие всех данных о пользователе
                check = check_data_user(for_the_user_id, token_group)
                if check == True:
                    user_id, first_name, last_name, check_list = cl_find_all_user(token_user=token_user,
                                                                                  password=password,
                                                                                  token_group=token_group,
                                                                                  for_the_user_id=for_the_user_id,
                                                                                  query_city=None).find_new_user()
                    # Проверка ошибок в ответе из поиска
                    if check_list == False:
                        message = 'По данному запросу ничего не найдено.'
                        attachment = ''
                        send_message(message, attachment, for_the_user_id, token_group)
                    else:
                        # Собираем все данные найденного пользователя и отправляем сообщение
                        message = f'@id{user_id}({last_name} {first_name})\n' \
                                  f'Чтобы продолжить поиск, напиши в сообщении слово "да"'
                        find_all_album(token_user, token_group, user_id, message, for_the_user_id)

            else:
                print(f'Неверно введено название города: {city_id}')
                attachment = ''
                message = f'Неверно введено название города: {query_city.title()}\n' \
                          f'Попробуйте еще раз'
                send_message(message, attachment, for_the_user_id, token_group)

    elif 'год' in converting_message:
        # Определяем текущий год
        current_datetime = datetime.now().year

        # Берем год рождения из сообщения
        age_converting_message = converting_message[1].replace(' ', '')[:4]
        if age_converting_message.isdigit() is True:
            # Проверяем корректность года рождения
            if 1900 <= int(age_converting_message) < (int(current_datetime) - 18):
                with open(f'find_id{for_the_user_id}.json', 'r') as file_j:
                    read_json = file_j.read()
                find_vk_offset = json.loads(read_json)
                city_id = find_vk_offset[0]['city_id']
                sex = find_vk_offset[0]['sex']
                data = [{
                    'city_id': city_id,
                    'birth_year': int(age_converting_message),
                    'sex': sex,
                    "offset": 0
                }]
                with open(f'find_id{for_the_user_id}.json', 'w', encoding='utf-8') as outfile:
                    json.dump(data, outfile)
                # Проверяем наличие всех данных о пользователе
                check = check_data_user(for_the_user_id, token_group)
                if check == True:
                    user_id, first_name, last_name, check_list = cl_find_all_user(token_user=token_user,
                                                                                  password=password,
                                                                                  token_group=token_group,
                                                                                  for_the_user_id=for_the_user_id,
                                                                                  query_city=None).find_new_user()
                    # Проверка ошибок в ответе из поиска
                    if check_list == False:
                        message = 'Ничего не найдено'
                        attachment = ''
                        send_message(message, attachment, for_the_user_id, token_group)
                    else:
                        # Собираем все данные найденного пользователя и отправляем сообщение
                        message = f'@id{user_id}({last_name} {first_name})\n' \
                                  f'Чтобы продолжить поиск, напиши в сообщении слово "да"'
                        find_all_album(token_user, token_group, user_id, message, for_the_user_id)
            else:
                attachment = ''
                message = f'Неверно введена дата рождения: {age_converting_message}'
                send_message(message, attachment, for_the_user_id, token_group)
        else:
            attachment = ''
            message = f'Неверно введена дата рождения: {age_converting_message}'
            send_message(message, attachment, for_the_user_id, token_group)


    elif 'помощь' in converting_message:
        message = 'список поддерживаемых команд:\n' \
                  '<начать> - Старт бота и сбор необходимой информации для поиска партнера.\n' \
                  '<город название города> - Команда изменения города, в котором происходит поиск, например:\n' \
                  'город Москва\n' \
                  'Эту команду потребуется ввести, если в вашем профиле не указан город проживания.\n' \
                  '<год год рождения> - Команда изменения года рождения искомых пользователей, например:\n' \
                  'год 2000\n' \
                  'Год рождения партнеров берется из условия +-3 года от указанного года рождения\n' \
                  '<да> - Найти следующего претендента с характеристиками, введенными в предыдущем поиске\n' \
                  '<очистить> - Очистка истории поиска\n' \
                  '<помощь> - Вывод списка команд и их описание.'
        attachment = ''
        send_message(message, attachment, for_the_user_id, token_group)

    elif 'да' in converting_message:
        message = 'Ищем другого пользователя'
        attachment = ''
        send_message(message, attachment, for_the_user_id, token_group)

        try:
            with open(f'find_id{for_the_user_id}.json', 'r') as file_j:
                read_json = file_j.read()
            find_vk_offset = json.loads(read_json)
            city_id = find_vk_offset[0]['city_id']
            birth_year = find_vk_offset[0]['birth_year']
            offset = find_vk_offset[0]['offset']
            sex = find_vk_offset[0]['sex']
            data = []
            data.append({
                'city_id': city_id,
                'birth_year': birth_year,
                'offset': int(offset) + 1,
                'sex': sex
            })
            with open(f'find_id{for_the_user_id}.json', 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile)

            # Получаем данные найденного пользователя и начинаем поиск фото пользователя с дальнейшей отправкой
            # сообщения фото и ссылкой. Если фото меньше 3, то отправляет те, которые нашлись
            user_id, first_name, last_name, check_list = cl_find_all_user(token_user=token_user, password=password,
                                                                          token_group=token_group,
                                                                          for_the_user_id=for_the_user_id,
                                                                          query_city=None).find_new_user()
            if check_list == False:
                # Получаем данные найденного пользователя и отправляем сообщение
                message = 'Ничего не найдено'
                attachment = ''
                send_message(message, attachment, for_the_user_id, token_group)
            else:
                # Получаем данные найденного пользователя и отправляем сообщение
                message = f'@id{user_id}({last_name} {first_name})\n' \
                          f'Чтобы продолжить поиск, напиши в сообщении слово "да"'
                find_all_album(token_user, token_group, user_id, message, for_the_user_id)

        except Exception as err:
            print(err)
            message = 'Поисковый запрос еще не был сформирован.\n' \
                      'Введите "помощь" для получения списка команд.'
            attachment = ''
            send_message(message, attachment, for_the_user_id, token_group)
            return
    elif 'очистить' in converting_message:
        del_user_table = create(password, for_the_user_id).del_table()
        print(del_user_table)
        message = del_user_table
        attachment = ''
        send_message(message, attachment, for_the_user_id, token_group)
    else:
        message = 'Такая команда отсутствует, попробуйте еще раз.\nДля получения справки и списку команд напишите без кавычек слово "помощь".'
        attachment = ''
        send_message(message, attachment, for_the_user_id, token_group)
