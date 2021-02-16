#!/usr/bin/env python
"""
This example demonstrates how to search for stations containing a particular term.  After retrieving the list
the user can then make use of browse.play_station() to create and play the new station.
"""
import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import pytheos
from pytheos.models.browse import ServiceOption

DISCOVERY_TIMEOUT = 3
SOURCE_ID = 1   # Pandora
SEARCH_NAME = 'a band'


async def main():
    services = await pytheos.discover(DISCOVERY_TIMEOUT)

    if services:
        with await pytheos.connect(services[0]) as p:
            results = await p.api.browse.set_service_option(SOURCE_ID, ServiceOption.CreateNewStation, name=SEARCH_NAME)

            num_results = int(results.header.vars.get('returned', 0))
            if num_results > 0:
                print(f"Search results for '{SEARCH_NAME}' .. ({num_results} stations)")
                for station in results.payload:
                    print(f"- {station['name']} (Station ID: {station['mid']})")

                print()
                print("Now you have to play the station to create it!  Get to it!")
            else:
                print("Couldn't find any results.")

            # TODO: svc.api.browse.play_station(player_id, SOURCE_ID, container_id, station['mid'], 'some station')

    else:
        print("No HEOS services detected!")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
