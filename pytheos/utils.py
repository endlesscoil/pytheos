#!/usr/bin/env python
""" General utility functions """

from __future__ import annotations

import re
from typing import Optional


def extract_host(url: str) -> Optional[str]:
    """ Extracts the hostname or IP address from the supplied URL.

    :param url: URL string
    :return: Matching string or None if not found
    """
    match = re.match(r"https?://([^:/]+)[:/]?", url) # Should match any valid url host.
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
        # FIXME: Do we need to wrap string arguments in quotes?
        command_string += f"?{attributes}"

    return command_string + "\n"

def parse_var_string(input: str) -> dict:
    """ Parses a URL parameter string (sorta) like "var1='val1'&var2='val2'" - also supports the special case
    where there is no value specified, such as "signed_in&un=username", for the player/signed_in command.

    :param input: Input string to parse
    :return: dict
    """
    vars = {}

    if input is not None:
        var_strings = [var_string.split('=') for var_string in input.split('&')]
        for elements in var_strings:
            # Copy name to value for vars with no value specified - e.g. signed_in&un=username
            name = elements[0]
            value = name
            if len(elements) > 1:
                value = elements[1]

            vars[name] = value.strip("'")

    return vars

def _encode_characters(input) -> str:
    """ Encodes certain special characters as defined by the HEOS specification.

    :param input: String to encode
    :return: New string with encoded characters
    """
    replace_map = {
        '&': '%26',
        '=': '%3D',
        '%': '%25',
    }

    if not isinstance(input, str):
        input = str(input)

    results = input
    for char, replacement in replace_map.items():
        results = results.replace(char, replacement)

    return results
