from importlib import import_module

from peewee import fn

from database_connection import sqlite_connection


class DatabaseFunctions:
    """Retrieve data from the database."""

    def __init__(self, db_name, db_connection, models='models'):
        self.__db = db_connection(db_name)
        self.__models = models

    def count_entries(self, table, condition=None, cond_value=None):
        """Count number of entries in the selected table."""
        cls = getattr(import_module(self.__models), table)
        with self.__db:
            if condition:
                attr = getattr(cls, condition)
                return cls.select().where(attr == cond_value).count()
            else:
                return cls.select().count()

    def average_value(self, table, column, condition=None, cond_value=None):
        """Calculate the average value of the selected column."""
        cls = getattr(import_module(self.__models), table)
        attr = getattr(cls, column)
        with self.__db:
            if condition:
                cond_attr = getattr(cls, condition)
                return cls.select(fn.AVG(attr).alias('avg')).where(
                    cond_attr == cond_value)
            else:
                return cls.select(fn.AVG(attr).alias('avg'))


def db_functions(func):
    """Pass DatabaseFunction object to decorated function."""

    def wrapper(**kwargs):
        obj = DatabaseFunctions(db_name='people.db',
                                db_connection=sqlite_connection)
        func(obj, **kwargs)

    return wrapper
