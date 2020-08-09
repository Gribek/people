import decimal

import click

from functions import db_functions, password_score, Result


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
    people = decimal.Decimal(obj.count_entries('Person'))
    female_perc = female / people * 100
    male_perc = male / people * 100
    r = Result((female_perc, male_perc), ('Female', 'Male'), ('%', '%'))
    r.display_single()


@cli.command('average-age')
@click.option('--gender',
              type=click.Choice(['male', 'female'], case_sensitive=False),
              default=None, help='Specify gender')
@db_functions
def average_age(obj, gender):
    """Calculate the average age of people."""
    kwargs = {'table': 'Person', 'column': 'age'}
    description = ''
    if gender is not None:
        kwargs['condition'] = 'gender'
        kwargs['cond_value'] = gender
        description += f'{gender} '
    avg_value = obj.average_value(**kwargs)[0].avg
    description += 'average age:'
    r = Result((avg_value,), (description.capitalize(),))
    r.display_single()


@cli.command('most-common')
@click.argument('category')
@click.option('--limit', default=1, help='Number of results')
@db_functions
def most_common(obj, limit, category):
    """Find the most common entries in the selected category."""
    result = obj.most_occurrences(category, limit)
    if result is None:
        print(f'There is no information about {category}')
        return None
    r = Result(((getattr(row, category), row.count) for row in result))
    r.display_multiple()


@cli.command('born-between')
@click.argument('lower')
@click.argument('upper')
@db_functions
def born_between(obj, lower, upper):
    """Find all people born between two dates."""
    result = obj.data_in_range('Person', 'date_of_birth', lower, upper)
    result_sorted = sorted(result, key=lambda x: x.date_of_birth)
    r = Result(((p.title, p.firstname, p.lastname, p.date_of_birth)
                for p in result_sorted))
    r.display_multiple()


@cli.command('password-security')
@db_functions
def password_security(obj):
    """Find the most secure password."""
    result = obj.get_data('Login', 'password')
    password = max((i.password for i in result), key=password_score)
    r = Result((password,), ('The most secure password:',))
    r.display_single()


if __name__ == '__main__':
    cli()
