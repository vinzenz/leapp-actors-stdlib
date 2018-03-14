import functools
import itertools
import json
import os
import pkgutil
import re
import socket

import click

from leapp.utils.actorapi import get_actor_api


def requires_project(f):
    @functools.wraps(f)
    def checker(*args, **kwargs):
        if not find_project_basedir('.'):
            raise click.UsageError('This command must be executed from the project directory')
        return f(*args, **kwargs)
    return checker


def load_modules(pkg_path, use_repo=None):
    modules = []
    from leapp.libraries import actor as actor_module
    for importer, name, is_pkg in pkgutil.iter_modules([pkg_path]):
        if is_pkg:
            continue
        if use_repo:
            for actor in use_repo.actors:
                actor_dir = os.path.dirname(actor.directory)
                if importer.path.endswith(actor_dir):
                    with actor.injected_context():
                        modules.append(importer.find_module(name).load_module(name))
                    break
        else:
            modules.append(importer.find_module(name).load_module(name))
    return modules


def load_modules_from(path, use_repo=None):
    if os.path.exists(path):
        if load_modules(path, use_repo=use_repo):
            return
        for root, _, _ in os.walk(path):
            load_modules(root, use_repo=use_repo)


def load_all_from(basedir, use_repo=None):
    for directory in ('channels', 'models', 'tags', 'actors', 'workflows'):  # Order is NOT arbitrary - keep the order
        modules_dir = os.path.join(basedir, directory)
        load_modules_from(modules_dir, use_repo=use_repo if directory == 'actors' else None)


def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name.replace('-', '_'))
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def make_class_name(name):
    return ''.join(map(lambda x: x.capitalize(), to_snake_case(name).split('_')))


def make_name(name):
    return to_snake_case(name).lower()


def find_project_basedir(path):
    path = os.path.realpath(path)
    while True:
        if os.path.isdir(os.path.join(path, '.leapp')):
            return path
        path, current = os.path.split(path)
        if not current:
            return None


def get_project_metadata(path):
    basedir = find_project_basedir(path)
    if basedir:
        with open(os.path.join(basedir, '.leapp', 'info'), 'r') as f:
            return json.load(f)
    return {}


def get_project_name(path):
    return get_project_metadata(path)['name']


class BaseChannels(object):
    def __init__(self, produce_hook=None):
        self._data = []
        self._new_data = []
        self._session = get_actor_api()
        self._produce_hook = produce_hook

    def set_produce_hook(self, produce_hook):
        self._produce_hook = produce_hook

    def produce(self, channel, message):
        message.setdefault('channel', channel)
        message.setdefault('phase', os.environ.get('LEAPP_CURRENT_PHASE', 'NON-WORKFLOW-EXECUTION'))
        message.setdefault('context', os.environ.get('LEAPP_EXECUTION_ID', 'TESTING-CONTEXT'))
        message.setdefault('hostname', os.environ.get('LEAPP_HOSTNAME', socket.getfqdn()))
        self._session.post('leapp://localhost/actors/v1/message', json=message)
        self._new_data.append(message)
        if self.produce_hook:
            self.produce_hook(message)

    def consume(self, *types):
        if not type:
            return self._data
        lookup = {model.__name__: model for model in types}
        return (lookup[message['type']](**json.loads(message['message']['data']))
                for message in self._data if message['type'] in lookup)


class WorkflowChannels(BaseChannels):
    def __init__(self):
        super(WorkflowChannels, self).__init__()

    def load(self, consumes):
        names = [consume.__name__ for consume in consumes]
        request = self._session.post('leapp://localhost/actors/v1/messages', json={
            'context': os.environ.get('LEAPP_EXECUTION_ID', 'TESTING-CONTEXT'),
            'messages': names})
        request.raise_for_status()
        self._data = request.json()['messages']


class RunChannels(BaseChannels):
    def __init__(self):
        super(RunChannels, self).__init__()

    def load(self):
        self._data = get_project_metadata(find_project_basedir('.'))['channel_data']

    def get_new(self):
        return self._new_data

    def store(self):
        self._data.extend(self._new_data)
        metadata = get_project_metadata(find_project_basedir('.'))
        metadata.update({'channel_data': self._data})
        with open(os.path.join(find_project_basedir('.'), '.leapp/info'), 'w') as f:
            json.dump(metadata, f, indent=2)