from http.client import NOT_IMPLEMENTED
import random
from Player import Player
from MahjongKit.MahjongKit import *


class FullGame():
    # round_number = 0
    game_table = None
    # players = []
    round = None
    game = 1
    repeat_counter = 0
    wind = 0
    reach_sticks = 0
    honba_sticks = 0
    player_count = 4

    def __init__(self, player_count):
        self.round_number = 0
        self.game_table = GameTable()
        # tmp_players = players
        tmp_players = [Player(self.game_table) for i in range(player_count)]
        for i in range(player_count):
            tmp_players[i].set_seat(i)
        random.shuffle(tmp_players)
        self.players = tmp_players
        # self.round = Round(player_count, tmp_players, 0, 0, 0, 0,0,0)

    def game_start(self):
        while (self.wind != 1 and self.game != 5):
            # self.round_number += 1
            self.round = Round(self.player_count, self.players,
                               self.wind, self.game, self.repeat_counter, self.reach_sticks, self.honba_sticks)
            self.round.start()
            end_status = self.round.round_end()
            self.wind = end_status['wind']
            self.game = end_status['game']
            self.repeat_counter = end_status['repeat_counter']
            self.reach_sticks = end_status['reach_sticks']
            self.honba_sticks = end_status['honba_sticks']

    def start_round(self):
        self.round.start()

    @property
    def players_getter(self):
        return self.round.players

    @property
    def player_count_getter(self):
        return self.round.player_count

    @property
    def round_number_getter(self):
        return self.round_number

    @property
    def game_table_getter(self):
        return self.round.game_table


class Round():

    dealer = 0
    players = None
    player_count = 0
    reach_sticks = 0
    honba_sticks = 0
    wind = 0
    repeat_counter = 0
    game = 0
    ending_status = None

    def __init__(self, player_count, players, wind, game, repeat_counter, reach_sticks, honba_sticks):
        self.player_count = player_count
        self.players = players
        # self.dealer = round_number % player_count
        self.wind = wind
        self.game = game
        self.repeat_counter = repeat_counter
        self.reach_sticks = reach_sticks
        self.honba_sticks = honba_sticks
        self.game_table = GameTable(reach_sticks, honba_sticks)
        for player in self.players:
            player.init_tiles(self.game_table.draw_tile(13))

    # round post last tile to players
    # get their responds
    # chose one to proceed (win > pon/kan > chi > none)
    # draw to player if need draw
    # get discard tile and repeat

    def start(self):
        turn = self.game-1
        is_win = False
        is_over = False
        while (not self.game_table.no_tile_left() and not is_win and not is_over):
            draw = self.game_table.draw_tile()
            self.players[turn].draw_tile(draw)
            discard = self.players[turn].discard_tile()
            print(
                f"Player {turn}, Draw {draw:2}, discard {discard:2}, ", end='')
            print("Tile:", ' '.join(Tile.t34_to_grf(self.players[turn].tiles)))
        # self.game_table.append_revealed_tile(turn, discard)
        # action: [int:discard]
        # currently need: discard, action_player, need_draw
            actions = [self.players[i].can_action(
                discard, turn) for i in range(self.player_count)]  # player draw func
            who_pon = -1
            who_kan = -1
            who_chi = -1
            for i in range(self.player_count):
                if actions[i]['type'] == 'pon':
                    who_pon = i
                if actions[i]['type'] == 'minkan':
                    who_kan = i
                if actions[i]['type'] == 'chi':
                    who_chi = i
            if who_kan != -1:
                self.players[who_kan].kan_tile(discard, turn)
                turn = who_kan
                continue
            if who_pon != -1:
                self.players[who_pon].pon_tile(discard, turn)
                turn = who_pon
                continue
            if who_chi != -1:
                self.players[who_chi].chi_tile(discard, turn)
                turn = who_chi
                continue

            # while (action[0] != -1):
            #     discard = action[0]
            #     turn = action[1]

            #     # get actions from players
            #     actions = [None for i in self.player_count]
            #     for id, player in enumerate(self.players):
            #         if (id != turn):
            #             # player action function (how do the player handle the tile)
            #             actions[id] = player.action(discard, turn)

            #     # somehow get the right action
            #     action = actions[0]

            #     # if need_draw
            #     if (action[2]):
            #         action = self.players[turn].draw(draw)

            turn = (turn + 1) % self.player_count
        self.is_win = 0
        self.is_over = 1
        self.who_win = -1
        self.win_from_who = -1
        # self.round_end(0, 0)

    def round_end(self):
        if not self.is_win and self.is_over:
            self.honba_sticks += 1
            self.repeat_counter += 1
            if not self.players[self.game-1].is_tenpai:
                self.game = (self.game + 1)
                if self.game == 5 and self.wind != 1:
                    self.wind = (self.wind + 1)
                    self.game = 0
            ending_status = {"status": "exhaustive", "wind":  self.wind,
                             "game": self.game, "repeat_counter": self.repeat_counter, "honba_sticks": self.honba_sticks, "reach_sticks": self.reach_sticks}
        else:
            if self.who_win == self.game:
                self.repeat_counter += 1
                self.honba_sticks += 1
                self.reach_sticks = 0
            else:
                self.repeat_counter = 0
                self.honba_sticks = 0
                self.reach_sticks = 0
                self.game = (self.game + 1)
                if self.game == 5 and self.wind != 1:
                    self.wind = (self.wind + 1)
                    self.game = 1
            ending_status = {"status": "Win", "is_zumo": self.is_zumo,
                             "win_player": self.who_win, "win_from_who": self.win_from_who, "wind":  self.wind, "game": self.game, "repeat_counter": self.repeat_counter, "honba_sticks": self.honba_sticks, "reach_sticks": self.reach_sticks}
            # WIP probably merge into round class
        return ending_status


class GameTable():

    bonus_indicators = None
    remaining_count = 0
    revealed_tiles = None
    tiles = None
    reach_sticks = 0
    honba_sticks = 0

    def __init__(self, reach_sticks=0, honba_sticks=0):
        self.tiles = [i for j in range(4) for i in range(34)]
        self.tiles[4] = 34
        self.tiles[13] = 35
        self.tiles[22] = 36
        random.shuffle(self.tiles)
        # add -1 at the end of tiles, to prevent index error
        self.tiles.append(-1)
        self.bonus_indicators = [self.tiles[9]]
        self.remaining_count = 136
        self.revealed_tiles = [[] for i in range(4)]
        self.reach_sticks = reach_sticks
        self.honba_sticks = honba_sticks

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
        self.revealed_tiles[player].append(tile)


if __name__ == '__main__':
    game = FullGame(4)
    game.game_start()
    print("Game over")
