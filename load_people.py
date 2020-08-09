from datetime import datetime, date, timedelta
import json
import re
from sys import exit
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from database_connection import sqlite_connection
from models import Person, Contact, Login, Location
from settings import DATABASE, API_URL, API_PARAMETERS

db = sqlite_connection(DATABASE)


def main():
    """Download data from API, modify and save to the database"""

    # create downloader to handle getting data from randomuser API
    downloader = ApiDataDownloader(API_URL, API_PARAMETERS)

    # Send request to API and collect data
    downloader.send_request()

    # Check for API response, exit if false
    if not downloader.response:
        exit(1)

    # check for API data, exit if no data has been received
    if downloader.data is None:
        print('Failed to get data from API')
        exit(1)

    # set of modifications to perform on API data
    modifications = (
        {'name': 'remove_non_digit', 'key_path': ('phone',)},
        {'name': 'remove_non_digit', 'key_path': ('cell',)},
        {'name': 'days_to_birthday', 'key_path': ('dob', 'days_to_birthday',)},
        {'name': 'delete_value', 'key_path': ('picture',)},
    )

    # create modifier object, pass modifications to perform
    modifier = ApiDataModifier(downloader, modifications, 'results')

    # modify data accordingly to configuration
    modifier.execute_modifications()

    # Save modified data to the database
    save_obj = ApiDataSave(downloader, 'results')
    save_obj.save_data_to_db()


class ApiDataDownloader:
    """Download data from API."""

    def __init__(self, url, parameters):
        self.__api_url = url
        self.__parameters = parameters
        self.response = False
        self.data = None

    def send_request(self):
        """Send request to API and gather data."""
        url = self.__api_url + urlencode(self.__parameters)
        try:
            response = urlopen(url)
        except URLError:
            print('Unable to connect to API')
        else:
            self.response = True
            if response.status == 200:
                self.data = json.loads(response.read())


class ApiDataReader:
    """Read data received from API."""

    def __init__(self, downloader, data_location=None):
        self._data = downloader.data
        if data_location:
            self._data = self._data[data_location]

    @staticmethod
    def get_value(dict_obj, key_path):
        """Get the value of the selected key from the dictionary."""
        result = dict_obj
        for key in key_path:
            try:
                result = result[key]
            except KeyError:
                return None
        return result


class ApiDataModifier(ApiDataReader):
    """Modify data received from API."""

    class _Decorators:
        """Decorators for ApiDataModifier class methods."""

        @classmethod
        def change_value(cls, func):
            """Replace selected value with function output."""

            def wrapper(self, dict_obj, key_path):
                value = self.get_value(dict_obj, key_path)
                new_value = func(self, value)
                if new_value is None:
                    return False
                return self.set_value(dict_obj, key_path, new_value)

            return wrapper

        @classmethod
        def add_new_value(cls, func):
            """Add new key-value pair to the dictionary"""

            def wrapper(self, dict_obj, key_path):
                value = func(self, dict_obj)
                if value is None:
                    return False
                return self.set_value(dict_obj, key_path, value)

            return wrapper

    def __init__(self, downloader, modifications, data_dict=None):
        super(ApiDataModifier, self).__init__(downloader, data_dict)
        self.__modifications = modifications

    @staticmethod
    def set_value(dict_obj, key_path, value):
        """Set the value of the selected key in the dictionary."""
        temp = dict_obj
        for i in range(len(key_path) - 1):
            try:
                temp = temp[key_path[i]]
            except KeyError:
                return False
        temp[key_path[-1]] = value
        return True

    def execute_modifications(self):
        """Perform all data modifications."""
        for person_dict in self._data:
            for modification in self.__modifications:
                method = getattr(self, modification['name'])
                method(person_dict, modification['key_path'])

    @staticmethod
    def delete_value(dict_obj, key_path):
        """Delete the value of the selected key from the dictionary."""
        temp = dict_obj
        for i in range(len(key_path) - 1):
            try:
                temp = temp[key_path[i]]
            except KeyError:
                return False
        try:
            del temp[key_path[-1]]
        except KeyError:
            return False
        return True

    @_Decorators.change_value
    def remove_non_digit(self, value):
        """Remove non digit characters from string."""
        try:
            new_value = re.sub(r'\D', '', value)
        except TypeError:
            return None
        return new_value

    @_Decorators.add_new_value
    def days_to_birthday(self, dict_obj):
        """Calculate days to next birthday."""
        today = date.today()
        birthdate = self.get_value(dict_obj, key_path=('dob', 'date'))
        birthday = datetime.strptime(birthdate, "%Y-%m-%dT%H:%M:%S.%fZ").date()
        birthday = birthday.replace(year=today.year)
        if birthday < today:
            birthday += timedelta(days=356)

        days_left = birthday - today
        return days_left.days


class ApiDataSave(ApiDataReader):
    """Save API data to the database."""

    def save_data_to_db(self):
        """Save all persons' data to the database"""
        for person_dict in self._data:
            person = self.save_person(person_dict)
            self.save_contact(person_dict, person)
            self.save_location(person_dict, person)
            self.save_login(person_dict, person)

    def save_person(self, dict_obj):
        """Save person to the database"""
        dataset = {
            'firstname': ('name', 'first'), 'lastname': ('name', 'last'),
            'title': ('name', 'title'), 'gender': ('gender',),
            'nationality': ('nat',), 'id_name': ('id', 'name'),
            'id_value': ('id', 'value'), 'date_of_birth': ('dob', 'date'),
            'age': ('dob', 'age'),
            'days_to_birthday': ('dob', 'days_to_birthday')
        }
        self.collect_data(dataset, dict_obj)
        with db:
            person = Person.create(**dataset)
        return person

    def save_contact(self, dict_obj, person):
        """Save contact data to the database"""
        dataset = {'email': ('email',), 'phone': ('phone',), 'cell': ('cell',)}
        self.collect_data(dataset, dict_obj)
        dataset['person'] = person
        with db:
            Contact.create(**dataset)

    def save_location(self, dict_obj, person):
        """Save location data to the database"""
        dataset = {
            'number': ('location', 'street', 'number'),
            'street': ('location', 'street', 'name'),
            'city': ('location', 'city'), 'state': ('location', 'state'),
            'country': ('location', 'country'),
            'postcode': ('location', 'postcode'),
            'timezone_offset': ('location', 'timezone', 'offset'),
            'timezone_description': ('location', 'timezone', 'description'),
            'coordinates_latitude': ('location', 'coordinates', 'latitude'),
            'coordinates_longitude': ('location', 'coordinates', 'longitude')
        }
        self.collect_data(dataset, dict_obj)
        dataset['person'] = person
        with db:
            Location.create(**dataset)

    def save_login(self, dict_obj, person):
        """Save login data to the database"""
        dataset = {
            'uuid': ('login', 'uuid'), 'username': ('login', 'username'),
            'password': ('login', 'password'), 'salt': ('login', 'salt'),
            'md5': ('login', 'md5'), 'sha1': ('login', 'sha1'),
            'sha256': ('login', 'sha256'),
            'registration_date': ('registered', 'date'),
            'years_since_registration': ('registered', 'age')
        }
        self.collect_data(dataset, dict_obj)
        dataset['person'] = person
        with db:
            Login.create(**dataset)

    def collect_data(self, dataset, dict_obj):
        """Gather data defined in dataset."""
        for key in dataset:
            dataset[key] = self.get_value(dict_obj, dataset[key])


if __name__ == '__main__':
    main()
