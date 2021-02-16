#!/usr/bin/env python
"""
This example demonstrates how to subscribe to events from the HEOS device.
"""
import logging
import os
import sys
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytheos
from pytheos.models.heos import HEOSEvent

DISCOVERY_TIMEOUT = 3


async def _on_now_playing_changed(event: HEOSEvent):
    """ Handles event/player_now_playing_changed events from HEOS.

    :param event: Event object
    :return: None
    """
    print(f'Now Playing Changed Event: {event}')


async def _on_player_state_changed(event: HEOSEvent):
    """ Handles event/player_state_changed events from HEOS.

    :param event: Event object
    :return: None
    """
    print(f'Player State Changed Event: {event}')


async def main():
    """ Main entry point """
    services = await pytheos.discover(DISCOVERY_TIMEOUT)
    if not services:
        print("No HEOS services detected!")
        return

    print("Connecting to first device found...")
    with await pytheos.connect(services[0]) as p:
        import pytheos.logger as logger
        logger.Logger.setLevel(logging.DEBUG)

        print(f"Connected to {p.server}!")
        p.subscribe('event/player_state_changed', _on_player_state_changed)
        p.subscribe('event/player_now_playing_changed', _on_now_playing_changed)

        print("Okay, go play something on your stereo - Ctrl+C to stop!")
        while True:
            await asyncio.sleep(0.5)


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.run_forever()

    except KeyboardInterrupt:
        print('Exiting..')
