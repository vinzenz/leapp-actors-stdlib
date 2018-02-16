import itertools


def get_flattened_subclasses(cls):
    classes = cls.__subclasses__()
    return itertools.chain(classes, *map(lambda x: get_flattened_subclasses(x), classes))


