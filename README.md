# Краткое описание работы чат-бота "Vkinder". 

**Файлы:**

1. **customizing_setting** - файл с настройками токенов, паролей;

2. **main** - стартовый файл;

3. **message_request_processing** - файл для обработки тела сообщений;

4. **vk_handler** - файл для работы с запросами ВК;

5. **data_db** - файл работы с БД;

6. **requirements.txt** - файл зависимостей;



**_Поиск не чувствителен к регистру._**



Команды:
                  
**начать** - Старт бота и сбор необходимой информации для поиска партнера.;

**город название населенного пункта** - Команда изменения города, в котором происходит поиск. Формат записи <город Москва>;

**год год рождения** - Команда изменения года рождения искомых пользователей. Формат записи <год 2000>;
                                         
**да** - повторный поиск с предыдущими параметрами. После успешного поиска пользователя, спрашивается у пользователя о
       повторе поиска. Программа ожидает ответ 'да';
       
**помощь** - вывод списка команд



При первом запуске бота происходит установка базы данных и таблицы.

После установки соединения с сервером программа ожидает входящее сообщение.
Если соединение с сервером не установлено, то дается 3 попытки с интервалом в 2 секунды между попытками.

При получении сообщения от группы, происходит перезагрузка соединения с изменением счетчика номера сообщения.
При получении сообщения от пользователя, происходит первичная проверка длины содержимого сообщения.

Ожидается, что первое сообщение от пользователя будет "начать".
После этого программа проверяет пол пользователя и его имя, год рождения и город. Имя используется в приветствии.
Полученный пол пользователя автоматически преобразуется в противоположный и записывается в файл.
При отсутствии в профиле пользователя года рождения, либо города проживания, предлагается ввести их.

Год рождения для поиска пользователей установлен в интервале +- 3 года от указанного в профиле пользователя или которой указал пользователь при изменении критериев поиска. 
В обработчике полученное название города проверяется на наличие в базах городов из VK API. При успешной проверке
получаем код города, в котором будет производиться поиск.
    Все данные записываются в уникальный json файл с идентификатором прользователя в названии, что позволяет использовать параметры поиска после завершения работы с ботом и использовать все личные настройки только данным пользователем при последующем подключении к боту.

Изначально офсет установлен на 0. При этом выводится самый популярный пользователь по указанным критериям.
Если профиль пользователя открыт, то происходит поиск ID пользователя в БД. Если пользователь отсутствует в БД, то
туда добавляется запись для предотвращения повтора вывода пользователя в сообщении. После этого начинается проверка всех фото пользователя и выборки 3 фото с максимальным суммарным количеством лайков и комментариев с дальнейшей отправкой сообщения со всеми данными пользователю.
    В том случае, если профиль пользователя закрыт, либо его ID уже есть в БД, происходит смещение офсет на +1 и поиск повторяется.
    Если сообщение содержит слово "да", то повторяется поиск по критериям поиска, которые были указаны ранее. При этом
также идет смещение офсет на +1.
    Значение офсет сбрасывается на 0, если были изменены параметры поиска или введены повторно те же значения возраста
и населенного пункта, а также при отправке команды "начать". Это позволяет провести повторный поиск с самого начала, при этом пользователи,
которые уже есть в БД, не будут повторно выводиться в сообщениях. Такой подход позволит найти тех
пользователей, у которых стала выше популярность и они поднялись в поисковых запросах к первым местам.

Для того, чтобы изменить город, в котором будет производиться поиск пользователей, отправляется сообщение с командой "город" и названием города.
Изменение критериев поиска по интервалу года рождения происходит аналогично - отправляется команда "год" и указывается год рождения.

