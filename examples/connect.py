#!/usr/bin/env python
"""
This example demonstrates how to connect to a HEOS device by IP address and port number.
"""
import os
import sys
import pprint
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytheos

HEOS_IP = os.environ.get('HEOS_IP', '127.0.0.1')
HEOS_PORT = int(os.environ.get('HEOS_PORT', 1255))


with pytheos.connect(HEOS_IP, HEOS_PORT) as svc:
    players = svc.api.player.get_players()
    pprint.pprint(players)
