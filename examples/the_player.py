#!/usr/bin/env python
"""
This example demonstrates high-level use of the Pytheos Player controller.
"""
import asyncio
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytheos

DISCOVERY_TIMEOUT = 3


async def main():
    print("Discovering HEOS services..")
    services = await pytheos.discover(DISCOVERY_TIMEOUT)
    if not services:
        print("No HEOS services detected!")
        return

    print("Connecting to first HEOS service..")
    with await pytheos.connect(services[0]) as p:
        player_id = None
        players = await p.get_players()

        for pid, player in players.items():
            print(f"Found player {player.name} ({player.id})!")
            player_id = pid

        assert player_id is not None
        player = players[player_id]

        print(f"Using player {player.name} ({player.id})")
        print()
        await print_details(player)

        # You also have full control of the other player features.  These are left disabled so you don't accidentally
        # play that sweet speed metal you had queued up at 100% volume at 1AM.
        #
        # player.play()
        # player.next()
        # player.previous()
        # player.stop()


async def print_details(player):
    print(f"Model: {player.model}")
    print(f"Version: {player.version}")
    print(f"Serial Number: {player.serial}")
    print(f"IP Address: {player.ip}")
    print()

    group = player.get_group()
    if group:
        print(f"Group: {group.id}")
        print(f"Group Leader: {group.leader.name}")
        print(f"Group Members: {[member.name for member in group.members]}")
        print()

    play_state = await player.get_play_state()
    repeat, shuffle = await player.get_play_mode()
    volume = await player.get_volume()
    print(f"Current Play State: {play_state.name}")
    print(f"Shuffle is {shuffle.name}, Repeat is {repeat.name}")
    print(f"Volume is {volume}%")
    print()

    if await player.is_playing():
        now_playing = await player.get_now_playing()
        print(f"Now Playing: {now_playing.artist} - {now_playing.song}")
        print()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
