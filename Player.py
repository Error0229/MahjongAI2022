from MahjongKit.MahjongKit import Tile, Meld, Partition, WinWaitCal

class Player:
    wind = 0
    seat = 0
    tiles = []
    discard_tiles = []
    points = 0
    gameboard = None
    open_melds = []
    riichi_status = False

    def __init__(self, gameboard):
        self.tiles = []
        self.discard_tiles = []
        self.points = 25000
        self.gameboard = gameboard
        self.open_melds = []
        self.riichi_status = False

    def init_tiles(self, tiles):
        self.tiles = tiles

    def set_seat(self, seat):
        self.seat = seat

    def set_wind(self, wind):
        self.wind = wind

    def init_round(self, tiles, wind):
        self.tiles = tiles
        self.wind = wind

    def discard_tile(self, tile=None):
        tile = self.tiles[0]
        self.tiles.remove(tile)
        self.discard_tiles.append(tile)
        self.gameboard.discard_tile(self.seat, tile)
        return tile

    def draw_tile(self, tile):
        self.tiles.append(tile)
        self.tiles.sort()

    def action(self):
        return [-1]

    def get_shantin(self):
        bonus_chr = filter(lambda f:f in [self.wind+27, self.seat+27 ,31, 32, 33], self.tiles)
        return Partition.shantin_multiple_forms(self.tiles, self.open_melds, bonus_chr)
    
    
    # return [int:how_many_ways_to_chi, [ways of chi]]
    def can_chi(self, tile, from_player):
        if((self.seat - from_player)%4 != 1):
            return [0, []]
        else:
            chi_lst = []
            for parts in Partition.partition(self.tiles):
                for part in parts:
                    if(len(part)==2 and part[0]!=part[1]):
                        tmp = [part+tile].sort 
                        if((tmp in Tile.index_to_chow) and (tmp not in chi_lst)):
                            chi_lst.append(tmp)
            return [len(chi_lst), chi_lst]

    # return [int:0/1, [pon]]
    def can_pon(self, tile):
        if(self.tiles.count(tile) < 2):
            return [0, []]
        else:
            return [1, [tile, tile, tile]]

    # return [int:0/1, [minkan]]
    def can_minkan(self, tile):
        if(self.tiles.count(tile) != 3):
            return [0, []]
        else:
            return [1, [tile, tile, tile, tile]]

    def can_ankan(self, tile):
        pass

    def can_win(self):
        pass

    def can_riichi(slef):
        pass
    
    @property
    def is_tenpai(self):
        return False
