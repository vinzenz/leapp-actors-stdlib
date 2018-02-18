import json

from leapp.exceptions import MissingActorAttributeError, WrongAttributeTypeError
from leapp.utils.meta import get_flattened_subclasses
from leapp.models import Model


class Actor(object):
    def produce(self, *args):
        for arg in args:
            if isinstance(arg, getattr(self.__class__, 'produces')):
                print json.dumps({arg.channel.name: [arg.__schema__().dump(arg).data]}, indent=2)

    def inputs(self):
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
    if not all([True] + map(lambda item: issubclass(item, Model), value)):
        raise WrongAttributeTypeError(
            'Actor {} attribute {} should contain only Models'.format(actor, name))


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
        _get_attribute(actor, 'name', _is_type((str, unicode)), required=True),
        _get_attribute(actor, 'tags', _is_tuple_of((str, unicode)), required=True),
        _get_attribute(actor, 'consumes', _is_model_tuple, required=False),
        _get_attribute(actor, 'produces', _is_model_tuple, required=False),
        _get_attribute(actor, 'description', _is_type((str, unicode)), required=False,
                       default_value='There has been no description provided for this actor')
    ])


def get_actors():
    actors = get_flattened_subclasses(Actor)
    for actor in actors:
        get_actor_metadata(actor)
    return actors
