import os
import pkgutil
import socket

from leapp.tool import commands
from leapp.tool.commands import workflow
from leapp.utils.clicmd import command, command_opt


__version__ = '1.0'
SHORT_HELP = "actor-tool is a leapp actor project management tool"
LONG_HELP = """
This tool is designed to get quickly started with leapp actor development
"""
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def load_commands():
    _load_commands_from(commands.__file__)

    _load_commands_from(commands.workflow.__file__)
    cli.command.add_sub(workflow.workflow.command)


def _load_commands_from(path):
    pkg_path = os.path.dirname(path)
    for importer, name, is_pkg in pkgutil.iter_modules([pkg_path]):
        if is_pkg:
            continue
        mod = importer.find_module(name).load_module(name)
        if hasattr(mod.cli, 'command'):
            if not mod.cli.command.parent:
                cli.command.add_sub(mod.cli.command)


@command('', help=LONG_HELP)
@command_opt('debug', is_flag=True, help='Enables debug logging')
def cli(args):
    os.environ['LEAPP_DEBUG'] = '1' if args.debug else '0'


def main():
    os.environ['LEAPP_HOSTNAME'] = socket.getfqdn()
    from argparse import ArgumentParser
    parser = ArgumentParser(prog='snactor', version='snactor version {}'.format(__version__))
    parser.set_defaults(func=None)
    s = parser.add_subparsers(description='Main commands')
    load_commands()
    cli.command.apply_parser(s, parser=parser)
    args = parser.parse_args()
    args.func(args)

