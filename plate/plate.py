import click
from configparser import ConfigParser
from shutil import copy
from os import getcwd, path, walk, listdir, mkdir, stat


CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower())


class Config(object):
    def __init__(self):
        config = ConfigParser()
        config.read(path.join(path.abspath(path.dirname(__file__)),
                              './plate.cfg'))
        self.home_dir = path.expanduser(config.get('settings', 'home_dir'))
        self.editor = config.get('settings', 'editor')


pass_config = click.make_pass_decorator(Config, ensure=True)


def create_plate(config):
    if click.confirm(
        "\nWould you like to create a new portfolio?\n"):
        portfolio = click.prompt(
            "\nWhat would you like to name this portfolio?\n")
        mkdir(config.home_dir + portfolio)
    else:
        portfolio = 'none'
    return portfolio


def no_portfolio(config):
    portfolios = next(walk(config.home_dir))[1]
    if len(portfolios) == 0:
        click.echo("\nYou don't have any portfolios.\n")
        portfolio = 'none'
    else:
        click.secho("\nHere's a list of your portfolios:", bold=True)
        for p in portfolios:
            click.echo(p)
        portfolio = click.prompt(
            '\nWhich portfolio would you like to use?\n')
        while portfolio not in portfolios:
            if portfolio == 'none':
                break
            click.echo("\nSorry, that portfolio doesn't exist")
            portfolio = click.prompt(
                '\nWhich portfolio would you like to use?\n')
    return portfolio


def no_plate_name(plate_dir, portfolio, use):
    plates = listdir(plate_dir)
    if len(plates) == 0:
        click.echo(f"\nSorry, you don't have any {portfolio} plates")
    else:
        click.secho("\nHere's a list of your plates:", bold=True)
        for p in plates:
            p_path = plate_dir + p
            if path.isfile(p_path):
                click.echo(p)
        plate_name = click.prompt(
            f'\nWhich plate would you like to {use}?\n')
        while plate_name not in plates:
            click.echo("Sorry, that plate doesn't exist")
            plate_name = click.prompt(
                f'\nWhich plate would you like to {use}?\n')
    return plate_name


def no_etching_name():
    if click.confirm(
        "\nWould you like to name your new etching? \
         (If 'no', it will be given the same name as its plate.) \n"):
        etching_name = click.prompt(
            "\nOk, what's the name of your new etching?\n")
    else:
        etching_name = ''
    return etching_name


@click.group()
def cli():
    """Welcome to Plate!
    
    The Plate vocabulary utilizes the art of printmaking as metaphor,
    here are some terms to get you started:
    "plate" - what we call a template
    "etch" - how to create a plate
    "press" - how to use a plate to create a new file
    "etching" - what we call the new file created by the plate
    "portfolios" - categories for your plates, defined by you"""
    pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--edit', is_flag=True, help='make changes to your settings')
@pass_config
def settings(config, edit):
    """Edit your settings for Plate here!
    
    This handles the plate.cfg file which tells Plate a few things:
    Where your home directory is (the place Plate stores all of your plates)
    and what your preferred text editor is for when you etch, edit, or press
    your plates"""
    click.echo('Your Plate directory is %s' % config.home_dir)
    if edit:
        click.edit(editor=config.editor, filename='./.plate/config.ini')


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '-type',
    '--plate-type',
    help='pick a pre-existing portfolio or create a new one')
