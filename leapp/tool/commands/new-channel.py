import os

import click

from leapp.tool.utils import find_project_basedir, make_name, make_class_name


@click.command('new-channel')
@click.argument('channel-name')
def cli(channel_name):
    basedir = find_project_basedir('.')
    if not basedir:
        raise click.UsageError('This command must be executed from the project directory')

    basedir = os.path.join(basedir, 'channels')
    if not os.path.isdir(basedir):
        os.mkdir(basedir)
    with open(os.path.join(basedir, channel_name.lower() + '.py'), 'w') as f:
        f.write('''from leapp.channels import Channel


class {channel_name}Channel(Channel):
    name = '{channel}'
    messages = ()
'''.format(channel_name=make_class_name(channel_name), channel=make_name(channel_name)))
