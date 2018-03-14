class DefinitionKind(object):
    class _Kind(object):
        def __init__(self, kind):
            self.name = kind

    ACTOR = _Kind('actor')
    MODEL = _Kind('model')
    CHANNEL = _Kind('channel')
    TAG = _Kind('tag')
    WORKFLOW = _Kind('workflow')
    LIBRARIES = _Kind('libraries')
    TOOLS = _Kind('tools')
    FILES = _Kind('files')
    TESTS = _Kind('tests')

    REPO_WHITELIST = (ACTOR, MODEL, CHANNEL, TAG, WORKFLOW, TOOLS, LIBRARIES, FILES)
    ACTOR_WHITELIST = (TOOLS, LIBRARIES, FILES, TESTS)
