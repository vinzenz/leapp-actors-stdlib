from leapp.exceptions import InvalidChannelItemError, InvalidChannelDefinitionError
from leapp.models import Model, ErrorModel
from leapp.utils.meta import get_flattened_subclasses


class Channel(object):
    pass


class OutputOnlyChannel(Channel):
    pass


class ErrorChannel(OutputOnlyChannel):
    name = 'errors'
    messages = (ErrorModel,)


def get_channels():
    channels = get_flattened_subclasses(Channel)
    for channel in channels:
        channel_name = getattr(channel, 'name', None)
        if not channel_name:
            raise InvalidChannelDefinitionError('Channel {} does not contain a channel name attribute'.format(channel))
        channel_messages = getattr(channel, 'messages', None)
        if not channel_messages:
            raise InvalidChannelDefinitionError('Channel {} must have at least one message model'.format(channel))
        models = get_flattened_subclasses(Model)
        for message in channel_messages:
            if message not in models:
                raise InvalidChannelItemError('Message {} on channel {} is not a valid Model'.format(message, channel))
    return channels
