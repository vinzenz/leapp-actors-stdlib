import os
import pkgutil
import socket

import click

from . import commands
from .commands import workflow

__version__ = '1.0'
SHORT_HELP = "actor-tool is a leapp actor project management tool"
LONG_HELP = """
This tool is designed to get quickly started with leapp actor development
"""
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def load_commands():
    _load_commands_from(commands.__file__)

    cli.add_command(workflow.workflow)
    _load_commands_from(commands.workflow.__file__)


def _load_commands_from(path):
    pkg_path = os.path.dirname(path)
    for importer, name, is_pkg in pkgutil.iter_modules([pkg_path]):
        if is_pkg:
            continue
        mod = importer.find_module(name).load_module(name)
        cli.add_command(mod.cli)


@click.group('actor-tool', help=LONG_HELP, short_help=SHORT_HELP, context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli():
    pass


def main():
    os.environ['LEAPP_HOSTNAME'] = socket.getfqdn()
    load_commands()
    cli()
