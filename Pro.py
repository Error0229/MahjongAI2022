class Pro:
    wind = 0
    wan = [1, 1, 3, 1, 2, 3, 0, 0, 1]  # 0-8
    so = [0, 0, 0, 1, 0, 0, 0, 2, 1]  # 9-17
    pin = [1, 1, 0, 1, 0, 0, 0, 0, 0]  # 18-26
    honor = [0, 0, 0, 0, 0, 0, 0]
    hands = [wan, so, pin]
    gameboard = None
    hand = []
    open_meld = []
    partition = {}
    efficiency_map = {}
    num_remain_tile = 70
    tile_count = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
                  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
    discards = []
    han = 0
    fu = 20

    def __init__(self, gameboard):
        self.hand = []
        self.open_meld = []
        self.gameboard = gameboard
        self.tile_count = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
                           4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
        self.discards = []
        self.num_remain_tile = 83
        self.fu = 20
        self.han = 0
        self.seq_meld = 0
        self.tri_meld = 0

    def set_seat(self, wind):
        self.wind = wind

    def discard_add(self, tile):
        self.discards.append(tile)

    def meld_add(self, meld):
        self.open_meld.append(meld)

    def open_meld_getter(self):
        return self.open_meld

    def discard_getter(self):
        return self.discards
