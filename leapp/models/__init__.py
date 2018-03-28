import sys

from . import fields

from leapp.exceptions import ModelDefinitionError
from leapp.utils.meta import get_flattened_subclasses, with_metaclass
from leapp.topics import Topic, ErrorTopic


class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        klass = super(ModelMeta, mcs).__new__(mcs, name, bases, attrs)

        # Every model has to be bound to a topic
        if klass.__name__ != 'Model' and issubclass(klass, ModelMeta):
            topic = getattr(klass, 'topic', None)
            if not topic or not issubclass(topic, Topic):
                raise ModelDefinitionError('Missing topic in Model {}'.format(name))
            topic.messages = tuple(set(topic.messages + (klass,)))

        kls_attrs = {name: value for name, value in attrs.items() if isinstance(value, fields.Field)}
        klass.fields = kls_attrs.copy()

        setattr(sys.modules[mcs.__module__], name, klass)
        return klass

    def __init__(cls, name, bases, attrs):
        super(ModelMeta, cls).__init__(name, bases, attrs)


class Model(with_metaclass(ModelMeta)):
    def __init__(self, *args, **kwargs):
        init_method = kwargs.pop('init_method', 'from_initialization')
        super(Model, self).__init__()
        for field in type(self).fields.keys():
            getattr(type(self).fields[field], init_method)(kwargs, field, self)

    @classmethod
    def create(cls, data):
        return cls(init_method='to_model', **data)

    def dump(self):
        result = {}
        for field in type(self).fields.keys():
            type(self).fields[field].to_builtin(self, field, result)
        return result

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
               all(getattr(self, name) == getattr(other, name) for name in sorted(type(self).fields.keys()))


class ErrorModel(Model):
    topic = ErrorTopic

    message = fields.String(required=True)
    actor = fields.String(required=True)
    time = fields.DateTime(required=True)


def get_models():
    return get_flattened_subclasses(Model)
