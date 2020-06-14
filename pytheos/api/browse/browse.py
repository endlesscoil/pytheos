#!/usr/bin/env python
from typing import Optional
import logging

from pytheos.api.api import API
from pytheos.api.browse.types import MusicSource, SourceMedia, SearchCriteria

logger = logging.getLogger(__name__)


class BrowseAPI(API):
    def get_music_sources(self) -> list:
        """ Retrieve a list of music sources.

        :return: list
        """
        results = self._pytheos.api.call('browse', 'get_music_sources')
        return [MusicSource(source) for source in results.payload]

    def get_source_info(self, source_id: int) -> Optional[MusicSource]:
        """ Retrieve information on the specified Source ID

        :param source_id: Source ID
        :return: MusicSource or None if not found
        """
        results = self._pytheos.api.call('browse', 'get_source_info', sid=source_id)
        if results.header.result == 'success':
            return MusicSource(results.payload.data)

        return None

    def browse_source(self,
                      source_id: int,
                      options: Optional[int]=None,
                      scid: Optional[int]=None,
                      item_range: Optional[tuple]=None) -> list:
        """ Browses a music source and retrieves a list of the media it contains

        :param source_id: Source ID
        :param options: Optional features
        :param scid: Options for creating new stations # FIXME - rename this.
        :param item_range: Tuple specifying the start and end range to query
        :return: list of SourceMedia
        """
        kwargs = {}
        if item_range is not None:
            kwargs['item_range'] = ','.join(item_range)

        # FIXME: This needs a whole bunch of work.  There are three different formats to this command.
        results = self._pytheos.api.call('browse', 'browse', sid=source_id, id=options, scid=scid, **kwargs)
        return [SourceMedia(media) for media in results.payload.data]

    def browse_source_container(self,
                                source_id: Optional[int]=None,
                                container_id: Optional[str]=None,
                                item_range: Optional[tuple]=None) -> list:
        """ Browses the specified Container on the specified Source.

        :param source_id: Source ID
        :param container_id: Container ID
        :param item_range: Tuple specifying the start and end range to query
        :return: list of SourceMedia
        """
        results = []

        while True:
            total_count, res = self._get_source_container_results(source_id, container_id, item_range)
            results.extend(res)

            # FIXME: Add logging stuff
            # Unknown container size - reached the end
            if total_count == 0 and len(res.payload) == 0:
                logger.debug(f'Reached end (unknown size)')
                break

            current_count = len(results)
            # Known container size - reached the end
            if current_count >= total_count:
                logger.debug(f'Reached end (known size)')
                break
            #/FIXME

            item_range = current_count, current_count + 50 # FIXME

        return results

    # FIXME: Can this just be replaced with browse.browse above?
    def _get_source_container_results(self, source_id: int, container_id: str, item_range: tuple) -> tuple:
        kwargs = {}

        if source_id is not None:
            kwargs['sid'] = source_id

        if container_id is not None:
            kwargs['cid'] = container_id

        if item_range is not None:
            kwargs['range'] = ','.join([str(itm) for itm in item_range])

        results = self._pytheos.api.call('browse', 'browse', **kwargs)
        return int(results.header.vars.get('count', 0)), [SourceMedia(media) for media in results.payload]

    def get_search_criteria(self, source_id: int) -> list:
        """ Retrieves the search criteria settings for the specified music source.

        :param source_id: Source ID
        :return: list of SearchCriteria
        """
        results = self._pytheos.api.call('browse', 'get_search_criteria', sid=source_id)

        return [SearchCriteria(item) for item in results.payload]
