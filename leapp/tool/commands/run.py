import imp
import os
import pkgutil
import sys

import click

from leapp.channels import get_channels
from leapp.models import get_models
from leapp.actors import get_actors
from leapp.tool.utils import find_project_basedir, get_project_name


def load_modules(pkg_path):
    modules = []
    for importer, name, is_pkg in pkgutil.iter_modules([pkg_path]):
        if is_pkg:
            continue
        modules.append(importer.find_module(name).load_module(name))
    return modules


def construct_submodule(project_name, project_module, filter_fun, name, load_dir):
    modules = []
    if os.path.exists(load_dir):
        modules = load_modules(load_dir)

    sub_module = imp.new_module(project_name + '.' + name)
    setattr(project_module, name, sub_module)
    sys.modules[project_name + '.' + name] = sub_module

    for mod in modules:
        for item in (getattr(mod, name) for name in dir(mod) if not name.startswith('_')):
            if item in filter_fun():
                setattr(sub_module, item.__name__, item)


def construct_project_module(basedir):
    project_name = get_project_name(basedir)

    models_dir = os.path.join(basedir, 'models')
    channels_dir = os.path.join(basedir, 'channels')
    project_module = imp.new_module(project_name)
    sys.modules[project_name] = project_module

    construct_submodule(project_name, project_module, get_channels, 'channels', channels_dir)
    construct_submodule(project_name, project_module, get_models, 'models', models_dir)


@click.command('run')
@click.argument('actor-name')
def cli(actor_name):
    basedir = find_project_basedir('.')
    construct_project_module(basedir)
    actors_dir = os.path.join(basedir, 'actors')
    if os.path.exists(actors_dir):
        load_modules(actors_dir)
    [actor for actor in get_actors() if actor.name == actor_name][0]().process()
