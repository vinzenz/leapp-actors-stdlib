import os
import pkgutil

import click

from leapp.actors import get_actors
from leapp.tool.utils import find_project_basedir


def load_modules(pkg_path):
    modules = []
    for importer, name, is_pkg in pkgutil.iter_modules([pkg_path]):
        if is_pkg:
            continue
        modules.append(importer.find_module(name).load_module(name))
    return modules


def load_modules_from(path):
    if os.path.exists(path):
        if load_modules(path):
            return
        for _, dirs, _ in os.walk(path):
            for directory in dirs:
                load_modules(os.path.join(path, directory))


@click.command('run')
@click.argument('actor-name')
def cli(actor_name):
    basedir = find_project_basedir('.')
    for directory in ('channels', 'models', 'actors'):  # Order is NOT arbitrary - keep the order
        modules_dir = os.path.join(basedir, directory)
        load_modules_from(modules_dir)
    [actor for actor in get_actors() if actor.name == actor_name][0]().process()
