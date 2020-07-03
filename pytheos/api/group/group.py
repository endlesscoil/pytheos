#!/usr/bin/env python
from typing import Optional

from pytheos.api.api import API
from pytheos.api.group.types import Group
from pytheos.api.types import Mute


class GroupAPI(API):
    """ API interface for the 'group' command group """

    def get_groups(self) -> list:
        """ Retrieves a list of all groups.

        :return: list
        """
        results = self._api.call('group', 'get_groups')
        return [Group(grp) for grp in results.payload]

    def get_group_info(self, group_id: int) -> Group:
        """ Retrieves the group information for the specified group.

        :param group_id: Group ID
        :return: Group
        """
        results = self._api.call('group', 'get_group_info', gid=group_id)
        return Group(results.payload)

    def get_mute(self, group_id: int) -> bool:
        """ Returns whether or not the group is currently muted

        :param group_id: Group ID
        :return: bool
        """
        results = self._api.call('group', 'get_mute', gid=group_id)
        return results.header.vars.get('state') == 'on'

    def get_volume(self, group_id: int) -> int:
        """ Retrieves the current volume

        :param group_id: Group ID
        :return: int
        """
        results = self._api.call('group', 'get_volume', gid=group_id)
        return int(results.header.vars.get('level'))

    def set_group(self, leader_id: int, member_ids=None) -> Optional[Group]:
        """ Sets up a group leader and associated member players.

        :param leader_id: Leader ID
        :param member_ids: List of Member IDs or None to delete the group
        :return: Group if a group was created or modified, None if it was deleted
        """
        player_ids = [leader_id]
        if member_ids:
            player_ids += member_ids

        results = self._api.call('group', 'set_group', pid=','.join([str(pid) for pid in player_ids]))

        if results.header.vars.get('gid') is not None:
            return Group(results.header.vars)

        return None

    def set_mute(self, group_id: int, enable: bool) -> None:
        """ Enables or disables mute on the specified group

        :param group_id: Group ID
        :param enable: True or False
        :return: None
        """
        self._api.call('group', 'set_mute', gid=group_id, state=Mute.On if enable else Mute.Off)

    def set_volume(self, group_id: int, level: int) -> None:
        """ Sets the volume level on the group

        :param group_id: Group ID
        :param level: Volume level
        :raises: ValueError
        :return: None
        """
        if not 0 <= level <= 100:
            raise ValueError('Level must be between 0 and 100')

        self._api.call('group', 'set_volume', gid=group_id, level=level)

    def toggle_mute(self, group_id: int) -> None:
        """ Toggles mute on the group

        :param group_id: Group ID
        :return: None
        """
        self._api.call('group', 'toggle_mute', gid=group_id)

    def volume_up(self, group_id: int, step_level: int=5) -> None:
        """ Turn the volume up by the specified step level.

        :param group_id: Group ID
        :param step_level: Step level
        :raises: ValueError
        :return: None
        """
        if not 0 < step_level <= 10:
            raise ValueError('Step level must be between 1 and 10')

        self._api.call('group', 'volume_up', gid=group_id, step=step_level)

    def volume_down(self, group_id: int, step_level: int = 5) -> None:
        """ Turn the volume down by the specified step level.

        :param group_id: Group ID
        :param step_level: Step level
        :raises: ValueError
        :return: None
        """
        if not 0 < step_level <= 10:
            raise ValueError('Step level must be between 1 and 10')

        self._api.call('group', 'volume_down', gid=group_id, step=step_level)
