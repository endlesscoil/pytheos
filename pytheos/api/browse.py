#!/usr/bin/env python
from __future__ import annotations

from collections import OrderedDict
from typing import Optional
import logging

from .. import models

logger = logging.getLogger(__name__)


class BrowseAPI:
    MAX_QUERY_RESULTS = 50
    MAX_SEARCH_LENGTH = 128

    def __init__(self, conn):
        self._api = conn

    async def add_to_queue(self, player_id: str, source_id: str, container_id: str, media_id: Optional[str]=None,
                           add_type: models.browse.AddToQueueType=models.browse.AddToQueueType.PlayNow):
        """ Adds the specified container or track to the playback queue.  If media_id is provided it will add the track
        specified by that ID, otherwise it will add the container specified by container_id.

        :param player_id: Player ID
        :param source_id: Source ID
        :param container_id: Container ID
        :param media_id: Media ID
        :param add_type: Type of add to perform
        :return: None
        """
        kwargs = {}
        if media_id is not None:
            kwargs['mid'] = media_id

        await self._api.call('browse', 'add_to_queue', pid=player_id, sid=source_id, cid=container_id, aid=add_type, **kwargs)

    async def browse_source(self,
                            source_id: int,
                            options: Optional[int]=None,
                            create_criteria: Optional[int]=None,
                            item_range: Optional[tuple]=None) -> list:
        """ Browses a music source and retrieves a list of the media it contains

        :param source_id: Source ID
        :param options: Optional features
        :param create_criteria: Options for creating new stations
        :param item_range: Tuple specifying the start and end range to query
        :return: list of SourceMedia
        """
        kwargs = {}
        if source_id is not None:
            kwargs['sid'] = source_id

        if create_criteria is not None:
            kwargs['scid'] = create_criteria

        if options is not None:
            kwargs['id'] = options  # NOTE: This is correct.. the options are called 'id' in the spec for some reason.

        if item_range is not None:
            kwargs['item_range'] = ','.join(item_range)

        # FIXME: This needs a whole bunch of work.  There are three different formats to this command.
        results = await self._api.call('browse', 'browse', **kwargs)
        return [models.Source(media, parent_source_id=source_id) for media in results.payload.data]

    async def browse_source_container(self,
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
            total_count, res = await self._get_source_container_results(source_id, container_id, item_range)
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

    async def delete_playlist(self, source_id: int, container_id: int):
        """ Deletes a playlist container.

        :param source_id: Source ID
        :param container_id: Container ID
        :return: None
        """
        await self._api.call('browse', 'delete_playlist', sid=source_id, cid=container_id)

    # FIXME: Can this just be replaced with browse.browse above?
    async def _get_source_container_results(self, source_id: int, container_id: str, item_range: tuple) -> tuple:
        kwargs = {}

        if source_id is not None:
            kwargs['sid'] = source_id

        if container_id is not None:
            kwargs['cid'] = container_id

        if item_range is not None:
            kwargs['range'] = ','.join([str(itm) for itm in item_range])

        results = await self._api.call('browse', 'browse', **kwargs)
        return int(results.header.vars.get('count', 0)), [models.Source(media, parent_source_id=source_id, parent_container_id=container_id) for media in results.payload]

    async def get_music_sources(self) -> list:
        """ Retrieve a list of music sources.

        :return: list
        """
        results = await self._api.call('browse', 'get_music_sources')
        return [models.Source(source) for source in results.payload]

    async def get_search_criteria(self, source_id: int) -> list:
        """ Retrieves the search criteria settings for the specified music source.

        :param source_id: Source ID
        :return: list of SearchCriteria
        """
        results = await self._api.call('browse', 'get_search_criteria', sid=source_id)

        return [models.browse.SearchCriteria(item) for item in results.payload]

    async def get_source_info(self, source_id: int) -> Optional[models.Source]:
        """ Retrieve information on the specified Source ID

        :param source_id: Source ID
        :return: MusicSource or None if not found
        """
        results = await self._api.call('browse', 'get_source_info', sid=source_id)

        return models.Source(results.payload.data)

    async def play_station(self, player_id: int, source_id: int, container_id: str, media_id: str, name: str):
        """ Starts playing the specified music station.  Media ID must be from media of the 'station' type.

        :param player_id: Player ID
        :param source_id: Source ID
        :param container_id: Container ID
        :param media_id: Media ID
        :param name: Station name returned by browse
        :return: None
        """
        await self._api.call('browse', 'play_stream', pid=player_id, sid=source_id, cid=container_id, mid=media_id, name=name)

    async def play_preset(self, player_id: int, preset: int):
        """ Plays one of the configured presets/favorites.

        :param player_id: Player ID
        :param preset: Preset number
        :return: None
        """
        if preset <= 0:
            raise ValueError('Preset must be greater than zero.')

        await self._api.call('browse', 'play_preset', pid=player_id, preset=preset)

    async def play_input(self, player_id: int, input_name: str, source_player_id: Optional[int]=None):
        """ Plays the specified input source on the provided Player ID.  Other speakers can be targeted if the optional
        Source Player ID is provided.

        :param player_id: Player ID
        :param input_name: Input name
        :param source_player_id: Source Player ID
        :return: None
        """
        kwargs = {}
        if source_player_id is not None:
            kwargs['spid'] = source_player_id

        await self._api.call('browse', 'play_input', pid=player_id, input=input_name, **kwargs)

    async def play_url(self, player_id: str, url: str):
        """ Play the specified URL

        :param player_id: Player ID
        :param url: URL string
        :return: None
        """
        kwargs = OrderedDict()
        kwargs['pid'] = player_id
        kwargs['url'] = url         # 'url' must be the last parameter in this command.

        await self._api.call('browse', 'play_stream', **kwargs)

    async def rename_playlist(self, source_id: int, container_id: int, name: str):
        """ Renames a playlist container.

        :param source_id: Source ID
        :param container_id: Container ID
        :param name: New playlist name
        :return: None
        """
        await self._api.call('browse', 'rename_playlist', sid=source_id, cid=container_id, name=name)

    async def retrieve_metadata(self, source_id: int, container_id: int) -> list:
        """ Retrieves image data for a specific container.  This only applies to Rhapsody and Napster.

        :param source_id: Source ID
        :param container_id: Container ID
        :return: AlbumMetadata
        """
        results = await self._api.call('browse', 'retrieve_metadata', sid=source_id, cid=container_id)

        return [models.browse.AlbumMetadata(itm) for itm in results.payload]

    async def search(self, source_id: int, query: str, search_criteria_id: int) -> list:
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
            total_count, res = await self._get_search_results(source_id, query, search_criteria_id, item_range)
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

    async def _get_search_results(self, source_id: int, query: str, search_criteria_id: int, item_range: tuple) -> tuple:
        """ Retrieves the results for a given range in a search request

        :param source_id:
        :param query:
        :param search_criteria_id:
        :param item_range:
        :return:
        """
        kwargs = {}

        if item_range is not None:
            kwargs['range'] = ','.join([str(itm) for itm in item_range])

        results = await self._api.call('browse', 'search', sid=source_id, search=query, scid=search_criteria_id, **kwargs)
        return int(results.header.vars.get('count', 0)), [models.Source(media) for media in results.payload]

    async def set_service_option(self, source_id: int, option: models.browse.ServiceOption, **kwargs) -> models.heos.HEOSResult:
        """ Sets a service option.

        :param source_id: Source ID
        :param option: Option to set
        :param kwargs: Optional parameters used by individual service options
        :return: HEOSResult
        """
        return await self._api.call('browse', 'set_service_option', sid=source_id, option=option, **kwargs)
