import sys

import itertools

from leapp.exceptions import TagFilterUsageError
from leapp.tags import Tag
from leapp.utils.meta import with_metaclass


def phase_sorter_key(a):
    return a.get_index()


class WorkflowMeta(type):

    def __new__(mcs, name, bases, attrs):
        klass = super(WorkflowMeta, mcs).__new__(mcs, name, bases, attrs)
        if not getattr(sys.modules[mcs.__module__], name, None):
            setattr(sys.modules[mcs.__module__], name, klass)
        phases = [attr for attr in attrs.values() if isinstance(attr, type) and issubclass(attr, Phase)]
        klass.phases = tuple(sorted(phases, key=phase_sorter_key))
        return klass


class PhaseMeta(type):
    classes = []

    def __new__(mcs, name, bases, attrs):
        klass = super(PhaseMeta, mcs).__new__(mcs, name, bases, attrs)
        PhaseMeta.classes.append(klass)
        return klass


class Phase(with_metaclass(PhaseMeta)):
    @classmethod
    def get_index(cls):
        return PhaseMeta.classes.index(cls)


class Workflow(with_metaclass(WorkflowMeta)):
    pass


class Filter(object):
    def __init__(self, *args):
        self.filters = args

    def get_pre(self):
        return tuple(itertools.chain(*(f.get_pre() for f in self.filters)))

    def get_post(self):
        return tuple(itertools.chain(*(f.get_post() for f in self.filters)))

    def get(self):
        return tuple(itertools.chain(*(f.get() for f in self.filters)))


class TagFilter(object):
    def __init__(self, *tags, **kwargs):
        self.phase = kwargs.get('phase')
        self.tags = tags
        if not self.phase or not isinstance(self.phase, type) or not issubclass(self.phase, Tag):
            raise TagFilterUsageError("TagFilter phase key needs to be set to a tag.")

    def get_pre(self):
        result = set((actor.name for actor in self.phase.Pre.actors))
        [result.intersection_update(actor.name for actor in tag.actors) for tag in self.tags]
        return tuple(result)

    def get_post(self):
        result = set(self.phase.Post.actors)
        [result.intersection_update(tag.actors) for tag in self.tags]
        return tuple(result)

    def get(self):
        result = set(self.phase.actors)
        [result.intersection_update(tag.actors) for tag in self.tags]
        return tuple(result)


class Flags(object):
    def __init__(self, *args, **kwargs):
        pass


class Policies(object):
    class Errors(object):
        class FailPhase(object):
            pass

        class FailImmediately(object):
            pass

        class ReportOnly(object):
            pass

    class Retry(object):
        class Actor(object):
            pass

        class Phase(object):
            pass

        class Disabled(object):
            pass

    def __init__(self, error=Errors.ReportOnly, retry=Retry.Disabled):
        self.error = error
        self.retry = retry
