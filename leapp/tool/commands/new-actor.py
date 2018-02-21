import os

import click

from leapp.tool.utils import find_project_basedir, make_class_name, make_name


@click.command('new-actor')
@click.argument('actor-name')
def cli(actor_name):
    basedir = find_project_basedir('.')
    if not basedir:
        raise click.UsageError('This command must be executed from the project directory')

    actors_dir = os.path.join(basedir, 'actors')
    if not os.path.isdir(actors_dir):
        os.mkdir(actors_dir)

    actor_dir = os.path.join(actors_dir, actor_name.lower())
    if not os.path.isdir(actor_dir):
        os.mkdir(actor_dir)

    actor_test_dir = os.path.join(actor_dir, 'tests')
    if not os.path.isdir(actor_test_dir):
        os.mkdir(actor_test_dir)

    actor_path = os.path.join(actor_dir, 'actor.py')
    if os.path.exists(actor_path):
        raise click.UsageError("File already exists")

    with open(actor_path, 'w') as f:
        f.write('''from leapp.actors import Actor


class {actor_class}(Actor):
    name = '{actor_name}'
    description = 'For the actor {actor_name} has been no description provided.'
    consumes = ()
    produces = ()
    tags = ()

    def process(self):
        pass
'''.format(actor_class=make_class_name(actor_name), actor_name=make_name(actor_name)))
