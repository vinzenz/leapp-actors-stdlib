import datetime
import six


def missing(): pass


class ModelViolationError(Exception):
    """
    ModelViolationError is raised if there if the data in the instances is not matching the definition
    """
    def __init__(self, message):
        super(ModelViolationError, self).__init__(message)


class ModelMisuseError(Exception):
    """
    ModelMisuseError is raised is a Model definition is illegal
    """
    def __init__(self, message):
        super(ModelMisuseError, self).__init__(message)


class Field(object):
    """
    Field is the base of all supported fields
    """
    def __init__(self, default=missing, required=False, allow_null=False):
        """
        :param default: Default value to use if the field is not set
        :param required: Marks the field as mandatory
        :param allow_null: Whether or not the field is allowed to be None
        """
        self._default = default
        self._required = required
        self._allow_null = allow_null

        if type(self) == Field:
            raise ModelMisuseError("Do not use this type directly")

    def validate_model_value(self, value, name):
        """
        Validates the value in the Model representation

        :param value: Value to check
        :param name: Name of the field (used for better error reporting only)
        :return: None
        """
        if value is None and not self._allow_null:
            raise ModelViolationError('Attribute {name} is None but it is not allowed'.format(name=name))
        if value is missing and self._required:
            raise ModelViolationError('Attribute {name} is not set but it is required'.format(name=name))

    def validate_builtin_value(self, value, name):
        """
        Validates the value in the builtin representation

        :param value: Value to check
        :param name: Name of the field (used for better error reporting only)
        :return: None
        """
        if value is None and not self._allow_null:
            raise ModelViolationError('Field {name} is null but it is not allowed'.format(name=name))

    def convert_to_model(self, value, name):
        """
        Performs the conversion from a builtin type to the model representation

        :param value: Value to convert
        :param name: Name of the field (used for better error reporting only)
        :return: Converted value in the model format
        """
        self.validate_builtin_value(value=value, name=name)
        return value

    def convert_from_model(self, value, name):
        """
        Performs the conversion from a model type to the builtin representation

        :param value: Value to convert
        :param name: Name of the field (used for better error reporting only)
        :return: Converted value in the builtin format
        """
        self.validate_model_value(value=value, name=name)
        return value

    def from_initialization(self, source, name, target):
        """
        Assigns the value to the target model passed through during the model initialization

        :param source: Dictionary to extract the value from (usually kwargs)
        :type source: dict
        :param name: Name of the field (used for better error reporting only)
        :type name: str
        :param target: Target model instance
        :type target: Instance of a Model derived class
        :return: None
        """
        source_value = source.get(name, self._default)
        self.validate_model_value(value=source_value, name=name)
        setattr(target, name, source_value)

    def to_model(self, source, name, target):
        """
        Converts the value with the given name to the model representation and assigns the attribute

        :param source: Dictionary to extract the value from
        :type source: dict
        :param name: Name of the field (used for better error reporting only)
        :type name: str
        :param target: Target model instance
        :type target: Instance of a Model derived class
        :return: None
        """
        source_value = source.get(name, self._default)
        target_value = self.convert_to_model(value=source_value, name=name)
        setattr(target, name, target_value)

    def to_builtin(self, source, name, target):
        """
        Converts the value with the given name to the builtin representation and assigns the field

        :param source: Source model to get the value from
        :type source: Instance of a Model derived class
        :param name: Name of the field (used for better error reporting only)
        :type name: str
        :param target: Dictionary to set the value to
        :type target: dict
        :return: None
        """
        target[name] = self.convert_from_model(getattr(source, name, None), name=name)


class BuiltinField(Field):
    """
    Base class for all builtin types to act as pass-through with additional validation
    """
    def __init__(self, model_type, builtin_type=missing, **kwargs):
        """
        :param model_type: Type to use as model value type
        :param builtin_type: Builtin type for conversion to the builtin representation. By default same as model_type
        :param kwargs: Pass through keyword arguments to the Field initializer
        """
        super(BuiltinField, self).__init__(**kwargs)
        self._model_type = model_type
        self._builtin_type = builtin_type if builtin_type is not missing else model_type

    def validate_model_value(self, value, name):
        super(BuiltinField, self).validate_model_value(value, name)
        self._validate(value=value, name=name, expected_type=self._model_type)

    def validate_builtin_value(self, value, name):
        super(BuiltinField, self).validate_builtin_value(value, name)
        self._validate(value=value, name=name, expected_type=self._builtin_type)

    @staticmethod
    def _validate(value, name, expected_type):
        if not isinstance(expected_type, tuple):
            expected_type = (expected_type,)
        if value is not None and not any(isinstance(value, t) for t in expected_type):
            names = ', '.join(['{}'.format(t.__name__) for t in expected_type])
            raise ModelViolationError("Fields {} is of type: {} expected: {}".format(name, type(value).__name__,
                                                                                     names))


class Boolean(BuiltinField):
    """
    Boolean field
    """
    def __init__(self, **kwargs):
        super(Boolean, self).__init__(bool, **kwargs)


class Float(BuiltinField):
    """
    Float field
    """
    def __init__(self, **kwargs):
        super(Float, self).__init__(float, **kwargs)


