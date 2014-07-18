import itertools
import Player as base

class AIPlayer(base.Player):

    def __init__(self, name):
        base.__init__(self, name)

    def get_move(self, b):
        return NotImplemented()
