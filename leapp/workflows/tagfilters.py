from exceptions import TagFilterUsageError
from tags import Tag


class TagFilter(object):
    def __init__(self, *tags, **kwargs):
        self.phase = kwargs.get('phase')
        self.tags = tags
        if not self.phase or not isinstance(self.phase, type) or not issubclass(self.phase, Tag):
            raise TagFilterUsageError("TagFilter phase key needs to be set to a tag.")

    def get_pre(self):
        result = set(self.phase.Pre.actors)
        [result.intersection_update(tag.actors) for tag in self.tags]
        return tuple(result)

    def get_post(self):
        result = set(self.phase.Post.actors)
        [result.intersection_update(tag.actors) for tag in self.tags]
        return tuple(result)

    def get(self):
        result = set(self.phase.actors)
        [result.intersection_update(tag.actors) for tag in self.tags]
        return tuple(result)