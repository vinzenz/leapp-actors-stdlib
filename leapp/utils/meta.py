import itertools


def get_flattened_subclasses(cls):
    classes = cls.__subclasses__()
    return list(itertools.chain(classes, *map(lambda x: get_flattened_subclasses(x), classes)))


