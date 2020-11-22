#!/usr/bin/env python
"""
This example demonstrates how to connect to a HEOS device by IP address and port number.
"""
import os
import sys
import pprint
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytheos


def main():
    assert len(sys.argv) > 1, f"Usage: {sys.argv[0]} <host>"
    host = sys.argv[1]

    with pytheos.connect(host) as svc:
        players = svc.api.player.get_players()
        pprint.pprint(players)


if __name__ == '__main__':
    main()
