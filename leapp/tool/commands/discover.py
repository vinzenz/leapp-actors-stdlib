import json as json_mod
import os
import sys

import click

from leapp.tool.utils import find_project_basedir, load_all_from, get_project_name, requires_project
from leapp.models import get_models
from leapp.actors import get_actors, get_actor_metadata
from leapp.channels import get_channels
from leapp.tags import get_tags


def _is_local(base_dir, cls):
    return os.path.realpath(sys.modules[cls.__module__].__file__).startswith(base_dir)


def _print_group(name, items):
    sys.stdout.write('{group}:\n'.format(group=name))
    for item in items:
        sys.stdout.write('   - {name:<35} {path}\n'.format(name=item.__name__, path=_get_class_file(item, False)))
    sys.stdout.write('\n')


def _get_class_file(cls, project_relative=True):
    path = os.path.abspath(sys.modules[cls.__module__].__file__.replace('.pyc', '.py'))
    return os.path.relpath(path, find_project_basedir('.') if project_relative else os.getcwd())


def _get_actor_details(actor):
    meta = get_actor_metadata(actor)
    meta['produces'] = tuple(model.__name__ for model in meta['produces'])
    meta['consumes'] = tuple(model.__name__ for model in meta['consumes'])
    meta['tags'] = tuple(tag.name for tag in meta['tags'])
    meta['path'] = _get_class_file(actor)
    return meta


def _get_tag_details(tag):
    return {'actors': [actor.__name__ for actor in tag.actors],
            'name': tag.name}


def _get_channel_details(channel):
    return {'name': channel().name,
            'path': _get_class_file(channel)}


def _get_model_details(model):
    return {'path': _get_class_file(model)}


@click.command('discover')
@click.option('--json', is_flag=True)
@requires_project
def cli(json):
    base_dir = find_project_basedir('.')
    load_all_from(base_dir)

    actors = [actor for actor in get_actors() if _is_local(base_dir, actor)]
    models = [model for model in get_models() if _is_local(base_dir, model)]
    channels = [channel for channel in get_channels() if _is_local(base_dir, channel)]
    tags = [tag for tag in get_tags() if _is_local(base_dir, tag)]
    if not json:
        _print_group('Models', models)
        _print_group('Channels', channels)
        _print_group('Actors', actors)
        _print_group('Tags', tags)
    else:
        output = {
            'project': get_project_name(base_dir),
            'base_dir': base_dir,
            'channels': {channel.__name__: _get_channel_details(channel) for channel in channels},
            'models': {model.__name__: _get_model_details(model) for model in models},
            'actors': {actor.__name__: _get_actor_details(actor) for actor in actors},
            'tags': {tag.name: _get_tag_details(tag) for tag in tags}
        }
        json_mod.dump(output, sys.stdout, indent=2)

