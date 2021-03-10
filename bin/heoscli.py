#!/usr/bin/env python
""" CLI interface for working with the Pytheos devices """
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import asyncio
import argparse
from pprint import pprint

from pytheos.networking.discovery import discover
from pytheos.utils import extract_host


async def discover_devices(args):
    print("Discovering devices...")
    devices = await discover(3)  #FIXME: args.timeout)
    if len(devices) == 0:
        print("Could not find any devices!")
        return 1

    print()
    print("Found devices:")
    for d in devices:
        host = extract_host(d.location)

        #if args.verbose: # FIXME
        print("="*(len(host)+2))
        print(f" {host} ")
        #if args.verbose: # FIXME
        print("="*(len(host)+2))
        print()
        print("-"*25)
        print(" Device response headers ")
        print("-"*25)
        pprint(d.headers)
        print()

    return 0


async def main():
    args = None
    #args = argparse.ArgumentParser() # FIXME
    assert len(sys.argv) > 1, f"Usage: {sys.argv[0]} <command>"     # FIXME: TEMP

    cmd_name = sys.argv[1]
    cmd = command_map.get(cmd_name)
    if not cmd:
        raise ValueError(f"Unknown command: {cmd_name}")

    return await cmd(args)


command_map = {
    'discover': discover_devices,
}


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
