import decimal

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


if __name__ == '__main__':
    cli()
