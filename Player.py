from MahjongKit.MahjongKit import Tile, Meld, Partition, WinWaitCal
import random


class Player:
    wind = 0
    seat = 0
    tiles = []
    discard_tiles = []
    points = 0
    gameboard = None
    open_melds = []
    ankan = []
    minkan = []
    riichi_status = False

    def __init__(self, gameboard):
        self.tiles = []
        self.discard_tiles = []
        self.points = 25000
        self.gameboard = gameboard
        self.open_melds = []
        self.ankan = []
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
        tile = self.tiles[random.randint(0, len(self.tiles)-1)]
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

    def do_discard_action(self, discard_action):
        # print(discard_action)
        if (discard_action['type'] == 'chi' or discard_action['type'] == 'pon'):
            self.open_melds.append(discard_action['meld'])
        elif discard_action['type'] == 'minkan':
            self.minkan.append(discard_action['meld'])
        # self.open_melds.append(discard_action['meld'])
        self.tiles.append(discard_action['tile'])
        # print(self.tiles)
        for tile in discard_action['meld']:
            self.tiles.remove(tile)

    '''
    CATJAM READS THIS
    discard_action dict contain:
        type:       str (win, chi, pon, minkan, draw, none)
        player:     int (player who do the action)
        from:       int (discard tile form the player)
        tile:       int (discard tile)
        meld:       [int, int, int] (for chi, pon, minkan) ([] if win, draw, none)
        need_draw:  bool (True if draw, minkan)
    '''

    def can_discard_action(self, tile, from_player):
        discard_actions = []
        discard_actions += self.can_pon(tile, from_player)
        discard_actions += self.can_chi(tile, from_player)[0] if len(
            self.can_chi(tile, from_player)) > 0 else []
        discard_actions += self.can_minkan(tile, from_player)
        discard_actions += self.can_draw(tile, from_player)
        return discard_actions[random.randint(0, len(discard_actions)-1)]

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
                    ress.append([{'type': 'chi', 'player': self.seat, 'from': from_player, 'tile': tile,
                                'meld': sorted(meld+[tile]), 'need_draw': False}])
                return ress
        return []

    def can_pon(self, tile, from_player):
        if (self.tiles.count(tile) >= 2):
            return [{'type': 'pon', 'player': self.seat, 'from': from_player, 'tile': tile,
                    'meld': [tile, tile, tile], 'need_draw':False}]
        return []

    def can_minkan(self, tile, from_player):
        if (self.tiles.count(tile) == 3):
            return [{'type': 'minkan', 'player': self.seat, 'from': from_player, 'tile': tile,
                    'meld': [tile, tile, tile, tile], 'need_draw':False}]
        return []

    def can_draw(self, tile, from_player):
        if ((self.seat - from_player) % 4 == 1):
            return [{'type': 'draw', 'player': self.seat, 'from': from_player, 'tile': tile,
                    'meld': [], 'need_draw':True}]
        return [{'type': 'none', 'player': self.seat, 'from': from_player, 'tile': tile,
                'meld': [], 'need_draw':False}]

    def can_ankan(self, tile):
        pass

    def can_win(self):
        pass

    def can_riichi(slef):
        pass

    @ property
    def is_tenpai(self):
        return False
#[{'type': 'pon', 'player': 3, 'from': 1, 'tile': 17, 'meld': [17, 17, 17], 'need_draw': False}, {'type': 'minkan', 'player': 3, 'from': 1, 'tile': 17, 'meld': [17, 17, 17, 17], 'need_draw': False}, {'type': 'none', 'player': 3, 'from': 1, 'tile': 17, 'meld': [], 'need_draw': False}]
# [{'type': 'pon', 'player': 1, 'from': 2, 'tile': 23, 'meld': [23, 23, 23], 'need_draw': False}, {'type': 'minkan', 'player': 1, 'from': 2, 'tile': 23, 'meld': [23, 23, 23, 23], 'need_draw': False}, {'type': 'none', 'player': 1, 'from': 2, 'tile': 23, 'meld': [], 'need_draw': False}]
