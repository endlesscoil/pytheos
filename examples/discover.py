#!/usr/bin/env python
"""
This example demonstrates how to use SSDP to discover HEOS devices on your network.
"""
import os
import sys
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytheos
import pytheos.utils

TIMEOUT = 5
services = asyncio.get_event_loop().run_until_complete(pytheos.discover(TIMEOUT))

if services:
    print("Discovered these HEOS services:")
    for svc in services:
        print(f'- {pytheos.utils.extract_host(svc.location)}')

else:
    print("No HEOS services detected!")
