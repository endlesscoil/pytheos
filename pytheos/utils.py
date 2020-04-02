#!/usr/bin/env python
import re


def extract_ip(url: str):
    return re.match(r"https?://([^:/$]+)[:/$]", url).group(1)

def build_command_string(group: str, command: str, **kwargs) -> str:
    attributes = '&'.join((
        '='.join((k, _replace_chars(v))) for k, v in kwargs.items()
    ))

    command_string = f"heos://{group}/{command}"
    if attributes:
        command_string += f"?{attributes}"

    return command_string + "\n"

def _replace_chars(input: str) -> str:
    replace_map = {
        '&': '%26',
        '=': '%3D',
        '%': '%25',
    }

    results = input
    for char, replacement in replace_map.items():
        results = results.replace(char, replacement)

    return results
