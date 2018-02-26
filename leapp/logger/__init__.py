import json
import logging
import sys

_logger = None


class LeappAuditFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(record)


class LeappAuditHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super(LeappAuditHandler, self).__init__(*args, **kwargs)
        self.setFormatter(LeappAuditFormatter())

    def emit(self, record):
        self.format(record)


def configure_logger():
    global _logger
    if not _logger:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(name)-24s %(levelname)-8s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S.%f',
            stream=sys.stderr,
        )

        logging.getLogger('').addHandler(logging.LeappAuditHandler())

        logging.info('Logging has been initialized')
        _logger = logging.getLogger('')

    return _logger
