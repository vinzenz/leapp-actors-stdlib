import json
import sys

import click

from leapp.logger import configure_logger
from leapp.actors import get_actors, Actor
from leapp.tool.utils import find_project_basedir, load_all_from, requires_project
from leapp.tool.utils import RunChannels


@click.command('run')
@click.argument('actor-name')
@click.option('--discard-output', is_flag=True)
@click.option('--print-output', is_flag=True)
@requires_project
def cli(actor_name, discard_output, print_output):
    log = configure_logger()
    basedir = find_project_basedir('.')
    log.info("Woot %s %s %s %s %s", log, basedir, print_output, discard_output, actor_name)
    load_all_from(basedir)
    channels = RunChannels()
    channels.load()
    actor_logger = log.getChild('actors')
    Actor.run([actor for actor in get_actors() if actor.__name__.lower() == actor_name.lower()][0](
        channels=channels, logger=actor_logger))
    if not discard_output:
        channels.store()
    if print_output:
        json.dump(channels.get_new(), sys.stdout, indent=2)
