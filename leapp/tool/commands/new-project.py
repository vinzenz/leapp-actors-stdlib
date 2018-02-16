import json
import os


import click


@click.command('new-project')
@click.argument('name')
def cli(name):
    basedir = os.path.join('.', name)
    if not os.path.isdir(basedir):
        os.mkdir(basedir)
        with open(os.path.join(basedir, '.leapp'), 'w') as f:
            json.dump({
                'name': name,
                'channel_data': {}
            }, f)
        print "New project {} has been created in {}".format(name, os.path.realpath(name))
