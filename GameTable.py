import random
from MahjongKit.MahjongKit import Tile
from MahjongKit.MahjongKit import Meld


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

    def __init__(self, ai_obj, oppenents, player_count):
        random.seed()
        winds = [i for i in range(player_count)]
        random.shuffle(winds)
        self.players = [ai_obj] + oppenents
        for i in range(player_count):
            self.players[i].set_seat(winds[i])
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

    def round_start(self):
        self.init_round()
        self.dealer_set += 1
        order = [player for player in self.players if player.seat ==
                 self.dealer_set % self.count_players]
        while self.mount_indicator != 122:
            for player in order:
                player.draw_tile(self.tiles_mount[self.mount_indicator])
                self.mount_indicator += 1
