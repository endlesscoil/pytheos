#!/usr/bin/env python
""" General utility functions """

from __future__ import annotations

import re
from socket import socket
from typing import Optional

import netifaces

CHARACTER_REPLACE_MAP = {
    '&': '%26',
    '=': '%3D',
    '%': '%25',
}


def extract_host(url: str) -> Optional[str]:
    """ Extracts the hostname or IP address from the supplied URL.

    :param url: URL string
    :return: Matching string or None if not found
    """
    match = re.match(r"https?://([^:/]+)[:/]?", url)    # Should match any valid url host.
    return match.group(1) if match else None


def build_command_string(group: str, command: str, **kwargs) -> str:
    """ Builds the command string to send to the HEOS service.

    :param group: Group name (e.g. system, player, etc)
    :param command: Command name (e.g. heart_beat)
    :param kwargs: Any parameters that should be sent along with the command
    :return: The command string
    """
    # Concatenate our vars string together from the keys and values we're provided.
    attributes = '&'.join(
        '='.join(
            (k, _encode_characters(v))
        ) for k, v in kwargs.items()
    )

    command_string = f"heos://{group}/{command}"
    if attributes:
        command_string += f"?{attributes}"

    return command_string + "\n"


def _encode_characters(input_string) -> str:
    """ Encodes certain special characters as defined by the HEOS specification.

    :param input_string: String to encode
    :return: New string with encoded characters
    """
    if not isinstance(input_string, str):
        input_string = str(input_string)

    results = ''
    for c in input_string:
        replacement_char = CHARACTER_REPLACE_MAP.get(c)
        results += replacement_char if replacement_char else c

    return results


def parse_var_string(input_string: str) -> dict:
    """ Parses a URL parameter string (sorta) like "var1='val1'&var2='val2'" - also supports the special case
    where there is no value specified, such as "signed_in&un=username", for the player/signed_in command.

    :param input_string: Input string to parse
    :return: dict
    """
    variables = {}

    if input_string is not None:
        var_strings = [var_string.split('=') for var_string in input_string.split('&')]
        for elements in var_strings:
            # Copy name to value for vars with no value specified - e.g. signed_in&un=username
            name = elements[0]
            value = name
            if len(elements) > 1:
                value = elements[1]

            variables[name] = _decode_characters(value.strip("'"))

    return variables


def _decode_characters(input_string: str) -> str:
    """ Decodes certain special characters as defined by the HEOS specification.

    :param input_string: String to decode
    :return: New string with decoded characters
    """
    results = input_string
    for replacement_str, original_str in CHARACTER_REPLACE_MAP.items():
        results = results.replace(original_str, replacement_str)

    return results


def get_default_ip(address_family: socket.AddressFamily) -> str:
    """ Retrieves the IP address on the default interface

    :param address_family: Address family
    :return: str
    """
    gateway, inf = get_default_interface(address_family)
    return get_interface_ip(inf, address_family)


def get_interface_ip(interface: str, address_family: socket.AddressFamily) -> Optional[str]:
    """ Retrieves the IP address of the specified interface.

    :param interface: Interface name
    :param address_family: Address family
    :return: str or None if not found
    """
    addresses = netifaces.ifaddresses(interface)
    proto_address = addresses.get(address_family)
    if not proto_address:
        return None

    return proto_address[0].get('addr')


def get_default_interface(address_family: socket.AddressFamily) -> tuple:
    """ Retrieves the default gateway and interface for the specified address family.

    :param address_family: Address family
    :return: tuple
    """
    gateways = netifaces.gateways()
    return gateways['default'].get(address_family)
