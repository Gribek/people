import re

from peewee import SqliteDatabase
import pytest

from functions import password_score
from load_people import ApiDataDownloader, ApiDataReader, ApiDataModifier, \
    ApiDataSave
from models import Person, Login, Location, Contact
from settings import API_URL, DATA_MODIFICATIONS

MODELS = [Person, Login, Location, Contact]
API_PERSONS = 2

db = SqliteDatabase(':memory:')


@pytest.fixture
def downloader_obj():
    api_param = {'results': API_PERSONS, 'seed': 'abc', }
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
    modifications = DATA_MODIFICATIONS
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

    def test_execute_modifications(self, modifier_obj):
        dict_obj = modifier_obj._data[1]
        modifier_obj.execute_modifications()

        error_new_key = 'days_to_birthday key not set'
        error_delete = 'picture key not deleted'
        error_change = 'Value not changed'

        assert 'days_to_birthday' in dict_obj['dob'], error_new_key
        assert 'picture' not in dict_obj, error_delete
        assert bool(re.search(r'\D', dict_obj['phone'])) is False, error_change
        assert bool(re.search(r'\D', dict_obj['cell'])) is False, error_change


class TestApiDataSave:

    @classmethod
    def setup_class(cls):
        db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        db.connect()
        db.create_tables(MODELS)

    @classmethod
    def teardown_class(cls):
        db.drop_tables(MODELS)
        db.close()

    def test_save_person(self, downloader_obj, modifier_obj):
        modifier_obj.execute_modifications()
        dict_obj = modifier_obj._data[0]
        save_obj = ApiDataSave(downloader_obj, 'results')
        save_obj.save_person(dict_obj)
        assert len(
            Person.select()) == 1, 'The Person object has not been saved'
        person = Person.select()[0]
        error = 'Invalid data has been written'
        assert person.title == dict_obj['name']['title'], error
        assert person.firstname == dict_obj['name']['first'], error
        assert person.lastname == dict_obj['name']['last'], error
        assert person.gender == dict_obj['gender'], error
        assert person.nationality == dict_obj['nat'], error
        assert person.id_name == dict_obj['id']['name'], error
        assert person.id_value == dict_obj['id']['value'], error
        assert person.date_of_birth == dict_obj['dob']['date'], error
        assert person.age == dict_obj['dob']['age'], error
        assert person.days_to_birthday == dict_obj['dob'][
            'days_to_birthday'], error

    def test_save_login(self, downloader_obj, modifier_obj):
        modifier_obj.execute_modifications()
        dict_obj = modifier_obj._data[0]
        save_obj = ApiDataSave(downloader_obj, 'results')
        p = save_obj.save_person(dict_obj)
        save_obj.save_login(dict_obj, p)
        assert len(Login.select()) == 1, 'The Login object has not been saved'
        login = Login.select()[0]
        error = 'Invalid data has been written'
        assert login.uuid == dict_obj['login']['uuid'], error
        assert login.username == dict_obj['login']['username'], error
        assert login.password == dict_obj['login']['password'], error
        assert login.salt == dict_obj['login']['salt'], error
        assert login.md5 == dict_obj['login']['md5'], error
        assert login.sha1 == dict_obj['login']['sha1'], error
        assert login.sha256 == dict_obj['login']['sha256'], error
        assert login.registration_date == dict_obj['registered']['date'], error
        assert login.years_since_registration == dict_obj[
            'registered']['age'], error
        assert login.person == p, error

    def test_save_location(self, downloader_obj, modifier_obj):
        modifier_obj.execute_modifications()
        dict_obj = modifier_obj._data[0]
        save_obj = ApiDataSave(downloader_obj, 'results')
        p = save_obj.save_person(dict_obj)
        save_obj.save_location(dict_obj, p)
        assert len(
            Location.select()) == 1, 'The Location object has not been saved'
        location = Location.select()[0]
        error = 'Invalid data has been written'
        assert location.number == dict_obj[
            'location']['street']['number'], error
        assert location.street == dict_obj['location']['street']['name'], error
        assert location.city == dict_obj['location']['city'], error
        assert location.state == dict_obj['location']['state'], error
        assert location.country == dict_obj['location']['country'], error
        assert location.postcode == str(
            dict_obj['location']['postcode']), error
        assert location.timezone_offset == dict_obj[
            'location']['timezone']['offset'], error
        assert location.timezone_description == dict_obj[
            'location']['timezone']['description'], error
        assert str(location.coordinates_latitude) == dict_obj[
            'location']['coordinates']['latitude'], error
        assert str(location.coordinates_longitude) == dict_obj[
            'location']['coordinates']['longitude'], error
        assert location.person == p, error

    def test_save_contact(self, downloader_obj, modifier_obj):
        modifier_obj.execute_modifications()
        dict_obj = modifier_obj._data[0]
        save_obj = ApiDataSave(downloader_obj, 'results')
        p = save_obj.save_person(dict_obj)
        save_obj.save_contact(dict_obj, p)
        assert len(
            Contact.select()) == 1, 'The Contact object has not been saved'
        contact = Contact.select()[0]
        error = 'Invalid data has been written'
        assert contact.email == dict_obj['email'], error
        assert contact.phone == dict_obj['phone'], error
        assert contact.cell == dict_obj['cell'], error
        assert contact.person == p, error

    def test_save_data_to_db(self, downloader_obj, modifier_obj):
        persons = len(Person.select())
        contacts = len(Contact.select())
        logins = len(Login.select())
        localizations = len(Location.select())
        modifier_obj.execute_modifications()
        save_obj = ApiDataSave(downloader_obj, 'results')
        save_obj.save_data_to_db()
        error = 'Incorrect number of objects saved in the database'
        assert len(Person.select()) == persons + API_PERSONS, error
        assert len(Contact.select()) == contacts + API_PERSONS, error
        assert len(Login.select()) == logins + API_PERSONS, error
        assert len(Location.select()) == localizations + API_PERSONS, error


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
