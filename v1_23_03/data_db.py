import psycopg2
from psycopg2 import Error


class create:
    def __init__(self, password):
        self.password = password

    # *********************                     ===       1     ===                     ******************************
    def create_db(self):
        print("Create database")
        create_conn = psycopg2.connect(dbname='postgres', user='postgres', password=self.password)
        cursor = create_conn.cursor()
        create_conn.autocommit = True
        sql = "CREATE DATABASE temp_bd_for_diploma"

        try:
            cursor.execute(sql)
            create_conn.commit()
            answer_db = "CREATE_BD --> OK"
        except (Exception, Error) as error:
            answer_db = error
            create_conn.rollback()
        cursor.close()
        create_conn.close()
        return answer_db

    # *********************                     ===       2     ===                     ******************************
    def create_table(self):
        print("Create_TABLE")
        conn = psycopg2.connect(database="temp_bd_for_diploma", user='postgres', password=self.password)
        cur_table = conn.cursor()
        try:
            cur_table.execute("""CREATE TABLE IF NOT EXISTS user_vk (id SERIAL PRIMARY KEY, 
                                user_id VARCHAR(20) UNIQUE NOT NULL,
                                first_name VARCHAR(20) NOT NULL,
                                last_name VARCHAR(20) NOT NULL);""")
            '''cur_table.execute("""CREATE TABLE IF NOT EXISTS photo (id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL REFERENCES user_vk(id) ON DELETE CASCADE,
                                photo VARCHAR(60) NOT NULL,
                                quantity_like VARCHAR(60) NULL);""")'''
            conn.commit()
            answer_tb = "таблицы созданы"
        except (Exception, Error) as error:
            answer_tb = error
            conn.rollback()
        conn.close()
        return answer_tb


# =================================================================================================================================


class check_insert_user_table:
    def __init__(self, password, user_id, first_name, last_name):
        self.password = password
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name

    def connect_db(self):
        conn = psycopg2.connect(database='temp_bd_for_diploma', user='postgres', password=self.password)
        connection = conn.cursor()
        return conn, connection

    def check_users(self):
        conn, connection = check_insert_user_table.connect_db(self)
        connection.execute("""SELECT * FROM user_vk WHERE user_id = %s;""", (f'{self.user_id}',))
        row = connection.fetchone()
        if row is not None:
            print('Значение отсутствует --> (Нет)')
            status = "CLOSED"
            connection.close()
            conn.close()
            return status
        elif row is None:
            print('Значение отсутствует --> ( =======   Да   =======)')
            status = "OPEN"
            connection.close()
            conn.close()
            return status

    def insert_users(self):
        conn, connection = check_insert_user_table.connect_db(self)
        connection.execute("""INSERT INTO user_vk (user_id, first_name, last_name) VALUES (%s, %s, %s);""",
                           (f'{self.user_id}', f'{self.first_name}', f'{self.last_name}'))
        conn.commit()
        status = "Значение добавлено --> ( =======   OK   =======)"
        connection.close()
        conn.close()
        user_id, first_name, last_name = self.user_id, self.first_name, self.last_name
        # print(f'in DB inject {self.user_id}', f'{self.first_name}', f'{self.last_name}')

        return user_id, first_name, last_name
