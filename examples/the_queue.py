#!/usr/bin/env python
"""
This example demonstrates high-level use of the Pytheos Queue controller.
"""
import asyncio

import pytheos
from examples.low_level.browse import browse_path


DISCOVERY_TIMEOUT = 3


async def main():
    print("Discovering HEOS services..")
    services = await pytheos.discover(DISCOVERY_TIMEOUT)
    if not services:
        print("No HEOS services detected!")
        return

    print("Connecting to first HEOS service..")
    with await pytheos.connect(services[0]) as p:
        players = await p.get_players()

        for heos_player in players:
            print(f"Found player {heos_player.name} ({heos_player.id})!")

        assert len(players) > 0
        player = players[0]
        print(f"Using player {player.name} ({player.id})")
        print()
        print("Current queue:")
        await player.queue.refresh()
        for item in player.queue:
            print(f"{item.queue_id}. {item.name}")

        print()
        print("Clearing queue!")
        await player.queue.clear()

        tracks = await browse_path(p, '/Local Music/Plex Media Server: drizzle/Music/Music/By Folder/Metal/Zyklon')
        for itm in tracks.keys():
            print(f"Adding {itm}")
            await player.queue.append(tracks[itm].object)

        print()
        print("New queue contents:")
        for item in player.queue:
            print(f"{item.queue_id}. {item.name}")

        print()
        tracks = await browse_path(p, '/History/TRACKS')
        if len(tracks) > 2:
            obj = tracks.get_item(-1).object
            print(f"Inserting {obj.name} from history at pos 1")
            await player.queue.insert(1, obj)

            print("Deleting second-to-last entry in queue")
            await player.queue.delete(-2)

            obj = tracks.get_item(-2).object
            print(f"Replacing 5th element with {obj.name}")
            await player.queue.replace(4, obj)

            await player.queue.refresh()
            print()
            print("Final queue contents:")
            for item in player.queue:
                print(f"{item.queue_id}. {item.name}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
