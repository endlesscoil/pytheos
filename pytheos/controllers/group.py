#!/usr/bin/env python
from __future__ import annotations

from .. import models

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pytheos import Pytheos
    from .. import controllers


class Group:
    """ High-level Group Representation """

    @property
    def id(self) -> int:
        return self._group.group_id

    @property
    def members(self) -> tuple:
        return tuple(self._members)

    def __contains__(self, player):
        return player.id == self._leader.id or any([p.id == player.id for p in self._members])

    def __init__(self, pytheos: 'Pytheos', group: models.Group):
        self._pytheos: 'Pytheos' = pytheos
        self._group: models.Group = group

        group_count = len(group.players)
        self._leader: 'controllers.Player' = group.players[0] if group_count > 0 else None
        self._members = group.players[1:] if group_count > 1 else []

    async def refresh(self, force=False):
        """ Refreshes the group information if leader is unset or force is specified.

        :param force: Force refresh
        :return: None
        """
        if not self._leader or force:
            self._group = await self._pytheos.api.group.get_group_info(self._group.group_id)

    async def add_member(self, player: 'controllers.Player'):
        """ Adds a new member to the group.

        :param player: Player
        :return: None
        """
        await self.refresh(force=True)

        if player in self:
            raise ValueError('Player is already present in this group.')

        self._members.append(player)
        await self._set_group()

    async def remove_member(self, player: 'controllers.Player'):
        """ Remove a member from a group.

        :param player: Player
        :return: None
        """
        await self.refresh(force=True)

        if player not in self:
            raise ValueError('Player is not present in this group.')

        if player in self._members:
            self._members.remove(player)

        if self._leader == player and len(self._members) > 1:
            self._leader = self._members[0]

        await self._set_group()

    async def get_leader(self) -> 'controllers.Player':
        await self.refresh(True)
        return self._leader

    async def set_leader(self, value: 'controllers.Player'):
        self._leader = value
        await self._set_group()

    async def get_muted(self) -> bool:
        return await self._pytheos.api.group.get_mute(self._group.group_id)

    async def set_muted(self, value: bool):
        await self._pytheos.api.group.set_mute(self._group.group_id, value)

    async def get_volume(self) -> int:
        return await self._pytheos.api.group.get_volume(self._group.group_id)

    async def set_volume(self, value: int):
        if value < self._pytheos.api.group.VOLUME_MIN:
            value = self._pytheos.api.group.VOLUME_MIN
        elif value > self._pytheos.api.group.VOLUME_MAX:
            value = self._pytheos.api.group.VOLUME_MAX

        await self._pytheos.api.group.set_volume(self._group.group_id, value)

    async def _set_group(self):
        """ Send the new group details to HEOS.

        :return: None
        """
        await self._pytheos.api.group.set_group(self._leader.id, [p.id for p in self._members])
