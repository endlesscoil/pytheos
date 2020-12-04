#!/usr/bin/env python
"""
This example demonstrates high-level use of the Pytheos Player controller.
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytheos


def main():
    print("Discovering HEOS services..")
    services = pytheos.discover()
    if not services:
        print("No HEOS services detected!")
        return

    print("Connecting to first HEOS service..")
    with pytheos.connect(services[0]) as p:
        player_id = None
        players = p.players

        for pid, player in players.items():
            print(f"Found player {player.name} ({player.id})!")
            player_id = pid

        assert player_id is not None
        player = players[player_id]

        print(f"Using player {player.name} ({player.id})")
        print()
        print_details(player)

        # You also have full control of the other player features.  These are left disabled so you don't accidentally
        # play that sweet speed metal you had queued up earlier at 100% volume at 1AM.
        #
        # player.play()
        # player.next()
        # player.previous()
        # player.stop()


def print_details(player):
    print(f"Model: {player.model}")
    print(f"Version: {player.version}")
    print(f"Serial Number: {player.serial}")
    print(f"IP Address: {player.ip}")
    print()

    if player.group:
        print(f"Group: {player.group.id}")
        print(f"Group Leader: {player.group.leader.name}")
        print(f"Group Members: {[member.name for member in player.group.members]}")
        print()

    print(f"Current Play State: {player.play_state.name}")
    print(f"Shuffle is {player.shuffle.name}, Repeat is {player.repeat.name}")
    print(f"Volume is {player.volume}%")
    print()

    if player.playing:
        print(f"Now Playing: {player.now_playing.artist} - {player.now_playing.song}")
        print()


if __name__ == '__main__':
    main()
