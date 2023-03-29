import psycopg2
from psycopg2 import Error


class create:
    def __init__(self, password):
        self.password = password

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
        print("Create_TABLE")
        conn = psycopg2.connect(database="db_user_vk", user='postgres', password=self.password)
        cur_table = conn.cursor()
        try:
            cur_table.execute(
                """CREATE TABLE IF NOT EXISTS user_vk (id SERIAL PRIMARY KEY, user_id VARCHAR(20) UNIQUE NOT NULL);""")
            conn.commit()
            answer_tb = "Таблицы созданы"
        except (Exception, Error) as error:
            answer_tb = error
            conn.rollback()
        conn.close()
        return answer_tb


"""СОЗДАНИЕ БАЗЫ ДАННЫХ"""


class check_insert_user_table:
    def __init__(self, password, user_id, first_name, last_name):
        self.password = password
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name

    def connect_db(self):
        conn = psycopg2.connect(database='db_user_vk', user='postgres', password=self.password)
        connection = conn.cursor()
        return conn, connection

    """ПРОВЕРКА ID ПОЛЬЗОВАТЕЛЯ В ТАБЛИЦЕ"""

    def check_users(self):
        conn, connection = check_insert_user_table.connect_db(self)
        connection.execute("""SELECT * FROM user_vk WHERE user_id = %s;""", (f'{self.user_id}',))
        row = connection.fetchone()
        if row is not None:
            # print('Пользователь имеется')
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
        connection.execute("""INSERT INTO user_vk (user_id) VALUES (%s);""", (self.user_id,))
        conn.commit()
        connection.close()
        conn.close()
        user_id, first_name, last_name = self.user_id, self.first_name, self.last_name

        return user_id, first_name, last_name
