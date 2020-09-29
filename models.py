from peewee import *

from db.database_connection import sqlite_connection
from settings import DATABASE

db = sqlite_connection(DATABASE)


class Person(Model):
    """Represent a single person."""
    title = TextField()
    firstname = TextField()
    lastname = TextField()
    gender = TextField()
    nationality = TextField()
    id_name = TextField(null=True)
    id_value = TextField(null=True)
    date_of_birth = DateField()
    age = IntegerField()
    days_to_birthday = IntegerField()

    class Meta:
        database = db

    @property
    def contact(self):
        """Get person's contact data"""
        return self.contacts.get()

    @property
    def location(self):
        """Get person's location data"""
        return self.locations.get()

    @property
    def login(self):
        """Get person's login data"""
        return self.logins.get()


class Contact(Model):
    """Represent a person's contact data."""
    email = TextField()
    phone = TextField()
    cell = TextField()
    person = ForeignKeyField(Person, backref='contacts', on_delete='CASCADE',
                             unique=True)

    class Meta:
        database = db


class Location(Model):
    """Represent a person's location data."""
    number = IntegerField()
    street = TextField()
    city = TextField()
    state = TextField()
    country = TextField()
    postcode = TextField()
    timezone_offset = TextField()
    timezone_description = TextField()
    coordinates_latitude = DecimalField(max_digits=6, decimal_places=4)
    coordinates_longitude = DecimalField(max_digits=7, decimal_places=4)
    person = ForeignKeyField(Person, backref='locations', on_delete='CASCADE',
                             unique=True)

    class Meta:
        database = db


class Login(Model):
    """Represent a person's login data."""
    uuid = TextField()
    username = TextField()
    password = TextField()
    salt = TextField()
    md5 = TextField()
    sha1 = TextField()
    sha256 = TextField()
    registration_date = DateField()
    years_since_registration = IntegerField()
    person = ForeignKeyField(Person, backref='logins', on_delete='CASCADE',
                             unique=True)

    class Meta:
        database = db


# Initialize database and create tables based on models
if __name__ == '__main__':
    db.connect(reuse_if_open=True)
    db.create_tables([Person, Contact, Location, Login])
    db.close()
