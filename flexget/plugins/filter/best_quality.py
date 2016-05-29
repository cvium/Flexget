from __future__ import unicode_literals, division, absolute_import
from builtins import *  # pylint: disable=unused-import, redefined-builtin

import logging

from flexget import plugin
from flexget.event import event

log = logging.getLogger('best_quality')


class FilterBestQuality(object):
    """
    Accepts the best quality of an entry. Rejects the other qualities should they exist.

    Example::

      best_quality: trakt_episode_id
    """

    schema = {
        'type': 'string'
    }

    def on_task_filter(self, task, config):
        best_entries = {}
        field = config
        for entry in task.entries:
            if not entry.get(field):
                entry.fail('Field {} not present in entry {}'.format(field, entry))
                continue
            if entry[field] in best_entries:
                if entry['quality'] > best_entries[entry[field]]['quality']:
                    best_entries[entry[field]].reject('Better quality found')
                    best_entries[entry[field]] = entry
                else:
                    entry.reject('Better quality already found')
            else:
                best_entries[entry[field]] = entry

        for entry in best_entries.values():
            entry.accept('Best quality found')


@event('plugin.register')
def register_plugin():
    plugin.register(FilterBestQuality, 'best_quality', api_ver=2)
