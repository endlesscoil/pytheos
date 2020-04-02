#!/usr/bin/env python
import re

def extract_ip(url):
    return re.match(r"http://([^:/]+)[:/]", url).group(1)

def build_command_string(group, command, **kwargs):
    # FIXME: encoding

    attributes = '&'.join((
        '='.join((k, v)) for k, v in kwargs.items()
    ))

    command_string = f"heos://{group}/{command}"
    if attributes:
        command_string += f"?{attributes}"

    return command_string + "\n"
