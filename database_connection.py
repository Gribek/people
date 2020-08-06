from peewee import SqliteDatabase


def sqlite_connection(filename):
    """Establish a connection to the SQLite database"""
    cnx = SqliteDatabase(filename, autoconnect=False,
                         pragmas={'foreign_keys': 1})
    return cnx
