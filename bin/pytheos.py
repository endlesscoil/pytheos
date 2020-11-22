#!/usr/bin/env python
""" CLI interface for working with the Pytheos devices """
from pytheos.networking.discovery import discover


def main():
    discovered = discover()
    print(discovered)


if __name__ == '__main__':
    main()
