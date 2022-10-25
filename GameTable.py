import random
from MahjongKit.MahjongKit import Tile
from MahjongKit.MahjongKit import Meld
from Player import Player


class GameTable():

    players = None
    dealer_set = 0
    bonus_indicator = None
    mount_indicator = 0
    round_number = 0
    reach_sticks = 0
    honba_sticks = 0
    count_players = 4
    count_remaining_tiles = 0
    revealed_tiles = None
    tiles_mount = None
    wind = 0

    def __init__(self, player_count):
        random.seed()
        winds = [i for i in range(player_count)]
        # opponents = [MahjongAgent.MahjongAgent(
        #     self) for i in range(player_count-1)]
        random.shuffle(winds)
        # self.players = [ai_obj] + opponents
        self.players = [Player(self) for i in range(player_count)]
        for i in range(player_count):
            self.players[i].set_seat(i)
        self.count_players = player_count
        self.revealed_tiles = []
        self.round_number = 0
        self.reach_sticks = 0
        self.honba_sticks = 0
        self.dealer_seat = 0

    def init_mount(self):
        self.tiles_mount = [i for j in range(4) for i in range(34)]
        self.tiles_mount[4] = 34
        self.tiles_mount[13] = 35
        self.tiles_mount[22] = 36  # red dora
        random.shuffle(self.tiles_mount)
        self.bonus_indicator = [self.tiles_mount[130]]
        self.count_remaining_tiles = 136

    def init_round(self):
        self.round_number += 1
        self.revealed_tiles = [self.bonus_indicator[0]]
        self.init_mount()
        for id, player in enumerate(self.players):
            player.init_tiles(self.tiles_mount[13*id:13*(id+1)])
        self.mount_indicator = 13*self.count_players
        self.count_remaining_tiles = 70

    def round_start(self):
        self.init_round()
        for i in range(self.count_players):
            self.players[i].set_wind(self.wind)
        while (self.count_remaining_tiles != 0):
            pass
            # self.dealer_set += 1


if __name__ == '__main__':
    game = GameTable(4)
