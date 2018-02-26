import itertools
import json
import os
import sys

import click

from leapp.logger import configure_logger
from leapp.actors import get_actors
from leapp.tool.utils import find_project_basedir, load_all_from, get_project_metadata, requires_project


class RunChannels(object):
    def __init__(self):
        self._data = {}
        self._new_data = {}

    def produce(self, channel, message):
        self._new_data.setdefault(channel, []).append(message)

    def consume(self, *types):
        if not type:
            return itertools.chain(*self._data.values())
        lookup = {model.__name__: model for model in types}
        return (lookup[message['type']](**message['message'])
                for message in itertools.chain(*self._data.values()) if message['type'] in lookup)

    def load(self):
        self._data = get_project_metadata(find_project_basedir('.'))['channel_data']

    def get_new(self):
        return self._new_data

    def store(self):
        for channel in self._new_data.keys():
            self._data.setdefault(channel, []).extend(self._new_data[channel])
        metadata = get_project_metadata(find_project_basedir('.'))
        metadata.update({'channel_data': self._data})
        with open(os.path.join(find_project_basedir('.'), '.leapp/info'), 'w') as f:
            json.dump(metadata, f, indent=2)


@click.command('run')
@click.argument('actor-name')
@click.option('--discard-output', is_flag=True)
@click.option('--print-output', is_flag=True)
@requires_project
def cli(actor_name, discard_output, print_output):
    log = configure_logger()
    log.info("Woot")
    basedir = find_project_basedir('.')
    load_all_from(basedir)
    channels = RunChannels()
    channels.load()
    [actor for actor in get_actors() if actor.name == actor_name][0](channels=channels).process()
    if not discard_output:
        channels.store()
    if print_output:
        json.dump(channels.get_new(), sys.stdout, indent=2)
