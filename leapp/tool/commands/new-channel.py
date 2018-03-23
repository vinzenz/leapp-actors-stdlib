import os

import click
import sys

from leapp.tool.utils import find_project_basedir, make_name, make_class_name


@click.command('new-channel')
@click.argument('channel-name')
def cli(channel_name):
    basedir = find_project_basedir('.')

    basedir = os.path.join(basedir, 'channels')
    if not os.path.isdir(basedir):
        os.mkdir(basedir)

    channel_path = os.path.join(basedir, channel_name.lower() + '.py')
    if os.path.exists(channel_path):
        raise click.UsageError("File already exists: {}".format(channel_path))

    channel_path = os.path.join(basedir, channel_name.lower() + '.py')
    with open(channel_path, 'w') as f:
        f.write('''from leapp.channels import Channel


class {channel_name}Channel(Channel):
    name = '{channel}'
'''.format(channel_name=make_class_name(channel_name), channel=make_name(channel_name)))

    sys.stdout.write("New channel {} has been created in {}\n".format(make_class_name(channel_name),
                                                                      os.path.realpath(channel_path)))
