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
        print(discard_action)
        self.open_melds.append(discard_action['meld'])
        self.tiles.append(discard_action['tile'])
        print(self.tiles)
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
        discard_actions = self.can_pon(tile, from_player) + self.can_chi(tile, from_player) + self.can_draw(tile, from_player)
        return discard_actions[0]

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
            melds = list(map(lambda x:sorted(x+[convert_tile]), melds))
            melds = list(filter(lambda x:(x in Tile.index_to_chow), melds))
            if (len(melds) > 0):
                ress = []
                for m in melds:
                    if((4 in m) and (34 in (self.tiles + [tile]))):
                        meld = [(34 if(t==4) else t) for t in m]    
                    elif((13 in m) and (35 in (self.tiles + [tile]))):
                        meld = [(35 if(t==13) else t) for t in m]
                    elif((22 in m) and (36 in (self.tiles + [tile]))):
                        meld = [(36 if(t==22) else t) for t in m]
                    else:
                        meld = m
                    ress.append({'type':'chi', 'player':self.seat, 'from':from_player,
                                 'tile':tile, 'meld':meld, 'need_draw':False})
                return ress
        return []

    def can_pon(self, tile, from_player):
        convert_hands = Tile.convert_bonus(self.tiles)
        convert_tile =  Tile.convert_bonus([tile])[0]
        if(convert_hands.count(convert_tile) >= 2):
            if((convert_tile== 4) and (34 in (self.tiles + [tile]))):
                meld = [4,4,34]
            elif((convert_tile==13) and (35 in (self.tiles + [tile]))):
                meld = [13,13,35]
            elif((convert_tile==22) and (36 in (self.tiles + [tile]))):
                meld = [22,22,36]
            else:
                meld = [tile, tile, tile]
            return [{'type':'pon', 'player':self.seat, 'from':from_player,
                     'tile':tile, 'meld':meld, 'need_draw':False}]
        return []

            

    def can_minkan(self, tile, from_player):
        convert_hands = Tile.convert_bonus(self.tiles)
        convert_tile =  Tile.convert_bonus([tile])[0]
        if(convert_hands.count(convert_tile) == 3):
            if((convert_tile== 4) and (34 in (self.tiles + [tile]))):
                meld = [4,4,4,34]
            elif((convert_tile==13) and (35 in (self.tiles + [tile]))):
                meld = [13,13,13,35]
            elif((convert_tile==22) and (36 in (self.tiles + [tile]))):
                meld = [22,22,22,36]
            else:
                meld = [tile, tile, tile, tile]
            return [{'type':'pon', 'player':self.seat, 'from':from_player,
                     'tile':tile, 'meld':meld, 'need_draw':False}]
        return []

    def can_draw(self, tile, from_player):
        if ((self.seat - from_player) % 4 == 1):
            return [{'type':'draw', 'player':self.seat, 'from':from_player, 'tile':tile, 
                    'meld':[], 'need_draw':True}]
        return [{'type':'none', 'player':self.seat, 'from':from_player, 'tile':tile, 
                'meld':[], 'need_draw':False}]

    def can_ankan(self, tile):
        pass

    def can_win(self):
        pass

    def can_riichi(slef):
        pass

    @ property
    def is_tenpai(self):
        return False
