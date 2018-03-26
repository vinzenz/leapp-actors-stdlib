import json
import multiprocessing
import os
import socket

from leapp.tool.utils import get_project_metadata, find_project_basedir
from leapp.utils.actorapi import get_actor_api


class BaseChannels(object):
    def __init__(self):
        self._data = []
        self._new_data = []

    def produce(self, channel, message):
        message.setdefault('channel', channel)
        message.setdefault('phase', os.environ.get('LEAPP_CURRENT_PHASE', 'NON-WORKFLOW-EXECUTION'))
        message.setdefault('context', os.environ.get('LEAPP_EXECUTION_ID', 'TESTING-CONTEXT'))
        message.setdefault('hostname', os.environ.get('LEAPP_HOSTNAME', socket.getfqdn()))
        self._new_data.append(message)
        return message

    def consume(self, *types):
        if not type:
            return self._data + self._new_data
        lookup = {model.__name__: model for model in types}
        return (lookup[message['type']].create(json.loads(message['message']['data']))
                for message in (self._data + self._data) if message['type'] in lookup)


class DaemonAPIChannels(BaseChannels):
    def __init__(self):
        super(DaemonAPIChannels, self).__init__()
        self._session = get_actor_api()

    def produce(self, channel, message):
        message = super(DaemonAPIChannels, self).produce(channel, message)
        self._session.post('leapp://localhost/actors/v1/message', json=message)
        return message

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
        self._manager = multiprocessing.Manager()
        self._data = self._manager.list()
        self._new_data = self._manager.list()

    def load(self):
        self._data = self._manager.list(get_project_metadata(find_project_basedir('.'))['channel_data'])

    def get_new(self):
        return list(self._new_data)

    def store(self):
        self._data.extend(self._new_data)
        metadata = get_project_metadata(find_project_basedir('.'))
        metadata.update({'channel_data': list(self._data)})
        with open(os.path.join(find_project_basedir('.'), '.leapp/info'), 'w') as f:
            json.dump(metadata, f, indent=2)
