#!/usr/bin/env python
from pytheos.api.api import API


class Group(API):
    def get_groups(self, player_id: int) -> list:
        results = self._pytheos.api.call('group', 'get_groups', pid=player_id)
        return [Group(grp) for grp in results.payload]

    def get_group_info(self, player_id: int, group_id: int) -> Group:
        results = self._pytheos.api.call('group', 'get_group_info', pid=player_id, gid=group_id)
        return Group(results.payload)
