import psycopg2
from psycopg2 import Error


class create:
    def __init__(self, password, for_the_user_id):
        self.password = password
        self.table_name = 'id_' + str(for_the_user_id)

    """СОЗДАНИЕ БАЗЫ ДАННЫХ"""

    def create_db(self):
        print("Create database")
        create_conn = psycopg2.connect(dbname='postgres', user='postgres', password=self.password)
        cursor = create_conn.cursor()
        create_conn.autocommit = True
        sql = "CREATE DATABASE db_user_vk"
        try:
            cursor.execute(sql)
            create_conn.commit()
            answer_db = "База данных создана"
        except (Exception, Error) as error:
            answer_db = error
            create_conn.rollback()
        cursor.close()
        create_conn.close()
        return answer_db

    """СОЗДАНИЕ ТАБЛИЦ"""

    def create_table(self):
        try:
            conn = psycopg2.connect(database='db_user_vk', user='postgres', password=self.password)
            cur_table = conn.cursor()
        except (Exception, Error) as error:
            print(error)
            return
        try:
            cur_table.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name} (id SERIAL PRIMARY KEY, user_id VARCHAR(20) UNIQUE NOT NULL);')
            conn.commit()
        except (Exception, Error) as error:
            print(f'Ошибка создания таблиц: {error}')
            conn.rollback()
        conn.close()


    """УДАЛЕНИЕ ТАБЛИЦЫ"""


    def del_table(self):
        print("DELETE_TABLE")
        conn = psycopg2.connect(database="db_user_vk", user='postgres', password=self.password)
        delete_table = conn.cursor()
        try:
            delete_table.execute(f"DROP TABLE {self.table_name} CASCADE;")
            conn.commit()
            answer_tb = "История поиска очищена"
        except (Exception, Error) as error:
            answer_tb = error
            conn.rollback()
        conn.close()
        return answer_tb


"""РАБОТА С ТАБЛИЦАМИ"""


class check_insert_user_table:
    def __init__(self, password, user_id, first_name, last_name, for_the_user_id):
        self.password = password
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.table_name = 'id_' + str(for_the_user_id)


    def connect_db(self):
        conn = psycopg2.connect(database='db_user_vk', user='postgres', password=self.password)
        connection = conn.cursor()
        return conn, connection

    """ПРОВЕРКА ID ПОЛЬЗОВАТЕЛЯ В ТАБЛИЦЕ"""

    def check_users(self):
        conn, connection = check_insert_user_table.connect_db(self)
        connection.execute(f"SELECT * FROM {self.table_name} WHERE user_id = '{self.user_id}';")
        row = connection.fetchone()
        if row is not None:
            status = "available"
            connection.close()
            conn.close()
            return status
        elif row is None:
            # print('Пользователь отсутствует')
            status = "absent"
            connection.close()
            conn.close()
            return status

    """ВСТАВКА НВОГО ЗНАЧЕНИЯ В ТАБЛИЦУ"""

    def insert_users(self):
        conn, connection = check_insert_user_table.connect_db(self)
        connection.execute(f"INSERT INTO {self.table_name} (user_id) VALUES ('{self.user_id}');")
        conn.commit()
        connection.close()
        conn.close()
        user_id, first_name, last_name = self.user_id, self.first_name, self.last_name

        return user_id, first_name, last_name
