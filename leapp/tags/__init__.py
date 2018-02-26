import sys

from leapp.exceptions import InvalidTagDefinitionError
from leapp.utils.meta import get_flattened_subclasses, with_metaclass


class TagMeta(type):
    def __new__(mcs, name, bases, attrs):
        klass = super(TagMeta, mcs).__new__(mcs, name, bases, attrs)
        if klass.__module__ is not TagMeta.__module__:
            setattr(sys.modules[mcs.__module__], name, klass)
            setattr(klass, 'actors', ())
            if not getattr(klass, 'parent', None):
                setattr(klass, 'Pre', type('Pre' + name, (Tag,), {'name': 'pre-' + klass.name, 'parent': klass, 'actors': ()}))
                setattr(klass, 'Post', type('Post' + name, (Tag,), {'name': 'post-' + klass.name, 'parent': klass, 'actors': ()}))
        return klass


class Tag(with_metaclass(TagMeta)):
    pass


def get_tags():
    tags = get_flattened_subclasses(Tag)
    for tag in (tag for tag in tags if tag is not Tag):
        tag_name = getattr(tag, 'name', None)
        if not tag_name:
            raise InvalidTagDefinitionError('Tag {} does not contain a tag name attribute'.format(tag))
    return tags
