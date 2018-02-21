import json as json_mod
import os
import sys

import click

from leapp.tool.utils import find_project_basedir, load_all_from, get_project_name
from leapp.models import get_models
from leapp.actors import get_actors, get_actor_metadata
from leapp.channels import get_channels


def is_local(base_dir, cls):
    return os.path.realpath(sys.modules[cls.__module__].__file__).startswith(base_dir)


def print_group(name, items):
    sys.stdout.write('{group}:\n'.format(group=name))
    for item in items:
        sys.stdout.write('   - {name:<25} ./{path}\n'.format(name=item.__name__, path=get_class_file(item)))
    sys.stdout.write('\n')


def get_class_file(cls):
    path = os.path.abspath(sys.modules[cls.__module__].__file__.replace('.pyc', '.py'))
    return os.path.relpath(path, find_project_basedir('.'))


def get_actor_details(actor):
    meta = get_actor_metadata(actor)
    meta['produces'] = tuple(model.__name__ for model in meta['produces'])
    meta['consumes'] = tuple(model.__name__ for model in meta['consumes'])
    meta['path'] = get_class_file(actor)
    return meta


def get_channel_details(channel):
    return {
            'name': channel().name,
            'path': get_class_file(channel)
        }


def get_model_details(model):
    return {
            'path': get_class_file(model)
        }


@click.command('discover')
@click.option('--json', is_flag=True)
def cli(json):
    base_dir = find_project_basedir('.')
    load_all_from(base_dir)

    actors = [actor for actor in get_actors() if is_local(base_dir, actor)]
    models = [model for model in get_models() if is_local(base_dir, model)]
    channels = [channel for channel in get_channels() if is_local(base_dir, channel)]
    if not json:
        print_group('Models', models)
        print_group('Channels', channels)
        print_group('Actors', actors)
    else:
        output = {
            'project': get_project_name(base_dir),
            'base_dir': base_dir,
            'channels': {channel.__name__: get_channel_details(channel) for channel in channels},
            'models': {model.__name__: get_model_details(model) for model in models},
            'actors': {actor.__name__: get_actor_details(actor) for actor in actors}
        }
        json_mod.dump(output, sys.stdout, indent=2)

