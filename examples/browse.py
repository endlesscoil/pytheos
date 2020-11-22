#!/usr/bin/env python
"""
This example demonstrates an algorithm that uses the Browse API to retrieve the contents at a
path specified on the command line.

Example:
    Retrieve the root music source list:
    $ python examples\browse.py /
    Listing:
    - Pandora
    - iHeartRadio
    - SiriusXM
    - SoundCloud
    - Amazon
    - Local Music
    - Playlists
    - History
    - AUX Input
    - Favorites

    Retrieve the tracks in a folder:
    $ python examples\browse.py /Local Music/Plex Media Server: someserver/Music/Music/By Folder/AwesomeBand/AwesomeAlbum
    Listing:
    - Some Cool Track
    - Other Track
    - ...
"""
import os
import sys
from typing import Union

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytheos
from pytheos import Pytheos
from pytheos.models import MusicSource, SourceMedia


class TreeEntry(dict):
    """ Container class for our tree """
    def __init__(self, obj: Union[MusicSource, SourceMedia, None], **kwargs: dict):
        super().__init__(**kwargs)

        self.object = obj


def browse_path(svc: Pytheos, path: str) -> TreeEntry:
    """ Traverses the provided path starting at the list of Music Sources.  The initial list can be retrieved
    by either a blank path or '/'.  Invalid paths will throw an exception.

    :param svc: Pytheos object
    :param path: Path string
    :return: The contents of the final path component
    """
    tree = _init_tree_with_sources(svc)

    source_id = None
    current_node = tree
    for comp in path.split('/'):
        # Handle leading, trailing, or duplicate slashes
        if comp == '':
            continue

        # Refresh our current node and bail out if it can't be found.
        current_node = current_node.get(comp)
        if current_node is None:
            raise ValueError('Could not find path')

        # Retrieve the contents of our new current node
        source_id, results = _retrieve_contents(svc, source_id, current_node.object)
        for item in results:
            current_node[item.name] = TreeEntry(obj=item)

    return current_node


def _init_tree_with_sources(svc: Pytheos) -> TreeEntry:
    """ Initialize our tree with the list of Music Sources from HEOS.

    :param svc: Pytheos object
    :return: Root TreeEntry object
    """
    tree = TreeEntry(obj=None)

    for source in svc.api.browse.get_music_sources():
        tree.setdefault(source.name, TreeEntry(obj=source))

    return tree


def _retrieve_contents(svc: Pytheos, parent_id: str, source: Union[MusicSource, SourceMedia]) -> tuple:
    """ Retrieve the contents of the provided source node.

    :param svc: Pytheos object
    :param parent_id: Parent Source ID
    :param source: Source node
    :return: tuple (new source id, result list)
    """
    new_source_id = parent_id

    if source.container:
        results = svc.api.browse.browse_source_container(source_id=parent_id, container_id=source.container_id)
    else:
        # This is a nested source, so update the source ID and retrieve the contents
        new_source_id = source.source_id
        results = svc.api.browse.browse_source(new_source_id)

    return new_source_id, results


def main():
    """ Main entry point """
    services = pytheos.discover()
    if not services:
        print("No HEOS services detected!")
        return

    print("Connecting to first device found...")

    with pytheos.connect(services[0]) as p:
        print(f"Connected to {p.server}!")
        # Use all command line parameters to construct our path or default to '/' if not specified.
        path = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else '/'

        try:
            listing = browse_path(p, path)

            print("Listing:")
            for name in listing:
                print(f'- {name}')

        except ValueError as ex:
            print(f'Error: {ex}')


if __name__ == '__main__':
    main()
