from enum import Enum


class AccountStatus(Enum):
    SignedOut = 'signed_out'
    SignedIn = 'signed_in'

    def __str__(self):
        return str(self.value)
