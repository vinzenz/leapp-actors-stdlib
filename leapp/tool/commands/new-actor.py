import os

import click

from leapp.tool.utils import find_project_basedir


@click.command('new-actor')
@click.argument('actor-name')
def cli(actor_name):
    basedir = find_project_basedir('.')
    if not basedir:
        raise click.UsageError('This command must be executed from the project directory')

    basedir = os.path.join(basedir, 'actors')
    if not os.path.isdir(basedir):
        os.mkdir(basedir)
    with open(os.path.join(basedir, actor_name.lower() + '.py'), 'w') as f:
        f.write('''from leapp.actors import Actor


class {actor_class}(Actor):
    name = '{actor_name}'
    description = 'For the actor {actor_name} has been no description provided.'
    inputs = ()
    outputs = ()
    tags = ()

    def process(self):
        pass
'''.format(actor_class=actor_name[0].upper() + actor_name[1:], actor_name=actor_name.lower()))
