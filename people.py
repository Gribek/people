import decimal
from importlib import import_module

import click

from functions import db_functions, password_score


@click.group()
def cli():
    pass


@cli.command('gender-percentage')
@db_functions
def man_women_percentage(obj):
    """Calculate man and women percentage in database"""
    decimal.getcontext().prec = 4
    male = decimal.Decimal(obj.count_entries('Person', 'gender', 'male'))
    female = decimal.Decimal(obj.count_entries('Person', 'gender', 'female'))
    male_percentage = male / (male + female) * 100
    female_percentage = female / (male + female) * 100
    print(f'male: {male_percentage}%', f'female: {female_percentage}%')


@cli.command('average-age')
@click.option('--gender',
              type=click.Choice(['male', 'female'], case_sensitive=False),
              default=None, help='Specify gender')
@db_functions
def average_age(obj, gender):
    """Calculate the average age of people."""
    kwargs = {'table': 'Person', 'column': 'age'}
    if gender is not None:
        kwargs['condition'] = 'gender'
        kwargs['cond_value'] = gender
    avg_value = obj.average_value(**kwargs)[0].avg
    print(f'Average age: {avg_value}')


@cli.command('most-common')
@click.argument('category')
@click.option('--limit', default=1, help='Number of results')
@db_functions
def most_common(obj, limit, category):
    results = obj.most_occurrences(category, limit)
    if results is None:
        print(f'There is no information about {category}')
        return None
    for result in results:
        print(getattr(result, category), result.count)


@cli.command('born-between')
@click.argument('lower')
@click.argument('upper')
@db_functions
def born_between(obj, lower, upper):
    """Find all people born between two dates."""
    result = obj.data_in_range('Person', 'date_of_birth', lower, upper)
    for p in result:
        print(p.title, p.firstname, p.lastname, p.date_of_birth)


@cli.command('password-security')
@db_functions
def password_security(obj):
    """Find the most secure password."""
    result = obj.get_data('Login', 'password')
    password = max((i.password for i in result), key=password_score)
    print(password)


if __name__ == '__main__':
    cli()
