import datetime
import hashlib
import json
import logging
import os
import sys

from leapp.compat import string_types
from leapp.exceptions import MissingActorAttributeError, WrongAttributeTypeError
from leapp.models import Model
from leapp.tags import Tag
from leapp.utils.meta import get_flattened_subclasses


class Actor(object):
    def __init__(self, messaging=None, logger=None):
        self._messaging = messaging
        self.log = (logger or logging.getLogger('leapp.actors')).getChild(self.name)

    @property
    def actor_files_paths(self):
        return os.getenv("LEAPP_FILES", "").split(":")

    @property
    def files_paths(self):
        return self.actor_files_paths + self.common_files_paths

    @property
    def common_files_paths(self):
        return os.getenv("LEAPP_COMMON_FILES", "").split(":")

    def get_folder_path(self, name):
        for path in self.files_paths:
            path = os.path.join(path, name)
            if os.path.isdir(path):
                return path
        return None

    def get_file_path(self, name):
        for path in self.files_paths:
            path = os.path.join(path, name)
            if os.path.isfile(path):
                return path
        return None

    def run(self, *args):
        os.environ['LEAPP_CURRENT_ACTOR'] = self.name
        try:
            self.process(*args)
        finally:
            os.environ.pop('LEAPP_CURRENT_ACTOR', None)

    def produce(self, *args):
        if self._messaging:
            for arg in args:
                if isinstance(arg, getattr(self.__class__, 'produces')):
                    message_data = json.dumps(arg.dump(), sort_keys=True)
                    message_hash = hashlib.sha256(message_data).hexdigest()
                    self._messaging.produce(arg.channel.name, {
                        'type': arg.__class__.__name__,
                        'actor': self.name,
                        'channel': arg.channel.name,
                        'stamp': datetime.datetime.utcnow().isoformat() + 'Z',
                        'message': {
                            'data': message_data,
                            'hash': message_hash
                        }
                    })

    def consume(self, *types):
        if self._messaging:
            return self._messaging.consume(*types)
        return ()


def _is_type(value_type):
    def validate(actor, name, value):
        if not isinstance(value, value_type):
            raise WrongAttributeTypeError('Actor {} attribute {} should be of type {}'.format(actor, name, value_type))
    return validate


def _is_tuple_of(value_type):
    def validate(actor, name, value):
        _is_type(tuple)(actor, name, value)
        if not value:
            raise WrongAttributeTypeError(
                'Actor {} attribute {} should at least one item of type {}'.format(actor, name, value_type))
        if not all(map(lambda item: isinstance(item, value_type), value)):
            raise WrongAttributeTypeError(
                'Actor {} attribute {} should contain only value of type {}'.format(actor, name, value_type))
    return validate


def _is_model_tuple(actor, name, value):
    _is_type(tuple)(actor, name, value)
    if not all([True] + list(map(lambda item: isinstance(item, type) and issubclass(item, Model), value))):
        raise WrongAttributeTypeError(
            'Actor {} attribute {} should contain only Models'.format(actor, name))


def _is_tag_tuple(actor, name, value):
    _is_type(tuple)(actor, name, value)
    if not all([True] + list(map(lambda item: isinstance(item, type) and issubclass(item, Tag), value))):
        raise WrongAttributeTypeError(
            'Actor {} attribute {} should contain only Tags'.format(actor, name))


def _get_attribute(actor, name, validator, required=False, default_value=None):
    value = getattr(actor, name, None)
    if not value and required:
        raise MissingActorAttributeError('Actor {} is missing attribute {}'.format(actor, name))
    validator(actor, name, value)
    if not value and default_value:
        value = default_value
    return name, value


def get_actor_metadata(actor):
    return dict([
        ('class_name', actor.__name__),
        ('path', os.path.dirname(sys.modules[actor.__module__].__file__)),
        _get_attribute(actor, 'name', _is_type(string_types), required=True),
        _get_attribute(actor, 'tags', _is_tag_tuple, required=True),
        _get_attribute(actor, 'consumes', _is_model_tuple, required=False),
        _get_attribute(actor, 'produces', _is_model_tuple, required=False),
        _get_attribute(actor, 'description', _is_type(string_types), required=False,
                       default_value='There has been no description provided for this actor')
    ])


def get_actors():
    actors = get_flattened_subclasses(Actor)
    for actor in actors:
        get_actor_metadata(actor)
    return actors
