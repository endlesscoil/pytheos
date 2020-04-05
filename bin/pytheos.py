#!/usr/bin/env python
""" CLI interface for working with the Pytheos devices """

from __future__ import annotations

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..")) # FIXME

from pytheos import discover


def main():
    discovered = discover()
    print(discovered)


if __name__ == '__main__':
    main()
