import json
from vk_handler import cl_send_message, cl_find_all_user
from datetime import datetime  # для получения даты рождения


def processing_message(converting_message, token_group, token_user, message_from_id, password):
    if 'старт' in converting_message:
        pass

    elif 'помощь' in converting_message:
        message_out = 'список поддерживаемых команд:\n' \
                      '<старт> - Приветствие и краткое описание бота\n' \
                      '<найди:> - Поиск по критериям. После команды через запятую указывается возраст, город и пол (м или ж) например:\n' \
                      'найди: 25, Москва, ж\n' \
                      '<еще> - Найти следующего претендента с характеристиками, введенными в предыдущем поиске\n' \
                      '<помощь> - Список и описание команд'

        attachment = ''
        cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                        token_group=token_group).message_

    elif 'найди' in converting_message:
        # ======================          ПРОВЕРКИ ВХОДЯЩИХ ДАННЫХ     =====================
        # проверяем итераций в полученном списке и записываем их в список длины
        quantity = []
        for quantity_iter in range(len(converting_message)):
            quantity.append(quantity_iter)
        print(len(quantity))
        if len(quantity) == 4:  # если длина стала 4'
            # Делаем триггеры, запускающий поиск. Во время проверок его значение изменяется на истину или остается ложью. Если одно из значений будет ложью, то не запустится поиск
            in_age = False
            in_city = False
            in_sex = False

            # Проверяем тип вошедших данных.
            # Проверяем является ли значение возраста числом
            if converting_message[1].isdigit() is True:
                in_age = True
            else:
                attachment = ''
                message_out = f'Неверно введены данные: < {converting_message[1]} >\nПопробуйте еще раз.'
                cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                                token_group=token_group).message_

            # проверяем является ли значение города строкой
            if converting_message[2].isdigit() is False:
                in_city = True
                # print(converting_message[3].isdigit())
            else:
                attachment = ''
                message_out = f'Неверно введены данные: < {converting_message[2]} >\nПопробуйте еще раз.'
                cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                                token_group=token_group).message_

            # проверяем является ли значение пола строкой
            if converting_message[3].isdigit() is False:
                in_sex = True
                # print(converting_message[2].isdigit())
            else:
                attachment = ''
                message_out = f'Неверно введены данные: < {converting_message[3]} >\nПопробуйте еще раз.'
                cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                                token_group=token_group).message_

            # если все значения являются истиной, то начинаем поиск
            if in_age and in_city and in_sex is True:

                current_datetime = datetime.now().year  # определяем текущий год
                # получаем год рождения по полученному возрасту из сообщения
                birth_year = int(current_datetime) - int(converting_message[1])
                hometown = converting_message[2].title()  # Название города делаем с заглавной буквы
                offset = 0  # устанавливаем смещение поиска на 0

                # смотрим значение пола М или Ж и меняем его на число 1 — женщина, 2 — мужчина, 0 — любой (по умолчанию).

                if converting_message[3] == 'м':
                    sex = 2
                elif converting_message[3] == 'ж':
                    sex = 1
                else:
                    sex = 0
                # Отправляем сообщение, что начинаем поиск
                message_info = (
                    f'Ищем пользователя: дата рождения: {converting_message[1]}, город {converting_message[2].title()}, пол {converting_message[3]}\nЭто может занять какое-то время.')
                attachment = ''
                message_out = message_info
                cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                                token_group=token_group).message_
                # -------------------------------------------------------------------

                data = []  # Делаем список полученных данных для дальнейшей записи в json
                data.append({
                    'hometown': f'{hometown}',
                    'birth_year': birth_year,
                    'offset': offset,
                    'sex': sex
                })
                # Записываем все в json
                with open('find_vk_offset.json', 'w', encoding='utf-8') as outfile:  # записываем все в find_vk.json
                    json.dump(data, outfile)  # ensure_ascii=False для того, чтобы не ломалась кириллическая кодировка

                # Выполняем поиск по заданным критериям
                user_id, first_name, last_name = cl_find_all_user(token_user=token_user, password=password).find()
                # Получаем данные найденного пользователя и отправляем сообщение
                attachment = ''
                message_out = f'@id{user_id}({last_name} {first_name})'
                cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                                token_group=token_group).message_

            else:
                # Получаем данные найденного пользователя и отправляем сообщение
                attachment = ''
                message_out = 'Произошло невообразимое!'
                cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                                token_group=token_group).message_

        else:
            attachment = ''
            message_out = f'Неверно введены данные. Попробуйте еще раз.'
            cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                            token_group=token_group).message_
    elif 'еще' in converting_message:
        # =============Читаем данные из файла, изменяем офсет и записываем снова в файл=====================
        with open('find_vk_offset.json', 'r') as file_j:
            read_json = file_j.read()
        find_vk_offset = json.loads(read_json)
        hometown = find_vk_offset[0]['hometown']
        birth_year = find_vk_offset[0]['birth_year']
        offset = find_vk_offset[0]['offset']
        sex = find_vk_offset[0]['sex']
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
        # Выполняем поиск по заданным критериям
        user_id, first_name, last_name = cl_find_all_user(token_user=token_user, password=password).find()
        # Получаем данные найденого пользователя и отправляем сообщение
        attachment = ''
        message_out = f'@id{user_id}({last_name} {first_name})'
        cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                        token_group=token_group).message_
    else:
        message_out = 'Такая команда отсутствует, попробуйте еще раз.\nДля получения справки и списку команд напишите без кавычек слово "помощь".'
        attachment = ''
        cl_send_message(message_from_id=message_from_id, message=message_out, attachment=attachment,
                        token_group=token_group).message_

        return
