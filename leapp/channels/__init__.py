from leapp.exceptions import InvalidChannelDefinitionError
from leapp.utils.meta import get_flattened_subclasses


class Channel(object):
    pass


class OutputOnlyChannel(Channel):
    pass


class ErrorChannel(OutputOnlyChannel):
    name = 'errors'


def get_channels():
    channels = get_flattened_subclasses(Channel)
    for channel in (channel for channel in channels if channel not in (ErrorChannel, OutputOnlyChannel)):
        channel_name = getattr(channel, 'name', None)
        if not channel_name:
            raise InvalidChannelDefinitionError('Channel {} does not contain a channel name attribute'.format(channel))

        channel_messages = getattr(channel, 'messages', None)
        if not channel_messages:
            setattr(channel, 'messages', ())

    return channels
