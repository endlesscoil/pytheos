#!/usr/bin/env python
import re


def extract_host(url: str):
    match = re.match(r"https?://([^:/]+)[:/]?", url) # Should match any valid url host.
    return match.group(1) if match else None

def build_command_string(group: str, command: str, **kwargs) -> str:
    # Concatenate our vars string together from the keys and values we're provided.
    attributes = '&'.join((
        '='.join((k, _replace_chars(v))) for k, v in kwargs.items()
    ))

    command_string = f"heos://{group}/{command}"
    if attributes:
        # FIXME: Do we need to wrap string arguments in quotes?
        command_string += f"?{attributes}"

    return command_string + "\n"

def parse_var_string(input):
    vars = {}

    var_strings = [var_string.split('=') for var_string in input.split('&')]
    for elements in var_strings:
        # Copy name to value for vars with no value specified - e.g. signed_in&un=username
        name = elements[0]
        value = name
        if len(elements) > 1:
            value = elements[1]

        vars[name] = value.strip("'")

    return vars

def _replace_chars(input):
    replace_map = {
        '&': '%26',
        '=': '%3D',
        '%': '%25',
    }

    if not isinstance(input, str):
        return str(input)

    results = input
    for char, replacement in replace_map.items():
        results = results.replace(char, replacement)

    return results
