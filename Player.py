class Player:
    def __init__(self, name):
        self.name  = name

    def get_move(self):
        raise NotImplementedError()
            
