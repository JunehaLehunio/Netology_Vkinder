# Основное описание работы чат-бота "Vkinder". 

**Файлы:**

1. **customizing_setting** - файл с настройками токенов, паролей;

2. **main** - стартовый файл;

3. **message_request_processing** - файл для обработки тела сообщений;

4. **vk_handler** - файл для работы с запросами ВК;

5. **data_db** - файл работы с БД;

6. **requirements.txt** - файл зависимостей;



**_Поиск не чувствителен к регистру._**



Команды:

**начать** - стартовая команда, собирающая информацию о пользователе для формирования поиска по критериям;

**возраст, название населенного пункта** - критерии поиска в формате **_<int, str>_**. Второе ожидаемое сообщение от
                                         пользователя;
                                         
**да** - повторный поиск с предыдущими параметрами. После успешного поиска пользователя, спрашивается у пользователя о
       повторе поиска. Программа ожидает ответ 'да';
       
**помощь** - вывод списка команд



При первом запуске бота происходит установка базы данных и таблицы.

После установки соединения с сервером программа ожидает входящее сообщение.

При получении сообщения от группы, происходит перезагрузка соединения с изменением счетчика номера сообщения.
При получении сообщения от пользователя, происходит первичная проверка сообщения.

Ожидается, что первое сообщение от пользователя будет "начать".
После этого программа проверяет пол пользователя и его имя. Имя используется в приветствии.
Полученный пол пользователя автоматически преобразуется в противоположный и записывается в файл.

Далее ожидается, что будет сообщение с параметрами поиска.
Вначале любое сообщение проверяется на наличие цифр в первых двух символах сообщения.
Если проверка прошла, то проверяется величина числа. Для ограничения возраста искомых пользователей, стоит нижний
порог возраста от 18 лет, верхний порог поиска - 99 лет.
Если все первичные проверки пройдены, то значение отправляется в обработчик сообщений.
    В обработчике полученное название города проверяется на наличие в базах городов из VK API. При успешной проверке
получаем код города, в котором будет производиться поиск.
    Все данные записываются в уникальный json файл с идентификатором прользователя в названии, что позволяет использовать параметры поиска после завершения работы с ботом и использовать все личные настройки только данным пользователем при последующем подключении к боту.

Изначально офсет установлен на 0. При этом выводится самый популярный пользователь по указанным критериям.
Если профиль пользователя открыт, то происходит поиск ID пользователя в БД. Если пользователь отсутствует в БД, то
туда добавляется запись для предотвращения повтора вывода пользователя в сообщении. После этого начинается проверка всех фото пользователя и выборка топ 3 фото с дальнейшей
отправкой сообщения со всеми данными соискателю.
    В том случае, если профиль пользователя закрыт, либо его ID уже есть в БД, происходит смещение офсет на +1 и поиск
повторяется.
    Если сообщение содержит слово "да", то повторяется поиск по критериям поиска, которые были указаны ранее. При этом
также идет смещение офсет на +1.
    Значение офсет сбрасывается на 0, когда были изменены параметры поиска или введены повторно те же значения возраста
и населенного пункта. В последнем случае, это позволяет провести повторный поиск с самого начала, при этом пользователи,
которые уже есть в БД, не будут повторно выводиться в сообщениях. Такой подход позволит найти тех
пользователей, у которых стала выше популярность и они поднялись в поисковых запросах к первым местам.

Если первые символы сообщения не являются числом, то сообщение сразу отправляется в обработчик сообщений, где
игнорируется проверка наличия названия населенного пункта, а происходит поиск на наличие слов - команд.

