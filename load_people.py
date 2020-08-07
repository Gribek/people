import json
import re
from datetime import datetime, date
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

API_URL = 'https://randomuser.me/api/?'
API_PARAMETERS = {'results': 1, 'seed': 'abc'}


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
        birthdate = self.get_value(dict_obj, key_path=('dob', 'date'))
        birthday = datetime.strptime(birthdate, "%Y-%m-%dT%H:%M:%S.%fZ").date()
        today = date.today()

        if (today.month == birthday.month and today.day >= birthday.day) \
                or today.month > birthday.month:
            next_bd_year = today.year + 1
        else:
            next_bd_year = today.year

        next_birthday = date(next_bd_year, birthday.month, birthday.day)
        days_left = next_birthday - today

        return days_left.days
