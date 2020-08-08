from importlib import import_module

from database_connection import sqlite_connection


class DatabaseFunctions:
    """Retrieve data from the database."""

    def __init__(self, db_name, db_connection, models='models'):
        self.__db = db_connection(db_name)
        self.__models = models

    def count_entries(self, table, column=None, condition=None):
        """Count number of entries in selected table"""
        cls = getattr(import_module(self.__models), table)
        with self.__db:
            if condition:
                attr = getattr(cls, column)
                return cls.select().where(attr == condition).count()
            else:
                return cls.select().count()


def db_functions(func):
    """Pass DatabaseFunction object to decorated function."""

    def wrapper(**kwargs):
        obj = DatabaseFunctions(db_name='people.db',
                                db_connection=sqlite_connection)
        func(obj, **kwargs)

    return wrapper
