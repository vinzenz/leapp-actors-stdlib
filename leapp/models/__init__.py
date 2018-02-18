from marshmallow import Schema
from marshmallow.fields import Field
from marshmallow.utils import missing
from . import fields

from leapp.exceptions import ModelDefinitionError
from leapp.utils.meta import get_flattened_subclasses
from leapp.channels import Channel, ErrorChannel


class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        klass = super(ModelMeta, mcs).__new__(mcs, name, bases, attrs)

        # Every model has to be bound to a channel
        if klass.__name__ != 'Model' and issubclass(klass, Model):
            channel = getattr(klass, 'channel', None)
            if not channel or not issubclass(channel, Channel):
                raise ModelDefinitionError('Missing channel in Model {}'.format(name))

        # This allows to declare a custom schema or use the generated one from the Model based on marshmallow fields
        if '__schema__' not in klass.__dict__.keys():
            kls_attrs = {name: value for name, value in attrs.items() if isinstance(value, Field)}
            klass.fields = kls_attrs.copy()
            kls_attrs['__model__'] = klass
            setattr(klass, '__schema__', type(klass.__name__ + 'Schema', (Schema,), kls_attrs))

        return klass

    def __init__(cls, name, bases, attrs):
        super(ModelMeta, cls).__init__(name, bases, attrs)


class Model(object):
    __metaclass__ = ModelMeta
    __schema__ = None

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__()
        for field in self.__class__.fields.keys():
            # Default value support from Marshmallow uses 'missing' if it is not set
            value = kwargs.get(field, self.__class__.fields[field].default)
            if value is missing:
                value = None
            setattr(self, field, value)

    def dump(self):
        return self.__schema__().dump(self).data


class ErrorModel(Model):
    channel = ErrorChannel

    message = fields.String(required=True)
    actor = fields.String(required=True)
    time = fields.DateTime(required=True)


def get_models():
    return get_flattened_subclasses(Model)
