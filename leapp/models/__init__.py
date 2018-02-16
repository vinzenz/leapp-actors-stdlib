from marshmallow import Schema
from . import fields

from leapp.utils.meta import get_flattened_subclasses

__all__ = ('fields', 'Schema')


class Model(Schema):
    pass


class ErrorModel(Model):
    message = fields.String()
    actor = fields.String()
    time = fields.DateTime()


def get_models():
    return get_flattened_subclasses(Model)
