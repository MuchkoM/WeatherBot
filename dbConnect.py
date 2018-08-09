import sqlite3
from config import *


class SQLDBConnect:
    def __init__(self, filename):
        self.filename = filename
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.filename, check_same_thread=False)

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def __del__(self):
        self.disconnect()

    def create_tables(self):
        connection = self.connection
        cursor = connection.cursor()

        s = ["""
                CREATE TABLE IF NOT EXISTS users  
                ( 
                    id INTEGER PRIMARY KEY,
                    last TIMESTAMP, 
                    period INTEGER
                );
                """, """
                CREATE TABLE IF NOT EXISTS places  
                ( 
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(40) NOT NULL,
                    stamp TIMESTAMP,
                    temperature DECIMAL(1,3)
                );
                """, """
                CREATE TABLE IF NOT EXISTS relUsersPlaces 
                ( 
                    idUser INTEGER NOT NULL , 
                    idPlace INTEGER NOT NULL ,
                    FOREIGN KEY(idUser) REFERENCES users(ID),
                    FOREIGN KEY(idPlace) REFERENCES places(ID)
                );
                """]

        cursor.execute(s[0])
        cursor.execute(s[1])
        cursor.execute(s[2])
        connection.commit()

    def get_subs_user_place(self):
        connection = self.connection
        cursor = connection.cursor()
        sql_query = """SELECT  users.id, places.name,users.last FROM  users
            inner join relUsersPlaces on users.id = relUsersPlaces.idUser 
            inner join places on places.id = relUsersPlaces.idPlace;"""
        cursor.execute(sql_query)
        connection.commit()
        return cursor.fetchall()

    def drop_tables(self):
        connection = self.connection
        cursor = connection.cursor()

        sql_querys = ["""DROP TABLE users;""", """DROP TABLE places;""", """DROP TABLE relUsersPlaces;"""]

        for sql_query in sql_querys:
            cursor.execute(sql_query)
        connection.commit()

    def add_user(self, user_id, period):
        connection = self.connection
        cursor = connection.cursor()
        s = """insert into users (id,LAST)
             values ('{}',{})""".format(user_id, period)
        cursor.execute(s)
        connection.commit()

    def get_cached_place(self, place):
        connection = self.connection
        cursor = connection.cursor()
        s = str(f"""select temperature from places where name = '{{}}' 
            and (strftime('%s','now') - strftime('%s',stamp)) < {cacheTime} """).format(place)
        cursor.execute(s)
        res = cursor.fetchone()
        connection.commit()
        return (place, res[0]) if res else None

    def get_users(self):
        connection = self.connection
        cursor = connection.cursor()
        s = """select * from users"""
        cursor.execute(s)
        connection.commit()
        return cursor.fetchall()

    def get_rel_user_place(self):
        connection = self.connection
        cursor = connection.cursor()
        s = """select * from relUsersPlaces"""
        cursor.execute(s)
        connection.commit()
        return cursor.fetchall()

    def get_place_id(self, place):
        connection = self.connection
        cursor = connection.cursor()
        s = """select id from places where name = '{}'""".format(place)
        cursor.execute(s)
        connection.commit()
        return cursor.fetchall()

    def get_subs(self):
        connection = self.connection
        cursor = connection.cursor()
        s = """select * from relUsersPlaces"""
        cursor.execute(s)
        connection.commit()
        return cursor.fetchall()

    def get_places(self):
        connection = self.connection
        cursor = connection.cursor()
        s = """select * from places"""
        cursor.execute(s)
        connection.commit()
        return cursor.fetchall()

    def add_place(self, place, temp):
        connection = self.connection
        cursor = connection.cursor()
        s = """select id from places where name = '{}'""".format(place)
        cursor.execute(s)

        if not cursor.fetchone():
            s = """insert into places(name,temperature,stamp) values ('{}',{},DATETIME('now'))""".format(place, temp)
        else:
            s = """update places set temperature={1}, stamp = DATETIME('now') where name='{0}';""".format(place, temp)

        cursor.execute(s)
        connection.commit()

    def get_temp(self):
        connection = self.connection
        cursor = connection.cursor()
        s = """SELECT strftime('%s','now') - strftime('%s','2004-01-01 02:34:56');"""
        cursor.execute(s)
        connection.commit()
        return cursor.fetchall()

    def add_sub(self, user_id, place):
        connection = self.connection
        cursor = connection.cursor()

        s = """INSERT INTO relUsersPlaces(idUser, idPlace)
            SELECT '{}', places.id
            FROM places where name = '{}'
            """.format(user_id, place)

        cursor.execute(s)
        connection.commit()


if __name__ == '__main__':
    user_id = 12312312

    dbc = SQLDBConnect('test.db')
    dbc.connect()

    dbc.drop_tables()
    dbc.create_tables()
    dbc.add_user(user_id, 0)
    dbc.add_user(user_id + 1, 0)

    dbc.add_place('Paris', 25)
    dbc.add_place('Minsk', 19)
    dbc.add_place('London', 17)
    dbc.add_place('Pinsk', 21)

    dbc.add_sub(user_id, 'Paris')
    dbc.add_sub(user_id, 'London')
    dbc.add_sub(user_id, 'Pinsk')

    dbc.add_sub(user_id + 1, 'Pinsk')
    dbc.add_sub(user_id + 1, 'Minsk')

    print("Users", dbc.get_users())
    print("Places", dbc.get_places())
    print("Subs", dbc.get_subs())
    print("Users Place", dbc.get_subs_user_place())
    print("tmp", dbc.get_temp())

    dbc.disconnect()
