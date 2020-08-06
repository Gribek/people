import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen


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
