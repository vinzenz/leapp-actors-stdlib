import os

import click
import sys

from leapp.tool.utils import find_project_basedir, make_class_name, requires_project


@click.command('new-model')
@click.argument('model-name')
@requires_project
def cli(model_name):
    basedir = find_project_basedir('.')

    basedir = os.path.join(basedir, 'models')
    if not os.path.isdir(basedir):
        os.mkdir(basedir)

    model_path = os.path.join(basedir, model_name.lower() + '.py')
    if os.path.exists(model_path):
        raise click.UsageError("File already exists: {}".format(model_path))

    with open(model_path, 'w') as f:
        f.write('''from leapp.models import Model, fields


class {model_name}(Model):
    channel = None #  TODO: import appropriate channel and set it here
'''.format(model_name=make_class_name(model_name)))

    sys.stdout.write("New model {} has been created in {}\n".format(make_class_name(model_name),
                                                                    os.path.realpath(model_path)))
