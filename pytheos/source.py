#!/usr/bin/env python
from collections import Sequence

from pytheos.api.browse.types import MusicSource, SourceMedia

from typing import TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from pytheos import Pytheos


class PytheosSource(Sequence):
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

    def __init__(self, pytheos: 'Pytheos', source: Union['PytheosSource', MusicSource], parent: Union['PytheosSource', 'PytheosContainer']=None):
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
        return f"<PytheosSource(id={self.id}, name={self.name})>"

    def retrieve_metadata(self):
        self._pytheos.api.browse.retrieve_metadata()

    def refresh(self, force: bool=False):
        """ Refreshes the container if it is uninitialized, this call is forced, or if caching is disabled.

        :param force: Force refresh
        :return: None
        """
        if self._items is None or self.nocache or force:
            items = self._pytheos.api.browse.browse_source(self.id)
            self._items = [_node_factory(item, self, self._pytheos) for item in items]

        return self._items


class PytheosContainer(Sequence):
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

    def __init__(self, pytheos: 'Pytheos', container: MusicSource, parent: Union[PytheosSource, 'PytheosContainer'], source_id=None):
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
        return f"<PytheosContainer(id={self.id}, name={self.name})>"

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
            self._items = [_node_factory(item, self, self._pytheos) for item in items]

        return self._items


class PytheosMedia:
    @property
    def name(self):
        return self._media.name

    @property
    def id(self):
        return self._media.media_id

    @property
    def is_container_type(self):
        return self._media.type.is_container

    @property
    def queue_id(self):
        return self._media.queue_id

    @property
    def parent(self):
        return self._parent

    def __init__(self, pytheos: 'Pytheos', media: SourceMedia, parent: Optional[Union[PytheosSource, PytheosContainer]]):
        self._pytheos = pytheos
        self._parent = parent
        self._media = media

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<PytheosMedia(id={self.id}, name={self.name})>"


def _node_factory(item, parent, pytheos):
    if item.container:
        return PytheosContainer(pytheos, item, parent, source_id=parent.source_id)
    elif item.media_id is None:
        return PytheosSource(pytheos, item, parent)

    return PytheosMedia(pytheos, item, parent)
