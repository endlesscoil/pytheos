#!/usr/bin/env python
from typing import Optional
import logging

from pytheos.api.api import API
from pytheos.api.browse.types import MusicSource, SourceMedia, SearchCriteria

logger = logging.getLogger(__name__)


class BrowseAPI(API):
    MAX_QUERY_RESULTS = 50
    MAX_SEARCH_LENGTH = 128


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

            # Unknown container size - reached the end
            if total_count == 0 and len(res.payload) == 0:
                break

            current_count = len(results)
            # Known container size - reached the end
            if current_count >= total_count:
                break

            item_range = current_count, current_count + self.MAX_QUERY_RESULTS

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

    def search(self, source_id: int, query: str, search_criteria_id: int) -> list:
        """ Search the source for a given string using the specified search criteria ID.

        FIXME: Can't get this working with my current setup - keep getting a -10 system error when searching Plex.

        :param source_id: Source ID
        :param query: String to search for.  May include wildcards if the search criteria does.
        :param search_criteria_id: Search Criteria ID
        :return: list of SourceMedia
        """
        if len(query) > self.MAX_SEARCH_LENGTH:
            raise ValueError(f"Query must be no longer than {self.MAX_SEARCH_LENGTH} characters.")

        results = []
        item_range = None

        while True:
            total_count, res = self._get_search_results(source_id, query, search_criteria_id, item_range)
            results.extend(res)

            # Unknown container size - reached the end
            if total_count == 0 and len(res.payload) == 0:
                break

            current_count = len(results)
            # Known container size - reached the end
            if current_count >= total_count:
                break

            item_range = current_count, current_count + self.MAX_QUERY_RESULTS

        return results

    def _get_search_results(self, source_id: int, query: str, search_criteria_id: int, item_range: tuple) -> tuple:
        kwargs = {}

        if item_range is not None:
            kwargs['range'] = ','.join([str(itm) for itm in item_range])

        results = self._pytheos.api.call('browse', 'search', sid=source_id, search=query, scid=search_criteria_id, **kwargs)
        return int(results.header.vars.get('count', 0)), [SourceMedia(media) for media in results.payload]

    def play_station(self, player_id: int, source_id: int, container_id: str, media_id: str, name: str):
        """ Starts playing the specified music station.  Media ID must be from media of the 'station' type.

        :param player_id: Player ID
        :param source_id: Source ID
        :param container_id: Container ID
        :param media_id: Media ID
        :param name: Station name returned by browse
        :return: None
        """
        self._pytheos.api.call('browse', 'play_stream',
                               pid=player_id, sid=source_id,
                               cid=container_id, mid=media_id,
                               name=name)
