import itertools


def with_metaclass(meta_class, base_class=object):
    return meta_class(
        'with_meta_base_' + base_class.__name__ + '_' + meta_class.__name__,
        (base_class,),
        {}
    )


def get_flattened_subclasses(cls):
    classes = cls.__subclasses__()
    return list(itertools.chain(classes, *map(lambda x: get_flattened_subclasses(x), classes)))