class Integer(BuiltinField):
    """
    Integer field (int, long in python 2, int in python 3)
    """
    def __init__(self, **kwargs):
        super(Integer, self).__init__(six.integer_types, **kwargs)


class Number(BuiltinField):
    """
    Combined Integer and Float field
    """
    def __init__(self, **kwargs):
        super(Number, self).__init__(six.integer_types + (float,), **kwargs)


class List(Field):
    """
        List represents lists of `elem_field` values
    """
    def __init__(self, elem_field, minimum=None, maximum=None, **kwargs):
        """
        :param elem_field:
        :type elem: Instance of :py:class:`Field`
        :param minimum:
        :type minimum: Minimal number of elements
        :param maximum:
        :type maximum: Maximum number of elements
        :param kwargs:
        """
        if kwargs.get('required', False) and kwargs.get('default', missing) is missing:
            kwargs['default'] = []
        super(List, self).__init__(**kwargs)
        if not isinstance(elem_field, Field):
            raise ModelMisuseError("elem_field must be a instance of a type derived from Field")
        self._elem_type = elem_field
        self._minimum = minimum or 0
        self._maximum = maximum

    def _validate_count(self, value, name):
        message = 'Element count error for field {name} expected between {minimum} and {maximum} elements got {count}'
        count = len(value)
        if not (self._minimum <= count <= (self._maximum or count)):
            raise ModelViolationError(
                message.format(name=name, minimum=self._minimum, maximum=self._maximum or count, count=count))

    def validate_model_value(self, value, name):
        super(List, self).validate_model_value(value, name)
        if isinstance(value, (list, tuple)):
            self._validate_count(value, name)
            for idx, entry in enumerate(value):
                self._elem_type.validate_model_value(entry, name='{}[{}]'.format(name, idx))
        elif value and value is not missing:
            raise ModelViolationError('Expected list but got {} for field {}'.format(type(value).__name__, name))

    def validate_builtin_value(self, value, name):
        super(List, self).validate_builtin_value(value, name)
        if isinstance(value, (list, tuple)):
            self._validate_count(value, name)
            for idx, entry in enumerate(value):
                self._elem_type.validate_builtin_value(entry, name='{}[{}]'.format(name, idx))
        elif value is not None:
            raise ModelViolationError('Expected list but got {} for field {}'.format(type(value).__name__, name))

    def convert_to_model(self, value, name):
        self.validate_builtin_value(value=value, name=name)
        if value is None:
            return None
        converter = self._elem_type.convert_to_model
        return list(converter(entry, name='{}[{}]'.format(name, idx)) for idx, entry in enumerate(value))

    def convert_from_model(self, value, name):
        self.validate_model_value(value=value, name=name)
        if value is None:
            return None
        converter = self._elem_type.convert_from_model
        return list(converter(entry, name='{}[{}]'.format(name, idx)) for idx, entry in enumerate(value))


class String(BuiltinField):
    def __init__(self, **kwargs):
        super(String, self).__init__(six.string_types + (six.binary_type,), **kwargs)


class DateTime(BuiltinField):
    def __init__(self, **kwargs):
        super(DateTime, self).__init__(datetime.datetime, builtin_type=str, **kwargs)

    def convert_to_model(self, value, name):
        self.validate_builtin_value(value=value, name=name)

        if value is None:
            return None

        # We want Z to be appended but it needs support from our side here:
        value = value.rstrip('Z')

        # If there are fractions, use them
        fractions = ''
        if '.' in value:
            fractions = '.%f'

        # Try to parse with timezone specification, else retry without
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S{fractions}%Z'.format(fractions=fractions))
        except ValueError:
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S{fractions}'.format(fractions=fractions))
            except ValueError:
                raise ModelViolationError(
                    "Field {name} contains an invalid date time value: '{value}'".format(name=name, value=value))

    def convert_from_model(self, value, name):
        self.validate_model_value(value=value, name=name)

        if value is None:
            return None

        if not value.utcoffset():
            return value.isoformat() + 'Z'


class Nested(Field):
    def __init__(self, model_type, **kwargs):
        super(Nested, self).__init__(**kwargs)
        from leapp.models import Model
        if not isinstance(model_type, type) or not issubclass(model_type, Model):
            raise ModelMisuseError("{} must be a type derived from Field".format(model_type))
        self._model_type = model_type

    def validate_model_value(self, value, name):
        super(Nested, self).validate_model_value(value, name)
        if value and value is not missing and not isinstance(value, self._model_type):
            raise ModelViolationError('Expected an instance of {} for attribute {} but got {}'.format(
                self._model_type.__name__, name, type(value)))

    def validate_builtin_value(self, value, name):
        super(Nested, self).validate_model_value(value, name)
        if value and not isinstance(value, dict):
            raise ModelViolationError('Expected a value for field {} got {}'.format(name, type(value).__name__))

    def convert_to_model(self, value, name):
        self.validate_builtin_value(value, name)
        if value is None:
            return None
        return self._model_type(**value)

    def convert_from_model(self, value, name):
        self.validate_model_value(value, name)
        if value is None:
            return None
        return value.dump()


__all__ = ('Boolean', 'DateTime', 'Float', 'Integer', 'List', 'Nested', 'Number', 'String')
