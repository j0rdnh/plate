import click
from configparser import ConfigParser
from shutil import copy
from os import getcwd, path, walk, listdir, mkdir


CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower())


class Config(object):
    def __init__(self):
        config = ConfigParser()
        config.read(path.join(path.abspath(path.dirname(__file__)),
                              '../plate.cfg'))
        self.home_dir = path.expanduser(config.get('settings', 'home_dir'))
        self.editor = config.get('settings', 'editor')


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
def cli():
    pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--edit', is_flag=True)
@pass_config
def config(config, edit):
    click.echo('Your Plate directory is %s' % config.home_dir)
    if edit:
        click.edit(editor=config.editor, filename='./.plate/config.ini')


@pass_config
def create_plate(config):
    if click.confirm(
        "\nWould you like to create a new Plate Type?\n"
    ):
        plate_type = click.prompt(
            "\nWhat would you like to name this Plate Type?\n")
        mkdir(config.home_dir + plate_type)
    else:
        plate_type = 'none'
    return plate_type


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('-type', '--plate-type')
@click.option('-plate', '--plate-name')
@pass_config
def etch(config, plate_type, plate_name):
    plate_types = next(walk(config.home_dir))[1]
    if plate_type is None:
        if len(plate_types) == 0:
            click.echo("\nYou don't have any Plate Types.")
            plate_type = create_plate()
        else:
            click.secho("\nHere's a list of your Plate Types:", bold=True)
            for p in plate_types:
                click.echo(p)
            if click.confirm(
                "\nWould you like to use one of these to Etch your Plate?\n"
            ):
                plate_type = click.prompt(
                    "\nWhich Plate Type would you like to use?\n")
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
            "\nWhat would you like to name your new Plate?\n")
    plate_path = plate_dir + plate_name
    open(plate_path, 'w+')
    plate_type = ' ' + plate_type
    plate_name = ' ' + plate_name
    click.secho(
        "\nYour{}{} Plate has been Etched!\n".format(plate_type, plate_name),
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
        plate_types = next(walk(config.home_dir))[1]
        if len(plate_types) == 0:
            click.echo("\nYou don't have any Plate Types.\n")
            plate_type = 'none'
        else:
            click.secho("\nHere's a list of your Plate Types:", bold=True)
            for p in plate_types:
                click.echo(p)
            plate_type = click.prompt(
                '\nWhich Plate Type would you like to Press?\n')
            while plate_type not in plate_types:
                if plate_type == 'none':
                    break
                click.echo("\nSorry, that Plate Type doesn't exist")
                plate_type = click.prompt(
                    '\nWhich Plate Type would you like to Press?\n')
    if plate_type != 'none':
        plate_dir = config.home_dir + plate_type + '/'
    else:
        plate_dir = config.home_dir
    if plate_name is None:
        plates = listdir(plate_dir)
        if len(plates) == 0:
            click.echo("\nSorry, you don't have any %s Plates" % plate_type)
        else:
            click.secho("\nHere's a list of your Plates:", bold=True)
            for p in plates:
                if path.isfile(p):
                    click.echo(p)
            plate_name = click.prompt(
                '\nWhich Plate would you like to Press?\n')
            while plate_name not in plates:
                click.echo("Sorry, that Plate doesn't exist")
                plate_name = click.prompt(
                    '\nWhich Plate would you like to Press?\n')
    cwd = getcwd()
    if etching_name is None:
        if click.confirm(
            "\nWould you like to name your new Etching? \
             (If 'no', it will be given the same name as its Plate.) \n"):
            etching_name = click.prompt(
                "\nOk, what's the name of your new Etching?\n")
        else:
            etching_name = ''
    etching_path = cwd + '/' + etching_name
    plate_to_press = plate_dir + plate_name
    copy(plate_to_press, etching_path)
    if etching_name == '':
        etching_name = ' ' + plate_name
    if plate_type == 'none':
        plate_type = ''
    else:
        plate_type = ' ' + plate_type
    plate_name = ' ' + plate_name
    click.secho(
        "\nYour Etching{} has been pressed with the{}{} Plate!\n".format(
            etching_name, plate_type, plate_name),
        bold=True)
    if click.confirm("Would you like to open your Etching now?\n"):
        click.edit(editor=config.editor, filename=etching_path)
    click.secho('\nGoodbye!\n', bold=True, fg='blue')
