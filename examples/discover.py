#!/usr/bin/env python
"""
This example demonstrates how to use SSDP to discover HEOS devices on your network.
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytheos
import pytheos.utils


services = pytheos.discover()

if services:
    print("Discovered these HEOS services:")
    for svc in services:
        print(f'- {pytheos.utils.extract_host(svc.location)}')

else:
    print("No HEOS services detected!")
