# People
### Table of contents
* [Setup](#setup)
* [Settings](#settings)
* [Available commands](#available-commands)
* [Technologies](#technologies)

### Setup
Download the repository and prepare a new virtual environment. Then install all dependencies using the command:
```
$ pip install -r requirements.txt
```

The attached database file already contains all the data required for this assignment. 
To start with an empty database and test all scripts, you can delete the people.db file or rename the database file in the settings (check [Settings](#settings)).
Then run the following scripts:
```
python models.py

python load_people.py
```
The first one will create a new database file and migrate all models.
The second one will download data from randomuser API, make modifications, and save them to the database.

This concludes the project setup, you can also skip the step of creating a new database and proceed to use the commands described [below](#available-commands) right after installing the requirements.

### Settings

The settings.py file contain the configuration for the following:
* database name
* randomuser API url
* parameters used when a request is made to the randomuser API

To rename the database file, change the value of the DATABASE variable, by default set to 'people.db':
```
DATABASE = 'people.db'
```
The variables sent in the request to the randomuser API can be found in the API_PARAMETERS dictionary.
They are now set so that the received data matches the contents of the persons.json file received with the assignment:
```
API_PARAMETERS = {'results': 1000, 'seed': 'abc'}
```

### Available commands

All commands are called from the people.py script.

**1. _gender-percentage_ - display the percentage of men and women**
  
 Command pattern: people.py gender-percentage 
  
 Example input:
 ```
 python people.py gender-percentage
 ```

**2. _average-age_ - display the average age of people**

 Command pattern: people.py gender-percentage [OPTIONS]
 
 Options:  
 --gender [male|female] - specifies gender
 
 Example input:
 ```
 python people.py average-age
 python people.py average-age --gender male
 ```

**3. _most-common_ - display the most common value in a given category**

Command pattern: people.py most-common CATEGORY [OPTIONS]

where:  
 CATEGORY can be any information stored in the database, e.g. city, country, password, gender, age, nationality, etc. 

  Options:  
 --limit integer - number of displayed results
 
 Example input:  
 ```
 python people.py most-common city
 python people.py most-common password --limit 5
 ```
 
 **4. _born-between_ - display all users born in the given date range**
 
 Command pattern:  people.py born-between LOWER UPPER
 
 where:  
 LOWER and UPPER are dates in the format 'YYYY-MM-DD'
 
 Example input:  
 ```
 python people.py born-between 1995-01-01 1996-12-31
 ```

**5. _password-security_ - display the most secure password**
 
 Command pattern: python people.py password-security
 
 Example input:  
 ```
 python people.py password-security
 ```
 
### Technologies
* Python 3.7.5
* SQLite 3.22.0
* peewee 3.13.3
* click 7.1.2
* pytest 5.2.2
