from http.client import NOT_IMPLEMENTED
import random
from Player import Player, Model_port
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
        tmp_players[0] = Model_port(self.game_table)
        for i in range(player_count):
            tmp_players[i].set_seat(i)
            tmp_players[i].set_wind(i)
        # random.shuffle(tmp_players)
        self.players = tmp_players
        # self.round = Round(player_count, tmp_players, 0, 0, 0, 0,0,0)

    def game_start(self):
        while (not (self.wind == 1 and self.game == 5)):
            # self.round_number += 1
            self.game_table.set_game_table(
                self.wind, self.game, self.honba_sticks, self.reach_sticks)
            self.round = Round(self.game_table, self.player_count, self.players,
                               self.wind, self.game, self.repeat_counter, self.reach_sticks, self.honba_sticks)
            for player in self.players:
                player.is_riichi = False
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

    def __init__(self, Game_table, player_count, players, wind, game, repeat_counter, reach_sticks, honba_sticks):
        self.player_count = player_count
        self.players = players
        # self.dealer = round_number % player_count
        self.wind = wind
        self.game = game
        self.repeat_counter = repeat_counter
        self.reach_sticks = reach_sticks
        self.honba_sticks = honba_sticks
        self.game_table = Game_table
        for player in self.players:
            player.init_tiles(self.game_table.draw_tile(13))
            player.open_melds = []
            player.ankan = []
            player.minkan = []

    # round post last tile to players
    # get their responds
    # chose one to proceed (win > pon/kan > chi > none)
    # draw to player if need draw
    # get discard tile and repeat

    def start(self):
        print(
            f'Round Start\nwind : {self.wind}, game : {self.game}, dora : {Tile.t34_to_grf(Tile.ind_to_bonus_dic[self.game_table.bonus_indicators[0]])}')
        print('>'*50)
        turn = self.game-1
        is_win = False
        is_over = False
        need_draw = True
        while (not self.game_table.no_tile_left() and not is_win and not is_over):
            draw = None
            if need_draw:
                draw = self.game_table.draw_tile()
                action = self.players[turn].can_draw_action(draw)

                if(action['type'] == 'zimo'):
                    self.process_zimo(action)
                    self.who_win = turn
                    self.is_win = True
                    self.is_zimo = True
                    self.win_from_who = turn
                    return
                elif(action['type'] == 'ankan'):
                    self.players[turn].draw_tile(draw)
                    continue
                elif(action['type'] == 'riichi'):
                    self.players[turn].do_draw_action(action)
                    self.players[turn].draw_tile(draw)
                    draw = action['to_discard']
                    self.game_table.riichi_status[turn] = True
                else:
                    self.players[turn].draw_tile(draw)
                    
            discard = self.players[turn].discard_tile(draw)
            

            actions = self.get_discard_action(discard, turn)
            if(actions[0]['type'] == 'win'):
                # process win
                self.process_win(actions)
                self.who_win = [action['player'] for action in actions]
                self.is_win = True
                self.is_zimo = False
                self.win_from_who = turn
                return
            else:
                # process discard action
                turn, need_draw = self.process_discard_action(actions[0])


        self.is_win = 0
        self.is_over = 1
        self.who_win = -1
        self.win_from_who = -1
        # self.round_end(0, 0)

    # choose a list discard actions
    def get_discard_action(self, discard, turn):
        dic = {'win': 5, 'minkan': 4, 'pon': 3, 'chi': 2, 'draw': 1, 'none': 0}
        res = [self.players[0].can_discard_action(discard, turn)]
        for i in range(1, 4):
            action = self.players[i].can_discard_action(discard, turn)
            if(dic[action['type']] > dic[res[0]['type']]):
                res = [action]
            elif(dic[action['type']] == dic[res[0]['type']]):
                res += action
        return res

    # process minkan, chi, pon
    # return (turn, need_draw)
    def process_discard_action(self, action):
        if(action['type'] in ['minkan', 'pon', 'chi']):
            self.players[action['player']].do_discard_action(action)
            self.game_table.open_melds[action['player']] += Tile.convert_bonuses(action['meld'])
        else:
            self.game_table.discard_tile(action['player'], action['tile'])
        return (action['player'], action['need_draw'])

    def process_win(self, actions):
        for action in actions:
            player = action['player']
            from_player = action['from']
            tile = action['tile']
            win = self.players[player].get_score(
                tile, from_player, self.game-1 == player)
            print('win')
            print(
                f"Tile: {' '.join(Tile.t34_to_grf(self.players[player].tiles))}", end=' , ')
            print(
                f"Melds: {' '.join(Tile.t34_to_grf(self.players[player].open_melds))}", end=' , ')
            print(
                f"minkans: {' '.join(Tile.t34_to_grf(self.players[player].minkan))}")
            print(
                f'player:{player}, from:{from_player}, score:{win["score_desc"]}, tile:{Tile.t34_to_grf(tile)}')
            print(f'han: {win["han"]}, fu: {win["fu"]}')
            self.players[player].points += win['score']
            self.players[from_player].points -= win['score']
            self.game_table.points[player] += win['score']
            self.game_table.points[from_player] -= win['score']

    def process_zimo(self, action):
        other_players = [0, 1, 2, 3]
        player = other_players.pop(action['player'])
        tile = action['tile']
        dealer = self.game-1
        win = self.players[player].get_score(tile, player, dealer == player)
        print('zimo')
        print(
            f"Tile: {' '.join(Tile.t34_to_grf(self.players[player].tiles))}", end=' , ')
        print(
            f"Melds: {' '.join(Tile.t34_to_grf(self.players[player].open_melds))}", end=' , ')
        print(
            f"minkans: {' '.join(Tile.t34_to_grf(self.players[player].minkan))}")
        print(
            f'player:{player}, from:{player}, score:{win["score_desc"]}, tile:{Tile.t34_to_grf(tile)}')
        print(f'han: {win["han"]}, fu: {win["fu"]}')
        self.players[player].points += win['score']
        self.game_table.points[player] += win['score']
        for other_player in other_players:
            if(other_player == dealer):
                self.players[other_player].points -= win['zimo_lose']['dealer']
                self.game_table.points[other_player] -= win['zimo_lose']['dealer']
            else:
                self.players[other_player].points -= win['zimo_lose']['other']
                self.game_table.points[other_player] -= win['zimo_lose']['other']

    def round_end(self):
        if not self.is_win and self.is_over:
            print('liuju')
            for i in range(4):
                self.players[i].display()
            # self.game_table.display()
            # self.honba_sticks += 1
            self.repeat_counter += 1
            if not self.players[self.game-1].is_tenpai:
                self.game = (self.game + 1)
                if self.game == 5 and self.wind != 1:
                    self.wind = (self.wind + 1)
                    self.game = 1
                for player in self.players:
                    player.set_wind(player.seat + 1 - self.game if player.seat +
                                    1 - self.game >= 0 else player.seat +
                                    1 - self.game + 4)
                ending_status = {"status": "exhaustive", "wind":  self.wind,
                                 "game": self.game, "repeat_counter": self.repeat_counter, "honba_sticks": self.honba_sticks, "reach_sticks": self.reach_sticks}
        else:
            for i in range(4):
                self.players[i].display()
            # self.game_table.display()
            if self.who_win == self.game - 1:
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
                for player in self.players:
                    player.set_wind(player.seat + 1 - self.game if player.seat +
                                    1 - self.game >= 0 else player.seat +
                                    1 - self.game + 4)
            ending_status = {"status": "Win", "is_zimo": self.is_zimo,
                             "win_player": self.who_win, "win_from_who": self.win_from_who, "wind":  self.wind, "game": self.game, "repeat_counter": self.repeat_counter, "honba_sticks": self.honba_sticks, "reach_sticks": self.reach_sticks}

        print(f'Round End')
        print('<'*50)
        # self.players[0].gameboard.display()
        # print(*self.players[0].get_state(),sep='\n')
        return ending_status


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
        print(f'reach_sticks:{self.reach_sticks}, honba_sticks:{self.honba_sticks}')
        print(f'bonus_indicators:{Tile.t34_to_grf(self.bonus_indicators)}')
        #print(f'hidden_bonus_indicators:{Tile.t34_to_grf(self.hidden_bonus_indicators)}')
        for i in range(4):
            print(f'player:{i}, point:{self.points[i]}, riichi:{self.riichi_status[i]}')
            print(f'discard_tiles:{" ".join(Tile.t34_to_grf(self.discard_tiles[i]))}')
            print(f'open_meld:{" ".join(Tile.t34_to_grf(self.open_melds[i]))}')
        

if __name__ == '__main__':
    game = FullGame(4)
    game.game_start()
    print("Game over.")

'''
self discard tiles in order                     : 1 * [20巡 * 34] V
opponents discard tiles in order                : 3 * [20巡 * 34] V
'''