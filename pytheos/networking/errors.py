#!/usr/bin/env python
from __future__ import annotations

from enum import Enum
from typing import Optional

from ..errors import PytheosError
from ..models.heos import HEOSResult


class HEOSErrorCode(Enum):
    UnrecognizedCommand = 1
    InvalidID = 2
    WrongNumberOfCommandArguments = 3
    RequestedDataNotAvailable = 4
    ResourceCurrentlyNotAvailable = 5
    InvalidCredentials = 6
    CommandCouldNotBeExecuted = 7
    UserNotLoggedIn = 8
    ParameterOutOfRange = 9
    UserNotFound = 10
    InternalError = 11
    SystemError = 12
    ProcessingPreviousCommand = 13
    MediaCannotBePlayed = 14
    OptionNotSupported = 15
    CommandQueueFull = 16
    ReachedSkipLimit = 17


class HEOSSystemErrorCode(Enum):
    RemoteServiceReturnedError = -9
    UserNotRegisters = -1061
    UserNotLoggedIn = -1063
    UserNotFound = -1056
    AuthenticationError = -1201
    AuthorizationError = -1232
    UserParametersInvalid = -1239


class ChannelUnavailableError(PytheosError):
    """ Error returned when a channel is unavailable """
    pass


class CommandFailedError(PytheosError):
    """ Error returned with a command fails to execute """
    def __init__(self, message: str, result: Optional[HEOSResult]):
        self.result = result
        self.message = message
        self.error_code = None
        self.system_error_code = None

        eid = result.header.vars.get('eid') if result else None
        if eid:
            self.error_code = HEOSErrorCode(int(eid))
            if self.error_code == HEOSErrorCode.SystemError:
                system_error_code = result.header.vars.get('syserrno')
                try:
                    self.system_error_code = HEOSSystemErrorCode(system_error_code)
                except ValueError:
                    self.system_error_code = system_error_code  # Unknown error code


class SignInFailedError(CommandFailedError):
    """ Error returned when the system/sign_in command fails """
    pass


class InvalidResponse(PytheosError):
    """ Error returned when the response to a command appears invalid """
    pass
