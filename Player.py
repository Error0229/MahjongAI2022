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

    def get_shantin(self):
        bonus_chr = filter(lambda f:f in [self.wind+27, self.seat+27 ,31, 32, 33], self.tiles)
        return Partition.shantin_multiple_forms(self.tiles, self.open_melds, bonus_chr)
    

    def do_action(self, tile, meld):
        self.open_melds.append(meld)
        for i in meld:
            if(i != tile):
                self.tiles.remove(i)
    
    # return dict contain:
    #   'type': str_action
    #   'player': int_action_player
    #   'meld': meld
    #   'tile': tile
    def can_action(self, tile, from_player):
        # choose a best option shintin-wise
        chi = self.can_chi(tile, from_player)
        pon = self.can_pon(tile)
        minken = self.can_minkan(tile)
        res = dict()
        res['player'] = self.seat
        res['tile'] = tile
        if(chi['count']>0):
            res['type'] = 'chi'
            res['meld'] = chi['melds'][0]
        elif(pon['count']>0):
            res['type'] = 'pon'
            res['meld'] = pon['melds'][0]
        elif(minken['count']>0):
            res['type'] = 'minken'
            res['meld'] = minken['melds'][0]
        else:
            res['type'] = 'none'
        return res
        
            
            
            

    
    # return {type:str, count:int, 'melds':[melds], 'tile':int}
    def can_chi(self, tile, from_player):
        res = dict()
        res['type'] = 'chi'
        res['tile'] = tile
        if((self.seat - from_player)%4 != 1):
            res['count'] = 0
            res['melds'] = []
        else:
            chi_lst = []
            for parts in Partition.partition(self.tiles):
                for part in parts:
                    if(len(part)==2 and part[0]!=part[1]):
                        tmp = [part+tile].sort 
                        if((tmp in Tile.index_to_chow) and (tmp not in chi_lst)):
                            chi_lst.append(tmp)
            res['count'] = len(chi_lst)
            res['melds'] = [[chi_lst]]
        return res


    # return {count:int, 'melds':[melds], 'tile':int}
    def can_pon(self, tile):
        res = dict()
        res['type'] = 'pon'
        res['tile'] = tile
        if(self.tiles.count(tile) < 2):
            res['count'] = 0
            res['melds'] = []
        else:
            res['count'] = 1
            res['melds'] = [[tile, tile, tile]]
        return res

    # return {count:int, 'melds':[melds], 'tile':int}
    def can_minkan(self, tile):
        res = dict()
        res['type'] = 'minkan'
        res['tile'] = tile
        if(self.tiles.count(tile) < 3):
            res['count'] = 0
            res['melds'] = []
        else:
            res['count'] = 1
            res['melds'] = [[tile, tile, tile, tile]]
        return res

    def can_ankan(self, tile):
        pass

    def can_win(self):
        pass

    def can_riichi(slef):
        pass
    
    @property
    def is_tenpai(self):
        return False
