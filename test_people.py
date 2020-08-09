import pytest

from functions import password_score
from load_people import ApiDataDownloader, ApiDataReader
from settings import API_URL


@pytest.fixture
def downloader_obj():
    api_param = {'results': 5, 'seed': 'abc', }
    downloader = ApiDataDownloader(API_URL, api_param)
    return downloader


@pytest.fixture
def reader_obj(downloader_obj):
    downloader_obj.send_request()
    reader = ApiDataReader(downloader_obj, data_location='results')
    return reader


class TestApiDataDownloader:

    def test_api_data_downloader_initial_attributes(self, downloader_obj):
        data_error = 'data attribute not None before sending request'
        response_error = 'response attribute not False before sending request'
        assert downloader_obj.data is None, data_error
        assert downloader_obj.response is False, response_error

    def test_api_data_downloader_send_request(self, downloader_obj):
        data_error = 'data attribute not None after sending request'
        response_error = 'response attribute False after sending request'
        downloader_obj.send_request()
        assert downloader_obj.data is not None, data_error
        assert downloader_obj.response is True, response_error
        assert 'results' in downloader_obj.data, 'Data saved incorrectly'
        assert 'info' in downloader_obj.data, 'Data saved incorrectly'


class TestApiDataReader:

    def test_api_data_reader_data(self, reader_obj, downloader_obj):
        error = 'Incorrect reference to data'
        assert reader_obj._data is downloader_obj.data['results'], error

    def test_api_data_reader_get_value(self, reader_obj):
        dict_obj = reader_obj._data[0]
        phone = dict_obj['phone']
        firstname = dict_obj['name']['first']
        street = dict_obj['location']['street']['name']
        error_value = 'Incorrect value returned'
        error_key_error = 'Value not None when key does not exist'
        assert reader_obj.get_value(dict_obj, ('phone',)) == phone, error_value
        assert reader_obj.get_value(
            dict_obj, ('name', 'first')) == firstname, error_value
        assert reader_obj.get_value(
            dict_obj, ('location', 'street', 'name')) == street, error_value
        assert reader_obj.get_value(
            dict_obj, ('non-existent_key',)) is None, error_key_error


def test_password_score():
    assert password_score('') == 0
    assert password_score('aeqwasd') == 1
    assert password_score('sdadWd ') == 3
    assert password_score('1joewe3') == 2
    assert password_score('r2dDt') == 4
    assert password_score('supertajne') == 6
    assert password_score('1@3$') == 4
    assert password_score('1@3$QWERTY') == 11
    assert password_score('superHaslo!!!1') == 12
