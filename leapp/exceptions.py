class LeappError(Exception):
    def __init__(self, message):
        super(LeappError, self).__init__(message)


class InvalidChannelItemError(LeappError):
    def __init__(self, message):
        super(InvalidChannelItemError, self).__init__(message)


class InvalidChannelDefinitionError(LeappError):
    def __init__(self, message):
        super(InvalidChannelDefinitionError, self).__init__(message)


class InvalidTagDefinitionError(LeappError):
    def __init__(self, message):
        super(InvalidTagDefinitionError, self).__init__(message)


class MissingActorAttributeError(LeappError):
    def __init__(self, message):
        super(MissingActorAttributeError, self).__init__(message)


class WrongAttributeTypeError(LeappError):
    def __init__(self, message):
        super(WrongAttributeTypeError, self).__init__(message)


class ModelDefinitionError(LeappError):
    def __init__(self, message):
        super(ModelDefinitionError, self).__init__(message)


class TagFilterUsageError(LeappError):
    def __init__(self, message):
        super(TagFilterUsageError, self).__init__(message)
