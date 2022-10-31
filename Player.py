import enum
from tabnanny import check
from MahjongKit.MahjongKit import Tile, Meld, Partition, WinWaitCal
import random


class Player:
    wind = 0
    wind34 = 0
    seat = 0
    seat34 = 0
    tiles = []
    discard_tiles = []
    points = 0
    gameboard = None
    open_melds = []
    ankan = []
    minkan = []
    is_riichi = False

    def __init__(self, gameboard):
        self.tiles = []
        self.discard_tiles = []
        self.points = 25000
        self.gameboard = gameboard
        self.open_melds = []
        self.ankan = []
        self.is_status = False

    def init_tiles(self, tiles):
        self.tiles = tiles

    def set_seat(self, seat):
        self.seat = seat
        self.seat34 = seat + 27

    def set_wind(self, wind):
        self.wind = wind
        self.wind34 = wind + 27

    def init_round(self, tiles, wind):
        self.tiles = tiles
        self.wind = wind
        self.wind34 = wind + 27

    def discard_tile(self, tile=None):
        # tile = self.tiles[random.randint(0, len(self.tiles)-1)]
        tile = self.to_discard_tile()['tile']
        self.tiles.remove(tile)
        self.discard_tiles.append(tile)
        self.gameboard.discard_tile(self.seat, tile)
        return tile

    # return {'tile':int, 'shantin':dic}
    def to_discard_tile(self):
        res = None
        for id in range(len(self.tiles)):
            hand = [i for i in self.tiles]
            new_tile = hand.pop(id)
            check = {'tile': new_tile, 'shantin': self.get_shantin(hand)}
            if(res == None):
                res = check
            else:
                if(new_tile == res['tile']):
                    continue
                if(min(list(res['shantin'].values())[1::]) < min(list(check['shantin'].values())[1::])):
                    continue
                else:
                    res = check
        return res

    def draw_tile(self, tile):
        self.tiles.append(tile)
        self.tiles.sort()

    def get_shantin(self, new_tiles=None, new_meld=[]):
        if(new_tiles == None):
            hand = self.tiles
        else:
            hand = new_tiles
        melds = self.open_melds
        if(new_meld != []):
            melds.append(new_meld)
        bonus_chr = list(
            filter(lambda f: f in [self.wind+27, self.seat+27, 31, 32, 33], hand))
        return Partition.shantin_multiple_forms(hand, melds, bonus_chr)

    # only return list of tiles waiting
    def get_waiting(self, is_draw, is_dealer):
        hand = Tile.convert_bonus(self.tiles)
        bonus_tiles = []
        bonus_num = 0

        for i in self.tiles:
            if(i in [34, 35, 36]):
                # bonus_tiles.append(i)
                bonus_num += 1
        for i in self.gameboard.bonus_indicators:
            bonus_tiles.append(i)
        bonus_num = len([i for i in hand if i in bonus_tiles])
        waiting = WinWaitCal.waiting_calculation(hand, self.open_melds, self.minkan, self.ankan, is_draw, self.seat34, self.wind34,
                                                 self.is_riichi, bonus_num, bonus_tiles, self.gameboard.honba_sticks, self.gameboard.reach_sticks, is_dealer)
        return list(waiting.keys())
        # WinWaitCal.waiting_calculation(hand, melds, minkan, ankan, is_zimo, self.seat, self.wind, is_riichi, bonus_num, bonus_tiles, benchan, reach_stick, is_dealer)

    def get_score(self, tile, from_player, is_dealer):
        # WIP: currently only check red bonus tiles
        is_zimo = (from_player == self.seat)
        hand = Tile.convert_bonus(self.tiles)
        bonus_tiles = []
        bonus_num = 0
        for i in self.tiles:
            if(i in [34, 35, 36]):
                # bonus_tiles.append(i)
                bonus_num += 1
        for i in self.gameboard.bonus_indicators:
            bonus_tiles.append(i)
        if is_zimo:
            for i in self.gameboard.hidden_bonus_indicators:
                bonus_tiles.append(i)
        bonus_num = len([i for i in hand if i in bonus_tiles])
        win = WinWaitCal.score_calculation(hand, tile, self.open_melds, self.minkan, self.ankan, is_zimo, self.seat34, self.wind34,
                                           self.is_riichi, bonus_num, bonus_tiles, self.gameboard.honba_sticks, self.gameboard.reach_sticks, is_dealer)
        return win

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
        if(self.can_win(tile, from_player)):
            return {'type': 'win', 'need_draw': False}
        discard_actions = []
        discard_actions += self.can_pon(tile, from_player)
        discard_actions += self.can_chi(tile, from_player)
        discard_actions += self.can_minkan(tile, from_player)
        discard_actions += self.can_draw(tile, from_player)
        return discard_actions[random.randint(0, len(discard_actions)-1)]

    def can_chi(self, tile, from_player):
        if ((self.seat - from_player) % 4 == 1):
            melds = []
            convert_tile = Tile.convert_bonus([tile])[0]
            for parts in Partition.partition(self.tiles):
                for part in parts:
                    # put part with 2 different tiles in melds
                    if (len(part) == 2 and (part[0] != part[1]) and (part not in melds)):
                        melds.append(part)
            # complete every meld, and check if it is in the chow index
            melds = list(map(lambda x: sorted(x+[convert_tile]), melds))
            melds = list(filter(lambda x: (x in Tile.index_to_chow), melds))
            if (len(melds) > 0):
                ress = []
                for m in melds:
                    if ((4 in m) and (34 in (self.tiles + [tile]))):
                        meld = [(34 if (t == 4) else t) for t in m]
                    elif ((13 in m) and (35 in (self.tiles + [tile]))):
                        meld = [(35 if (t == 13) else t) for t in m]
                    elif ((22 in m) and (36 in (self.tiles + [tile]))):
                        meld = [(36 if (t == 22) else t) for t in m]
                    else:
                        meld = m
                    ress.append({'type': 'chi', 'player': self.seat, 'from': from_player,
                                 'tile': tile, 'meld': meld, 'need_draw': False})
                return ress
        return []

    def can_pon(self, tile, from_player):
        convert_hands = Tile.convert_bonus(self.tiles)
        convert_tile = Tile.convert_bonus([tile])[0]
        if (convert_hands.count(convert_tile) >= 2):
            if ((convert_tile == 4) and (34 in (self.tiles + [tile]))):
                meld = [4, 4, 34]
            elif ((convert_tile == 13) and (35 in (self.tiles + [tile]))):
                meld = [13, 13, 35]
            elif ((convert_tile == 22) and (36 in (self.tiles + [tile]))):
                meld = [22, 22, 36]
            else:
                meld = [tile, tile, tile]
            return [{'type': 'pon', 'player': self.seat, 'from': from_player,
                     'tile': tile, 'meld': meld, 'need_draw': False}]
        return []

    def can_minkan(self, tile, from_player):
        convert_hands = Tile.convert_bonus(self.tiles)
        convert_tile = Tile.convert_bonus([tile])[0]
        if (convert_hands.count(convert_tile) == 3):
            if ((convert_tile == 4) and (34 in (self.tiles + [tile]))):
                meld = [4, 4, 4, 34]
            elif ((convert_tile == 13) and (35 in (self.tiles + [tile]))):
                meld = [13, 13, 13, 35]
            elif ((convert_tile == 22) and (36 in (self.tiles + [tile]))):
                meld = [22, 22, 22, 36]
            else:
                meld = [tile, tile, tile, tile]
            return [{'type': 'minkan', 'player': self.seat, 'from': from_player,
                     'tile': tile, 'meld': meld, 'need_draw': True}]
        return []

    def can_draw(self, tile, from_player):
        if ((self.seat - from_player) % 4 == 1):
            return [{'type': 'draw', 'player': self.seat, 'from': from_player, 'tile': tile,
                    'meld': [], 'need_draw':True}]
        return [{'type': 'none', 'player': self.seat, 'from': from_player, 'tile': tile,
                'meld': [], 'need_draw':False}]

    def can_ankan(self, tile):
        pass

    # def get_waiting(self, is_draw):
    def can_win(self, tile, from_player):
        if(tile in self.get_waiting(from_player == self.seat, self.gameboard.game-1 == self.seat)):
            return True
        return False

    def can_riichi(slef):
        pass

    @ property
    def is_tenpai(self):
        return False
#[{'type': 'pon', 'player': 3, 'from': 1, 'tile': 17, 'meld': [17, 17, 17], 'need_draw': False}, {'type': 'minkan', 'player': 3, 'from': 1, 'tile': 17, 'meld': [17, 17, 17, 17], 'need_draw': False}, {'type': 'none', 'player': 3, 'from': 1, 'tile': 17, 'meld': [], 'need_draw': False}]
# [{'type': 'pon', 'player': 1, 'from': 2, 'tile': 23, 'meld': [23, 23, 23], 'need_draw': False}, {'type': 'minkan', 'player': 1, 'from': 2, 'tile': 23, 'meld': [23, 23, 23, 23], 'need_draw': False}, {'type': 'none', 'player': 1, 'from': 2, 'tile': 23, 'meld': [], 'need_draw': False}]
