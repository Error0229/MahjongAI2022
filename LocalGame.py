from http.client import NOT_IMPLEMENTED
import random
from Player import Player
from MahjongKit.MahjongKit import *


class FullGame():
    # round_number = 0
    game_table = None
    # players = []
    round = None

    def __init__(self, player_count, players):
        self.round_number = 0
        self.game_table = GameTable()
        # tmp_players = players
        tmp_players = [Player(self.game_table) for i in range(player_count)]
        for i in range(player_count):
            tmp_players[i].set_seat(i)
        random.shuffle(tmp_players)
        self.players = tmp_players
        self.round = Round(player_count, tmp_players, 0, 0, 0, 0)

    def game_start(self):
        while (self.round_number < 8):
            self.round_number += 1
            self.round = Round(self.round.player_count, self.round.players,
                               self.round.wind, self.round.ben, self.round.reach_sticks, self.round.honba_sticks)
            self.round.run()

    def start_round(self):
        self.round.run()

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
    ben = 0

    def __init__(self, player_count, players, wind, ben, reach_sticks, honba_sticks):
        self.player_count = player_count
        self.players = players
        # self.dealer = round_number % player_count
        self.wind = wind
        self.ben = ben
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

    def run(self):
        turn = self.wind
        is_win = False
        is_over = False
        while (not self.game_table.no_tile_left() and not is_win and not is_over):
            draw = self.game_table.draw_tile()
            self.players[turn].draw_tile(draw)
            discard = self.players[turn].discard_tile()
            print("Player " + str(turn) + ", Draw " +
                  str(draw) + ", discard " + str(discard)+", Tiles: "+' '.join(Tile.t34_to_grf(self.players[turn].tiles)))
            # self.game_table.append_revealed_tile(turn, discard)
        # action: [int:discard]
        # currently need: discard, action_player, need_draw
            action = self.players[turn].action()  # player draw func
            while (action[0] != -1):
                discard = action[0]
                turn = action[1]

                # get actions from players
                actions = [None for i in self.player_count]
                for id, player in enumerate(self.players):
                    if (id != turn):
                        # player action function (how do the player handle the tile)
                        actions[id] = player.action(discard, turn)

                # somehow get the right action
                action = actions[0]

                # if need_draw
                if (action[2]):
                    action = self.players[turn].draw(draw)
            turn = (turn + 1) % self.player_count


# WIP probably merge into round class
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
    game = FullGame(4, [])
    game.game_start()

    print("Game over")
