#!/usr/bin/env python
"""
This example demonstrates how to subscribe to events from the HEOS device.
"""
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytheos
from pytheos.types import HEOSEvent

HEOS_IP = os.environ.get('HEOS_IP', '127.0.0.1')
HEOS_PORT = int(os.environ.get('HEOS_PORT', 1255))


def _on_now_playing_changed(event: HEOSEvent):
    """ Handles event/player_now_playing_changed events from HEOS.

    :param event: Event object
    :return: None
    """
    print(f'Now Playing Changed Event: {event}')

def _on_player_state_changed(event: HEOSEvent):
    """ Handles event/player_state_changed events from HEOS.

    :param event: Event object
    :return: None
    """
    print(f'Player State Changed Event: {event}')

def main():
    """ Main entry point """

    with pytheos.connect((HEOS_IP, HEOS_PORT)) as svc:
        svc.subscribe('event/player_state_changed', _on_player_state_changed)
        svc.subscribe('event/player_now_playing_changed', _on_now_playing_changed)

        print("Okay, go play something on your stereo - Ctrl+C to stop!")
        try:
            while True:
                time.sleep(0.5)

        except KeyboardInterrupt:
            print('Exiting..')


if __name__ == '__main__':
    main()
