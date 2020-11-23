#!/usr/bin/env python
from collections.abc import Sequence

from .containers import create_media_leaf, MediaContainer
from ..models import MusicSource

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pytheos import Pytheos


class Source(Sequence):
    @property
    def id(self):
        return self._source.source_id

    @property
    def available(self):
        return self._source.available

    @property
    def name(self):
        return self._source.name

    @property
    def type(self):
        return self._source.type

    @property
    def image_url(self):
        return self._source.image_url

    @property
    def service_username(self):
        return self._source.service_username

    @property
    def nocache(self):
        return self._nocache

    @nocache.setter
    def nocache(self, value):
        self._nocache = value

    @property
    def source_id(self):
        return self.id

    @property
    def parent(self):
        return self._parent

    def __init__(self, pytheos: 'Pytheos', source: Union['Source', MusicSource],
                 parent: Union['Source', 'MediaContainer']=None):
        super().__init__()

        self._pytheos = pytheos
        self._source = source
        self._parent = parent

        self._nocache = False
        self._items = None

    def __getitem__(self, item):
        return self._items[item]

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<SourceController(id={self.id}, name={self.name})>"

    def retrieve_metadata(self):
        self._pytheos.api.browse.retrieve_metadata()

    def refresh(self, force: bool=False):
        """ Refreshes the container if it is uninitialized, this call is forced, or if caching is disabled.

        :param force: Force refresh
        :return: None
        """
        if self._items is None or self.nocache or force:
            items = self._pytheos.api.browse.browse_source(self.id)
            self._items = [create_media_leaf(item, self, self._pytheos) for item in items]

        return self._items
