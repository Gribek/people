# People
### Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Settings](#settings)
* [Available commands](#available-commands)

### General info
The goal of this project was to prepare scripts that create a user database and then be able to obtain statistical 
information about the users via the command line interface. The program uses the randomuser API (https://randomuser.me/) 
as a source of data. It also performs some arbitrary modifications of initial data before storing them in the database.

### Technologies
* Python 3.8.5
* SQLite 3.22.0
* peewee 3.13.3
* click 7.1.2
* pytest 5.2.2

### Setup
##### Using Docker
Download the repository and then run the following command:
```
docker-compose run --rm app
```
It will automatically attach you to the container and provide the pseudo terminal, where you can try the commands described [below](#available-commands).  

This is a default setup, which uses current settings and the attached database file with some test data.
If you want to start with an empty database, follow the instructions in [Database setup](#Database-setup).
Remember that if you make changes to the settings.py file (e.g. renaming the database), you need to rebuild the docker image before running ```docker-compose run``` again:
```
docker-compose build
```

##### Using virtual environment
Download the repository and prepare a new virtual environment. Then install all dependencies using the command:
```
$ pip install -r requirements.txt
```
Now you can try the commands described [below](#available-commands).  

This is a default setup, which uses current settings and the attached database file with some test data.
If you want to start with an empty database, follow the instructions in [Database setup](#Database-setup)

##### Database setup
To start with an empty database, you can delete the people.db file (from db subdirectory) or rename the database file in the settings (check [Settings](#settings)).  

Run the following scripts (from a virtual environment or a docker container):
```
python models.py

python load_people.py
```
The first one will create a new database file and migrate all models.
The latter will download data from randomuser API, make modifications, and save them to the database.

### Settings
The settings.py file contain the configuration for the following:
* database filename
* randomuser API url
* parameters used when a request is made to the randomuser API
* configuration of data modification to be performed

##### Database filename
To rename the database file, change the value of the DATABASE variable, by default set to 'people.db':
```
DATABASE = 'people.db'
```

##### API request parameters

The variables sent in the request to the randomuser API can be found in the API_PARAMETERS dictionary.
By default, parameters are set so that the data received in the response contains information about 1000 users:
```
API_PARAMETERS = {'results': 1000, 'seed': 'abc'}
```
You can find more information about randomuser API request parameters in its documentation https://randomuser.me/documentation.

##### Modifications
All modifications are configured in the DATA_MODIFICATIONS variable. 
Each of them is a single dictionary selecting the value to modify and the method to run.

### Available commands

All commands are called from the people.py script.

**1. _gender-percentage_ - display the percentage of men and women**
  
 Command pattern: people.py gender-percentage 
  
 Example input:
 ```
 python people.py gender-percentage
 ```

**2. _average-age_ - display the average age of people**

 Command pattern: people.py average-age [OPTIONS]
 
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
 
