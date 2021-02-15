#!/usr/bin/env python
from __future__ import annotations

from .. import models

from typing import TYPE_CHECKING, Sequence, Union, Optional
if TYPE_CHECKING:
    from pytheos import Pytheos


def create_media_leaf(item, parent, pytheos_obj):
    """ Returns a leaf for our tree with a type appropriate for the response.

    :param item:
    :param parent:
    :param pytheos_obj:
    :return:
    """
    from pytheos.controllers.source import Source

    if item.container:
        return MediaContainer(pytheos_obj, item, parent, source_id=parent.source_id)

    if item.media_id is not None:
        return MediaItem(pytheos_obj, item, parent)

    return item


class MediaContainer(Sequence):
    @property
    def id(self):
        return self._container.container_id

    @property
    def source_id(self):
        return self._source_id

    @property
    def name(self):
        return self._container.name

    @property
    def nocache(self):
        return self._nocache

    @nocache.setter
    def nocache(self, value):
        self._nocache = value

    @property
    def is_container_type(self):
        return self._container.type.is_container

    @property
    def parent(self):
        return self._parent

    def __init__(self, pytheos: 'Pytheos', container: models.Source, parent: Union['models.Source', 'MediaContainer'],
                 source_id=None):
        super().__init__()

        self._pytheos = pytheos
        self._parent = parent
        self._container = container
        self._nocache = False
        self._source_id = source_id

        self._items: Optional[list] = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<HEOSContainer(id={self.id}, name={self.name})>"

    def __getitem__(self, item):
        return self._items[item]

    def __len__(self):
        return len(self._items)

    def refresh(self, force: bool=False):
        """ Refreshes the container if it is uninitialized, this call is forced, or if caching is disabled.

        :param force: Force refresh
        :return: None
        """
        if self._items is None or self.nocache or force:
            items = self._pytheos.api.browse.browse_source_container(self._source_id, self.id)
            self._items = [create_media_leaf(item, self, self._pytheos) for item in items]

        return self._items


class MediaItem:
    @property
    def name(self):
        return self._media.name

    @property
    def id(self):
        return self._media.media_id

    @property
    def is_container_type(self):
        return self._media.is_container     # FIXME - what should this be now with all the rearranging?

    @property
    def queue_id(self):
        return self._media.queue_id

    @property
    def parent(self):
        return self._parent

    def __init__(self, pytheos: 'Pytheos', media: models.MediaItem,
                 parent: Optional[Union['models.Source', 'MediaContainer']]):
        self._pytheos = pytheos
        self._parent = parent
        self._media = media

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<ContainerItem(id={self.id}, name={self.name})>"
