#!/usr/bin/env python
from __future__ import annotations

from typing import Optional

from .. import models


class GroupAPI:
    """ API interface for the 'group' command group """

    VOLUME_MIN = 0
    VOLUME_MAX = 100
    VOLUME_STEP_MIN = 1
    VOLUME_STEP_MAX = 10

    def __init__(self, conn):
        self._api = conn

    async def get_groups(self) -> list:
        """ Retrieves a list of all groups.

        :return: list
        """
        results = await self._api.call('group', 'get_groups')
        return [models.Group(grp) for grp in results.payload]

    async def get_group_info(self, group_id: int) -> models.Group:
        """ Retrieves the group information for the specified group.

        :param group_id: Group ID
        :return: Group
        """
        results = await self._api.call('group', 'get_group_info', gid=group_id)
        return models.Group(results.payload)

    async def get_mute(self, group_id: int) -> bool:
        """ Returns whether or not the group is currently muted

        :param group_id: Group ID
        :return: bool
        """
        results = await self._api.call('group', 'get_mute', gid=group_id)
        return results.header.vars.get('state') == 'on'

    async def get_volume(self, group_id: int) -> int:
        """ Retrieves the current volume

        :param group_id: Group ID
        :return: int
        """
        results = await self._api.call('group', 'get_volume', gid=group_id)
        return int(results.header.vars.get('level'))

    async def set_group(self, leader_id: int, member_ids=None) -> Optional[models.Group]:
        """ Sets up a group leader and associated member players.

        :param leader_id: Leader ID
        :param member_ids: List of Member IDs or None to delete the group
        :return: Group if a group was created or modified, None if it was deleted
        """
        player_ids = [leader_id]
        if member_ids:
            player_ids += member_ids

        results = await self._api.call('group', 'set_group', pid=','.join([str(pid) for pid in player_ids]))

        if results.header.vars.get('gid') is not None:
            return models.Group(results.header.vars)

        return None

    async def set_mute(self, group_id: int, enable: bool) -> None:
        """ Enables or disables mute on the specified group

        :param group_id: Group ID
        :param enable: True or False
        :return: None
        """
        await self._api.call('group', 'set_mute', gid=group_id, state=models.player.Mute.On if enable else models.player.Mute.Off)

    async def set_volume(self, group_id: int, level: int) -> None:
        """ Sets the volume level on the group

        :param group_id: Group ID
        :param level: Volume level
        :raises: ValueError
        :return: None
        """
        if not self.VOLUME_MIN <= level <= self.VOLUME_MAX:
            raise ValueError(f'Level must be between {self.VOLUME_MIN} and {self.VOLUME_MAX}')

        await self._api.call('group', 'set_volume', gid=group_id, level=level)

    async def toggle_mute(self, group_id: int) -> None:
        """ Toggles mute on the group

        :param group_id: Group ID
        :return: None
        """
        await self._api.call('group', 'toggle_mute', gid=group_id)

    async def volume_up(self, group_id: int, step_level: int=5) -> None:
        """ Turn the volume up by the specified step level.

        :param group_id: Group ID
        :param step_level: Step level
        :raises: ValueError
        :return: None
        """
        if not self.VOLUME_STEP_MIN < step_level <= self.VOLUME_STEP_MAX:
            raise ValueError(f'Step level must be between {self.VOLUME_STEP_MIN} and {self.VOLUME_STEP_MAX}')

        await self._api.call('group', 'volume_up', gid=group_id, step=step_level)

    async def volume_down(self, group_id: int, step_level: int = 5) -> None:
        """ Turn the volume down by the specified step level.

        :param group_id: Group ID
        :param step_level: Step level
        :raises: ValueError
        :return: None
        """
        if not self.VOLUME_STEP_MIN < step_level <= self.VOLUME_STEP_MAX:
            raise ValueError(f'Step level must be between {self.VOLUME_STEP_MIN} and {self.VOLUME_STEP_MAX}')

        await self._api.call('group', 'volume_down', gid=group_id, step=step_level)
