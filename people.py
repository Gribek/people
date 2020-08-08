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
    print(f'{male_percentage}%', f'{female_percentage}%')


if __name__ == '__main__':
    cli()
