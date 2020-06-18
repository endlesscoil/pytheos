import os
import sys;
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pprint

import pytheos.discovery



services = pytheos.discovery.discover()

if not services:
    print("No HEOS services detected!")
else:
    svc = services[0]
    svc.connect()
    players = svc.api.player.get_players()
    pprint.pprint(players)
