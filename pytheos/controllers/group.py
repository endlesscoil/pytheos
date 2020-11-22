#!/usr/bin/env python
from ..models import Group

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytheos import Pytheos
    from pytheos.controllers import PlayerController


class GroupController:
    """ High-level Group Representation """

    @property
    def id(self) -> int:
        return self._group.group_id

    @property
    def leader(self) -> 'PlayerController':
        return self._leader

    @leader.setter
    def leader(self, value: 'PlayerController'):
        self.refresh(True)
        self._leader = value
        self._set_group()

    @property
    def members(self) -> tuple:
        return tuple(self._members)

    @property
    def muted(self) -> bool:
        return self._pytheos.api.group.get_mute(self._group.group_id)

    @muted.setter
    def muted(self, value: bool):
        self._pytheos.api.group.set_mute(self._group.group_id, value)

    @property
    def volume(self) -> int:
        return self._pytheos.api.group.get_volume(self._group.group_id)

    @volume.setter
    def volume(self, value: int):
        if value < self._pytheos.api.group.VOLUME_MIN:
            value = self._pytheos.api.group.VOLUME_MIN
        elif value > self._pytheos.api.group.VOLUME_MAX:
            value = self._pytheos.api.group.VOLUME_MAX

        self._pytheos.api.group.set_volume(self._group.group_id, value)

    def __contains__(self, player):
        return player.id == self._leader.id or any([p.id == player.id for p in self._members])

    def __init__(self, pytheos: 'Pytheos', group: Group):
        self._pytheos: 'Pytheos' = pytheos
        self._group: Group = group

        group_count = len(group.players)
        self._leader: 'PlayerController' = group.players[0] if group_count > 0 else None
        self._members = group.players[1:] if group_count > 1 else []

    def refresh(self, force=False):
        """ Refreshes the group information if leader is unset or force is specified.

        :param force: Force refresh
        :return: None
        """
        if not self._leader or force:
            self._group = self._pytheos.api.group.get_group_info(self._group.group_id)

    def add_member(self, player: 'PlayerController'):
        """ Adds a new member to the group.

        :param player: Player
        :return: None
        """
        self.refresh(force=True)

        if player in self:
            raise ValueError('Player is already present in this group.')

        self._members.append(player)
        self._set_group()

    def remove_member(self, player: 'PlayerController'):
        """ Remove a member from a group.

        :param player: Player
        :return: None
        """
        self.refresh(force=True)

        if not player in self:
            raise ValueError('Player is not present in this group.')

        if player in self._members:
            self._members.remove(player)

        if self._leader == player and len(self._members) > 1:
            self._leader = self._members[0]

        self._set_group()

    def _set_group(self):
        """ Send the new group details to HEOS.

        :return: None
        """
        self._pytheos.api.group.set_group(self._leader.id, [p.id for p in self._members])
