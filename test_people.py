import datetime
import re

import pytest

from functions import password_score
from load_people import ApiDataDownloader, ApiDataReader, ApiDataModifier
from settings import API_URL


@pytest.fixture
def downloader_obj():
    api_param = {'results': 1, 'seed': 'abc', }
    downloader = ApiDataDownloader(API_URL, api_param)
    return downloader


@pytest.fixture
def reader_obj(downloader_obj):
    downloader_obj.send_request()
    reader = ApiDataReader(downloader_obj, data_location='results')
    return reader


@pytest.fixture
def modifier_obj(downloader_obj):
    downloader_obj.send_request()
    modifications = (
        {'name': 'remove_non_digit', 'key_path': ('phone',)},
        {'name': 'remove_non_digit', 'key_path': ('cell',)},
        {'name': 'days_to_birthday', 'key_path': ('dob', 'days_to_birthday',)},
        {'name': 'delete_value', 'key_path': ('picture',)},
    )
    modifier = ApiDataModifier(
        downloader_obj, modifications, data_dict='results')
    return modifier


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


class TestApiDataModifier:

    def test_api_data_modifier_set_value(self, modifier_obj):
        dict_obj = modifier_obj._data[0]
        phone = '000-000-000'
        firstname = 'Some non-existing name'
        street = 'Name of the street that does not exist'
        new_value = 'new_value'
        value_returned = modifier_obj.set_value(dict_obj, ('phone',), phone)
        modifier_obj.set_value(dict_obj, ('name', 'first'), firstname)
        modifier_obj.set_value(
            dict_obj, ('location', 'street', 'name'), street)
        modifier_obj.set_value(dict_obj, ('new_key',), new_value)

        error_value = 'Value not set'
        error_new_key_value = 'New key-value not set'
        error_true_returned = 'True not returned after setting value'
        error_key_error = 'False not returned when key path is incorrect'

        assert dict_obj['phone'] == phone, error_value
        assert dict_obj['name']['first'] == firstname, error_value
        assert dict_obj['location']['street']['name'] == street, error_value
        assert dict_obj['new_key'] == new_value, error_new_key_value
        assert modifier_obj.set_value(dict_obj, ('phone',), phone)
        assert value_returned is True, error_true_returned
        assert modifier_obj.set_value(
            dict_obj, ('non-existent_key', 'street'),
            street) is False, error_key_error

    def test_api_data_modifier_delete_value(self, modifier_obj):
        dict_obj = modifier_obj._data[0]
        resp = modifier_obj.delete_value(dict_obj, ('email',))
        modifier_obj.delete_value(dict_obj, ('name', 'first'))
        modifier_obj.delete_value(dict_obj, ('location', 'street', 'name'))

        error_value = 'Value not deleted'
        error_true_returned = 'True not returned after deleting value'
        error_key_error = 'False not returned when key path is incorrect'

        assert 'email' not in dict_obj, error_value
        assert 'first' not in dict_obj['name'], error_value
        assert 'name' not in dict_obj['location']['street'], error_value
        assert resp is True, error_true_returned
        assert modifier_obj.delete_value(
            dict_obj, ('non-existent_key',)) is False, error_key_error
        assert modifier_obj.delete_value(
            dict_obj, ('non-existent_key', 'street')) is False, error_key_error

    def test_remove_non_digit(self, modifier_obj):
        dict_obj = modifier_obj._data[0]
        modifier_obj.remove_non_digit(dict_obj, ('phone',))
        modifier_obj.remove_non_digit(dict_obj, ('cell',))
        error = 'Non-digit characters present'
        assert bool(re.search(r'\D', dict_obj['phone'])) is False, error
        assert bool(re.search(r'\D', dict_obj['cell'])) is False, error

    def test_days_to_birthday(self, modifier_obj):
        dict_obj = modifier_obj._data[0]
        modifier_obj.days_to_birthday(dict_obj, ('days_to_birthday',))
        error_key = 'days_to_birthday key not set'
        assert 'days_to_birthday' in dict_obj, error_key


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
