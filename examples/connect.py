#!/usr/bin/env python
"""
This example demonstrates how to connect to a HEOS device by IP address and port number.
"""
import os
import sys
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytheos


async def main():
    assert len(sys.argv) > 1, f"Usage: {sys.argv[0]} <host>"
    host = sys.argv[1]

    with await pytheos.connect(host) as svc:
        players = await svc.api.player.get_players()

        print('Found players:')
        for p in players:
            print(f'- id={p.player_id}, name={p.name}, ip={p.ip}')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
