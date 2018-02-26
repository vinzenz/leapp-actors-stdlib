import os

import click

from leapp.tool.utils import find_project_basedir, make_name, make_class_name, requires_project


@click.command('new-tag')
@click.argument('tag-name')
@requires_project
def cli(tag_name):
    basedir = find_project_basedir('.')
    if not basedir:
        raise click.UsageError('This command must be executed from the project directory')

    basedir = os.path.join(basedir, 'tags')
    if not os.path.isdir(basedir):
        os.mkdir(basedir)

    if os.path.exists(os.path.join(basedir, tag_name.lower() + '.py')):
        raise click.UsageError("File already exists")

    with open(os.path.join(basedir, tag_name.lower() + '.py'), 'w') as f:
        f.write('''from leapp.tags import Tag


class {tag_name}Tag(Tag):
    name = '{tag}'
'''.format(tag_name=make_class_name(tag_name), tag=make_name(tag_name)))
