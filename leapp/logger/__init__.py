import json
import logging
import os
import sys

import requests
import requests.exceptions

_logger = None


class LeappAuditFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(record.__dict__)


class LeappAuditHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super(LeappAuditHandler, self).__init__(*args, **kwargs)
        self.setFormatter(LeappAuditFormatter())
        base_url = os.environ.get('LEAPP_ACTOR_API', 'http://localhost:9999/')
        self.url = os.path.join(base_url, 'audit/log/record')
        self.session = requests.session()

    def emit(self, record):
        try:
            self.session.post(self.url, data=self.format(record), timeout=0.1)
        except requests.exceptions.RequestException:
            pass


def configure_logger():
    global _logger
    if not _logger:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(name)-24s %(levelname)-8s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S.%f',
            stream=sys.stderr,
        )

        logging.getLogger('urllib3').setLevel(logging.WARN)
        handler = LeappAuditHandler()
        logging.getLogger('').addHandler(handler)

        logging.info('Logging has been initialized')
        _logger = logging.getLogger('')

    return _logger
