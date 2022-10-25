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

    def get_shantin(self, new_tile=None, new_meld=[]):
        tmp_tiles = self.tiles
        tmp_melds = self.open_melds
        if (new_tile != None):
            tmp_tiles.append(new_tile)
            for i in new_meld:
                tmp_tiles.remove(i)
            tmp_melds.append(new_meld)
        bonus_chr = filter(
            lambda f: f in [self.wind+27, self.seat+27, 31, 32, 33], tmp_tiles)
        return Partition.shantin_multiple_forms(tmp_tiles, tmp_melds, bonus_chr)

    '''
    action notes:
    (these need last tile from another)
        win:
        chaken:
        chi:          discard
        pon:          discard,                          change_turn
        minkon: draw, discard, check_stale, open_bonus, change_turn

    (these need to draw a tile first)
        zimo:
        ankon:  draw, discard, check_stale, open_bonus, change_turn
        riicih:       discard, check_stale
        none:         discard
    '''
    # return int

    def do_action(self, action):
        print(action)
        self.open_melds.append(action['meld'])
        self.tiles.append(action['tile'])
        print(self.tiles)
        for tile in action['meld']:
            self.tiles.remove(tile)
        # return self.discard_tile()

    # return {'type':str, 'player':int, 'tile':int, 'meld':[int, int, int]}
    def can_action(self, tile, from_player):
        no_action = {'type': 'dont_call'}
        if self.can_chi(tile, from_player):
            return self.can_chi(tile, from_player)[0]
        if self.can_pon(tile):
            return self.can_pon(tile)[0]
        return no_action
        actions = self.can_chi(tile, from_player) + \
            self.can_pon(tile) + [no_action]
        return actions[0]

    # return [{'type':str, 'player':int, 'tile':int, 'meld':[int, int, int]}]
    def can_chi(self, tile, from_player):
        if ((self.seat - from_player) % 4 == 1):
            melds = []
            for parts in Partition.partition(self.tiles):
                for part in parts:
                    # put part with 2 different tiles in melds
                    if (len(part) == 2 and (part[0] != part[1]) and (part not in melds)):
                        melds.append(part)
            # check every part + tile is in chow
            melds = list(filter(lambda x: (
                sorted(x+[tile]) in Tile.index_to_chow), melds))
            if (len(melds) > 0):
                ress = []
                for meld in melds:
                    ress.append({'type': 'chi', 'player': self.seat,
                                'tile': tile, 'meld': sorted(meld+[tile])})
                return ress
        return []

    # return [{'type':str, 'player':int, 'tile':int, 'meld':[int, int, int, int]}]
    def can_pon(self, tile):
        if (self.tiles.count(tile) == 2):
            res = dict()
            res['type'] = 'pon'
            res['player'] = self.seat
            res['tile'] = tile
            res['meld'] = [tile, tile, tile]
            return [res]
        return []

    # return [{'type':str, 'player':int, 'tile':int, 'meld':[meld]}]
    def can_minkan(self, tile):
        if (self.tiles.count(tile) == 3):
            res = dict()
            res['type'] = 'minkan'
            res['player'] = self.seat
            res['tile'] = tile
            res['meld'] = [tile, tile, tile, tile]
            return [res]
        return []

    def can_ankan(self, tile):
        pass

    def can_win(self):
        pass

    def can_riichi(slef):
        pass

    @ property
    def is_tenpai(self):
        return False
