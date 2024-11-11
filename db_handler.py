import sqlite3


def create_connection(db_file='DB.db'):
    connection = sqlite3.connect(db_file)

    return connection