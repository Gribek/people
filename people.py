import decimal
from importlib import import_module

import click

from functions import db_functions


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
    models = ['Person', 'Login', 'Location', 'Contact']
    for model in models:
        cls = getattr(import_module('models'), model)
        attr = getattr(cls, category, None)
        if attr is not None:
            break
    else:
        print(f'There is no information about {category}')
        return None

    results = obj.most_occurrences(cls, attr, limit)
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


if __name__ == '__main__':
    cli()
