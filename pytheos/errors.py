#!/usr/bin/env python
from __future__ import annotations

from typing import Optional

from pytheos.types import HEOSResult


class Error(Exception):
    pass

class ChannelUnavailableError(Error):
    pass

class CommandFailedError(Error):
    def __init__(self, message: str, result: Optional[HEOSResult]):
        self.result = result
        self.message = message

class SignInFailedError(CommandFailedError):
    pass
