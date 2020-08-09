# Name of the database file
DATABASE = 'people.db'

# Url address to the randomuser API
API_URL = 'https://randomuser.me/api/?'

# Parameters used when a request is made to the randomuser API
API_PARAMETERS = {'results': 1000, 'seed': 'abc'}

# Configuration of data modification to be performed
DATA_MODIFICATIONS = (
    {'name': 'remove_non_digit', 'key_path': ('phone',)},
    {'name': 'remove_non_digit', 'key_path': ('cell',)},
    {'name': 'days_to_birthday', 'key_path': ('dob', 'days_to_birthday',)},
    {'name': 'delete_value', 'key_path': ('picture',)},
)