@click.option('-plate', '--plate-name', help='name your plate')
@pass_config
def etch(config, portfolio, plate_name):
    """Etch your plate here!"""
    portfolios = next(walk(config.home_dir))[1]
    if portfolio is None:
        if len(portfolios) == 0:
            click.echo("\nYou don't have any portfolios.")
            portfolio = create_plate(config=config)
        else:
            click.secho("\nHere's a list of your portfolios:", bold=True)
            for p in portfolios:
                click.echo(p)
            if click.confirm(
                "\nWould you like to use one of these to etch your plate?\n"):
                portfolio = click.prompt(
                    "\nWhich portfolio would you like to use?\n")
            else:
                portfolio = create_plate(config=config)
    else:
        if portfolio not in portfolios:
            mkdir(config.home_dir + portfolio)
    if portfolio != 'none':
        plate_dir = config.home_dir + portfolio + '/'
    else:
        plate_dir = config.home_dir
    if plate_name is None:
        plate_name = click.prompt(
            "\nWhat would you like to name your new Plate?\n")
    if '.' not in plate_name:
        plate_ext = click.prompt("Please add an extension")
        if '.' not in plate_ext:
            plate_ext = '.' + plate_ext
        plate_name = plate_name + plate_ext
    plate_path = plate_dir + plate_name
    open(plate_path, 'w+')
    portfolio = ' ' + portfolio
    plate_name = ' ' + plate_name
    click.secho(
        f"\nYour{portfolio}{plate_name} plate has been etched!\n",
        bold=True)
    if click.confirm("Would you like to open it now?\n"):
        click.edit(editor=config.editor, filename=plate_path)
    click.secho('\nGoodbye!\n', bold=True, fg='green')


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('-type', '--plate-type', help='specify a portfolio')
@click.option(
    '-plate',
    '--plate-name',
    help='specify which plate you want to press')
@click.option('-name', '--etching-name', help='name your new file')
@pass_config
def press(config, portfolio, plate_name, etching_name):
    """Press your plate here!"""
    if portfolio is None:
        portfolio = no_portfolio(config=config)
    if portfolio != 'none':
        plate_dir = config.home_dir + portfolio + '/'
    else:
        plate_dir = config.home_dir
    if plate_name is None:
        plate_name = no_plate_name(plate_dir=plate_dir,
                                   portfolio=portfolio,
                                   use='press')
    cwd = getcwd()
    if etching_name is None:
        etching_name = no_etching_name()
    if '.' not in etching_name:
        plate_ext = plate_name.split('.')[1]
        etching_name = etching_name + plate_ext
    if path.isfile(etching_name):
        click.echo(
            "\nSorry, a file by that name already exists in this directory.")
        etching_name = click.prompt(
            "What would you like to name your new etching?\n")
    etching_path = cwd + '/' + etching_name
    plate_to_press = plate_dir + plate_name
    copy(plate_to_press, etching_path)
    if etching_name == '':
        etching_name = ' ' + plate_name
    else:
        etching_name = ' ' + etching_name
    if portfolio == 'none':
        portfolio = ''
    else:
        portfolio = ' ' + portfolio
    plate_name = ' ' + plate_name
    click.secho(f"\nYour etching{etching_name} has been pressed" +
                f" with the{portfolio}{plate_name} plate!\n",
                bold=True)
    if click.confirm("Would you like to open your etching now?\n"):
        click.edit(editor=config.editor, filename=etching_path)
    click.secho('\nGoodbye!\n', bold=True, fg='blue')


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '-type',
    '--plate-type',
    help='specify which portfolio the plate you want to edit is')
@click.option('-plate', '--plate-name')
@pass_config
def edit(config, portfolio, plate_name):
    """Edit your plates here!"""
    if portfolio is None:
        portfolio = no_portfolio(config=config)
    if portfolio != 'none':
        plate_dir = config.home_dir + portfolio + '/'
    else:
        plate_dir = config.home_dir
    if plate_name is None:
        plate_name = no_plate_name(plate_dir=plate_dir,
                                   portfolio=portfolio,
                                   use='edit')
    plate_path = plate_dir + plate_name
    click.echo(f'\nOpening {plate_name} now!\n')
    plate_stats = stat(plate_path)
    plate_state = plate_stats[8]
    click.edit(editor=config.editor, filename=plate_path)
    while stat(plate_path)[8] == plate_state:
        continue
    click.secho(f'{plate_name} has been edited!\n', bold=True)
