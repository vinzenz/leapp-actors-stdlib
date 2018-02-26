import sys

from leapp.exceptions import InvalidChannelDefinitionError
from leapp.utils.meta import get_flattened_subclasses, with_metaclass


class ChannelMeta(type):
    def __new__(mcs, name, bases, attrs):
        klass = super(ChannelMeta, mcs).__new__(mcs, name, bases, attrs)
        setattr(sys.modules[mcs.__module__], name, klass)
        setattr(klass, 'messages', ())
        return klass


class OutputOnlyChannel(with_metaclass(ChannelMeta)):
    pass


class Channel(OutputOnlyChannel):
    pass


class ErrorChannel(OutputOnlyChannel):
    name = 'errors'


def get_channels():
    channels = get_flattened_subclasses(OutputOnlyChannel)
    for channel in (channel for channel in channels if channel is not Channel):
        channel_name = getattr(channel, 'name', None)
        if not channel_name:
            raise InvalidChannelDefinitionError('Channel {} does not contain a channel name attribute'.format(channel))
    return channels
