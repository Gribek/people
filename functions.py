from importlib import import_module
import re

from peewee import fn, SQL

from database_connection import sqlite_connection
from settings import DATABASE


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

    def most_occurrences(self, column, limit):
        """Find the most frequent values in the selected column."""
        with self.__db:
            tables = self.__db.get_tables()
            for table in tables:
                cls = getattr(import_module('models'), table.title())
                attr = getattr(cls, column, None)
                if attr is not None:
                    break
            else:
                return None

            return cls.select(attr, fn.COUNT(attr).alias('count')).group_by(
                attr).order_by(SQL('count').desc()).limit(limit)

    def data_in_range(self, table, column, lower, upper):
        """Collect data within the given range."""
        cls = getattr(import_module(self.__models), table)
        attr = getattr(cls, column)
        with self.__db:
            return cls.select().where(attr.between(lower, upper))

    def get_data(self, table, *columns):
        """Get data from selected table."""
        cls = getattr(import_module(self.__models), table)
        attr = []
        for column in columns:
            attr.append(getattr(cls, column))
        return cls.select(*attr)


class Result:
    """Display the result in the terminal."""

    def __init__(self, result, prefix=None, suffix=None):
        self.__result = result
        self.__prefix = prefix
        self.__suffix = suffix

    def display_multiple(self):
        """Print multiple results."""
        for line in self.__result:
            print(*line)

    def display_single(self):
        """Format and print the result."""
        for i in range(len(self.__result)):
            result_string = ' '.join(str(j[i]) for j in (
                self.__prefix, self.__result, self.__suffix) if j)
            print(result_string)


def db_functions(func):
    """Pass DatabaseFunction object to decorated function."""

    def wrapper(**kwargs):
        obj = DatabaseFunctions(db_name=DATABASE,
                                db_connection=sqlite_connection)
        func(obj, **kwargs)

    return wrapper


def password_score(password):
    """Calculate the score for password security."""
    score = 0
    if bool(re.search(r'[a-z]', password)):
        score += 1
    if bool(re.search(r'[A-Z]', password)):
        score += 2
    if bool(re.search(r'\d', password)):
        score += 1
    if len(password) >= 8:
        score += 5
    if any(c in r"!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~" for c in password):
        score += 3
    return score
