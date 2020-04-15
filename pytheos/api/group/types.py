#!/usr/bin/env python
from dataclasses import dataclass
from enum import Enum


class GroupRole(Enum):
    Leader = 'leader'
    Member = 'member'

    def __str__(self):
        return self.value


@dataclass
class Group:
    name: str
    group_id: int
    players: list

    def __init__(self, from_dict: dict=None):
        if from_dict:
            self.name = from_dict.get('name')
            self.group_id = from_dict.get('gid')

            self.players = [GroupPlayer(gp) for gp in from_dict.get('players', [])]


@dataclass
class GroupPlayer:
    name: str
    player_id: int
    role: GroupRole

    def __init__(self, from_dict: dict=None):
        if from_dict:
            self.name = from_dict.get('name')
            self.player_id = from_dict.get('pid')
            self.role = GroupRole(from_dict.get('role'))
