import json
import re
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


class ApiDataModifier:
    """Modify data received from API."""

    class _Decorators:
        """Decorators for ApiDataModifier class methods."""

        @classmethod
        def change_value(cls, func):
            """Change the value of the selected key in the dict."""

            def wrapper(self, dict_obj, key_path):
                value = self.get_value(dict_obj, key_path)
                new_value = func(self, value)
                if new_value is None:
                    return False
                return self.set_value(dict_obj, key_path, new_value)

            return wrapper

    def __init__(self, downloader, modifications, data_dict=None):
        self.__data = downloader.data
        if data_dict is not None:
            self.__data = self.__data[data_dict]
        self.__modifications = modifications

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

    @_Decorators.change_value
    def remove_non_digit(self, value):
        """Remove non digit characters from string."""
        try:
            new_value = re.sub(r'\D', '', value)
        except TypeError:
            return None
        return new_value
