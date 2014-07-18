import Player as base

class HumanPlayer(base.Player):
    base.__init__('Human')

    def get_move(self):   # we'll override with GUI
        return None
