#!/usr/bin/env python
from dataclasses import dataclass


@dataclass
class Group:
    name: str
    group_id: int
    players: list

    def __init__(self, from_dict=None):
        if from_dict:
            self.name = from_dict.get('name')
            self.group_id = from_dict.get('group_id')

            self.players = [GroupPlayer(gp) for gp in from_dict.get('players', [])]
