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


@pass_config
def create_plate(config):
    if click.confirm(
        "\nWould you like to create a new plate type?\n"
    ):
        plate_type = click.prompt(
            "\nWhat would you like to name this plate type?\n")
        mkdir(config.home_dir + plate_type)
    else:
        plate_type = 'none'
    return plate_type


@pass_config
def no_plate_type(config):
    plate_types = next(walk(config.home_dir))[1]
    if len(plate_types) == 0:
        click.echo("\nYou don't have any plate types.\n")
        plate_type = 'none'
    else:
        click.secho("\nHere's a list of your plate types:", bold=True)
        for p in plate_types:
            click.echo(p)
        plate_type = click.prompt(
            '\nWhich plate type would you like to use?\n')
        while plate_type not in plate_types:
            if plate_type == 'none':
                break
            click.echo("\nSorry, that plate type doesn't exist")
            plate_type = click.prompt(
                '\nWhich plate type would you like to use?\n')
    return plate_type


def no_plate_name(plate_dir, plate_type, use):
    plates = listdir(plate_dir)
    if len(plates) == 0:
        click.echo(f"\nSorry, you don't have any {plate_type} plates")
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
    pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--edit', is_flag=True)
@pass_config
def settings(config, edit):
    click.echo('Your Plate directory is %s' % config.home_dir)
    if edit:
        click.edit(editor=config.editor, filename='./.plate/config.ini')


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('-type', '--plate-type')
@click.option('-plate', '--plate-name')
@pass_config
def etch(config, plate_type, plate_name):
    plate_types = next(walk(config.home_dir))[1]
    if plate_type is None:
        if len(plate_types) == 0:
            click.echo("\nYou don't have any plate types.")
            plate_type = create_plate()
        else:
            click.secho("\nHere's a list of your plate types:", bold=True)
            for p in plate_types:
                click.echo(p)
            if click.confirm(
                "\nWould you like to use one of these to etch your plate?\n",
                abort=True
            ):
                plate_type = click.prompt(
                    "\nWhich plate type would you like to use?\n",
                    abort=True
                )
            else:
                plate_type = create_plate()
    else:
        if plate_type not in plate_types:
            mkdir(config.home_dir + plate_type)
    if plate_type != 'none':
        plate_dir = config.home_dir + plate_type + '/'
    else:
        plate_dir = config.home_dir
    if plate_name is None:
        plate_name = click.prompt(
            "\nWhat would you like to name your new Plate?\n",
            abort=True
        )
    if '.' not in plate_name:
        plate_ext = click.prompt("Please add an extension", abort=True)
        if '.' not in plate_ext:
            plate_ext = '.' + plate_ext
        plate_name = plate_name + plate_ext
    plate_path = plate_dir + plate_name
    open(plate_path, 'w+')
    plate_type = ' ' + plate_type
    plate_name = ' ' + plate_name
    click.secho(
        f"\nYour{plate_type}{plate_name} plate has been etched!\n",
        bold=True)
    if click.confirm("Would you like to open it now?\n"):
        click.edit(editor=config.editor, filename=plate_path)
    click.secho('\nGoodbye!\n', bold=True, fg='green')


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('-type', '--plate-type')
@click.option('-plate', '--plate-name')
@click.option('-name', '--etching-name')
@pass_config
def press(config, plate_type, plate_name, etching_name):
    if plate_type is None:
        plate_type = no_plate_type()
    if plate_type != 'none':
        plate_dir = config.home_dir + plate_type + '/'
    else:
        plate_dir = config.home_dir
    if plate_name is None:
        plate_name = no_plate_name(plate_dir=plate_dir,
                                   plate_type=plate_type,
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
            "What would you like to name your new etching?\n",
            abort=True
        )
    etching_path = cwd + '/' + etching_name
    plate_to_press = plate_dir + plate_name
    copy(plate_to_press, etching_path)
    if etching_name == '':
        etching_name = ' ' + plate_name
    else:
        etching_name = ' ' + etching_name
    if plate_type == 'none':
        plate_type = ''
    else:
        plate_type = ' ' + plate_type
    plate_name = ' ' + plate_name
    click.secho(f"\nYour etching{etching_name} has been pressed" +
                f" with the{plate_type}{plate_name} plate!\n",
                bold=True)
    if click.confirm("Would you like to open your etching now?\n"):
        click.edit(editor=config.editor, filename=etching_path)
    click.secho('\nGoodbye!\n', bold=True, fg='blue')


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('-type', '--plate-type')
@click.option('-plate', '--plate-name')
@pass_config
def edit(config, plate_type, plate_name):
    if plate_type is None:
        plate_type = no_plate_type()
    if plate_type != 'none':
        plate_dir = config.home_dir + plate_type + '/'
    else:
        plate_dir = config.home_dir
    if plate_name is None:
        plate_name = no_plate_name(plate_dir=plate_dir,
                                   plate_type=plate_type,
                                   use='edit')
    plate_path = plate_dir + plate_name
    click.echo(f'\nOpening {plate_name} now!\n')
    plate_stats = stat(plate_path)
    plate_state = plate_stats[8]
    click.edit(editor=config.editor, filename=plate_path)
    while stat(plate_path)[8] == plate_state:
        continue
    click.secho(f'{plate_name} has been edited!\n', bold=True)
