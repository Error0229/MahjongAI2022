from MahjongKit.MahjongKit import Tile
import random


class GameTable():

    wind = 0
    game = 0
    bonus_indicators = None
    hidden_bonus_indicators = None
    remaining_count = 0
    tiles = None
    reach_sticks = 0
    honba_sticks = 0
    points = [0, 0, 0, 0]
    riichi_status = [False, False, False, False]
    discard_tiles = None
    open_melds = None

    def __init__(self, wind=-1, game=-1, reach_sticks=0, honba_sticks=0):
        self.wind = wind
        self.game = game
        self.tiles = [i for j in range(4) for i in range(34)]
        self.tiles[4] = 34
        self.tiles[13] = 35
        self.tiles[22] = 36
        random.shuffle(self.tiles)
        # add -1 at the end of tiles, to prevent index error
        self.tiles.append(-1)
        self.bonus_indicators = [self.tiles[9]]
        self.hidden_bonus_indicators = [self.tiles[8]]
        self.remaining_count = 136
        self.revealed_tiles = [[] for i in range(4)]
        self.reach_sticks = reach_sticks
        self.honba_sticks = honba_sticks
        self.points = [25000, 25000, 25000, 25000]

    def set_game_table(self, wind=-1, game=-1, reach_sticks=0, honba_sticks=0):
        self.wind = wind
        self.game = game
        self.tiles = [i for j in range(4) for i in range(34)]
        self.tiles[4] = 34
        self.tiles[13] = 35
        self.tiles[22] = 36
        random.shuffle(self.tiles)
        # add -1 at the end of tiles, to prevent index error
        self.tiles.append(-1)
        self.bonus_indicators = [self.tiles[9]]
        self.hidden_bonus_indicators = [self.tiles[8]]
        self.remaining_count = 136
        self.reach_sticks = reach_sticks
        self.honba_sticks = honba_sticks
        self.riichi_status = [False, False, False, False]
        self.discard_tiles = [[] for i in range(4)]
        self.open_melds = [[] for i in range(4)]

    def draw_tile(self, num=1):
        '''
        pull out number of tiles
        return -1 if fail
        return int if pull 1 tile
        return list of int if pull multiple tiles
        '''
        if (self.no_tile_left(num)):
            return -1
        self.remaining_count -= num
        if (num == 1):
            return self.tiles[self.remaining_count]
        else:
            return self.tiles[self.remaining_count: self.remaining_count+num]

    def no_tile_left(self, num=1):
        return self.remaining_count-num < 14

    # def append_revealed_tile(self, player, tile):
    #     self.revealed_tiles[player].append(tile)

    def discard_tile(self, player, tile):
        self.discard_tiles[player].append(Tile.convert_bonus(tile))

    def display(self):
        print('----- GameTable info -----')
        print(f'wind:{self.wind}, game:{self.game}')
        print(
            f'reach_sticks:{self.reach_sticks}, honba_sticks:{self.honba_sticks}')
        print(f'bonus_indicators:{Tile.t34_to_grf(self.bonus_indicators)}')
        # print(f'hidden_bonus_indicators:{Tile.t34_to_grf(self.hidden_bonus_indicators)}')
        for i in range(4):
            print(
                f'player:{i}, point:{self.points[i]}, riichi:{self.riichi_status[i]}')
            print(
                f'discard_tiles:{" ".join(Tile.t34_to_grf(self.discard_tiles[i]))}')
            print(f'open_meld:{" ".join(Tile.t34_to_grf(self.open_melds[i]))}')
