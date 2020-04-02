#!/usr/bin/env python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..")) # FIXME

from pytheos import discover


def main():
    discovered = discover("urn:schemas-denon-com:device:ACT-Denon:1")
    print(discovered)

if __name__ == '__main__':
    main()
