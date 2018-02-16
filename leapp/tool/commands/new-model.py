import os

import click

from leapp.tool.utils import find_project_basedir


@click.command('new-model')
@click.argument('model-name')
def cli(model_name):
    basedir = find_project_basedir('.')
    if not basedir:
        raise click.UsageError('This command must be executed from the project directory')
    basedir = os.path.join(basedir, 'models')
    if not os.path.isdir(basedir):
        os.mkdir(basedir)
    with open(os.path.join(basedir, model_name.lower() + '.py'), 'w') as f:
        f.write('''from leapp.models import Model, fields


class {model_name}(Model):
    pass
'''.format(model_name=model_name[0].upper() + model_name[1:]))
