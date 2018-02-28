import itertools

from workflows import TagFilter


class Filter(object):
    def __init__(self, *args):
        self.filters = args

    def _get_with(self, fun):
        return tuple(itertools.chain(*(fun(f) for f in self.filters)))

    def get_pre(self):
        return self._get_with(TagFilter.get_pre)

    def get_post(self):
        return self._get_with(TagFilter.get_post)

    def get(self):
        return self._get_with(TagFilter.get)