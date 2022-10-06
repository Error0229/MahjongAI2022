
class OpponentClass():
    
    def __init__(self):
        self.opponent_discard = []
        self.open_meld = []

    def discard_add(self,tile):
        self.opponent_discard.append(tile)

    def meld_add(self,meld):
        self.open_meld.append(meld)

    def open_meld_getter(self):
        return self.open_meld
    
    def discard_getter(self):
        return self.opponent_discard

