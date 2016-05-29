from __future__ import unicode_literals, division, absolute_import
from builtins import *  # pylint: disable=unused-import, redefined-builtin

import logging
import os
import shutil

from flexget import plugin
from flexget.event import event

log = logging.getLogger('best_quality')


class Delete(object):
    """
    Deletes

    Example::

      best_quality: trakt_episode_id
    """

    schema = {
        'type': 'object',
        'properties': {
            'type': {'type': 'string', 'enum': ['dirs', 'files']},
            'on_status': {'type': 'string', 'enum': ['rejected', 'accepted', 'undecided'], 'default': 'accepted'}
        },
        'required': ['type'],
        'additionalProperties': False
    }

    def on_task_exit(self, task, config):
        if config['on_status'] == 'accepted':
            entries = task.accepted
        elif config['on_status'] == 'rejected':
            entries = task.rejected
        else:
            entries = task.undecided

        for entry in entries:
            if 'location' not in entry:
                entry.reject('Not a local file. Skipping')
                continue
            if config['type'] == 'dirs' and os.path.isdir(entry['location']):
                if task.options.test:
                    log.info('Would delete %s', entry['location'])
                    continue
                log.info('Deleting %s', entry['location'])
                try:
                    shutil.rmtree(entry['location'])
                except OSError as e:
                    log.error(e)
                    entry.fail()
            elif config['type'] == 'files' and os.path.isfile(entry['location']):
                if task.options.test:
                    log.info('Would delete %s', entry['location'])
                    continue
                log.info('Deleting %s', entry['location'])
                try:
                    os.remove(entry['location'])
                except OSError as e:
                    log.error(e)
                    entry.fail()
            else:
                log.debug('Entry %s file type does not match %s', entry, config['type'])


@event('plugin.register')
def register_plugin():
    plugin.register(Delete, 'delete', api_ver=2)
