import random
from Game.Player import Player
from Game.ModelPort import ModelPort
from MahjongKit.MahjongKit import *
from Game.GameTable import GameTable


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
    shantin_records = []
    legal_discard_records = []
    
    def __init__(self, player_count):
        self.round_number = 0
        self.game_table = GameTable()
        # tmp_players = players
        tmp_players = [Player(self.game_table) for _ in range(player_count)]
        discard_cnn = 'discard_cnn_31_Final_10w_data_5conv31.h5'
        chow_cnn = 'chow_cnn_31_final_10w_data_4conv.h5'
        pon_cnn = 'pon_cnn_31_final_10w_data_4conv.h5'
        riichi_cnn = 'riichi_cnn_31_final_v2_10w_data_4conv.h5'
        tmp_players[0] = ModelPort(self.game_table, discard_cnn, chow_cnn, pon_cnn, riichi_cnn)
        #tmp_players[1] = ModelPort(self.game_table, discard_cnn, chow_cnn, pon_cnn, riichi_cnn)
        tmp_players[2] = ModelPort(self.game_table, discard_cnn, chow_cnn, pon_cnn, riichi_cnn)
        # stop bully CNN :(

        for i in range(player_count):
            tmp_players[i].set_seat(i)
            tmp_players[i].set_wind(i)
            tmp_players[i].set_round_wind(i)

        self.players = tmp_players
        self.game_log = {'rank': [], 'score': [], 'liuju_cnt':0, 'round_cnt':0}
        
    def game_start(self):
        while (not (self.wind == 1 and self.game == 5)):
            self.game_table.set_game_table(
                self.wind, self.game, self.honba_sticks, self.reach_sticks)
            self.round = Round(self.game_table, self.player_count, self.players,
                               self.wind, self.game, self.repeat_counter, self.reach_sticks, self.honba_sticks)
            self.round.start()
            # end of round
            end_status = self.round.round_end()
            self.wind = end_status['wind']
            self.game = end_status['game']
            self.repeat_counter = end_status['repeat_counter']
            self.reach_sticks = end_status['reach_sticks']
            self.honba_sticks = end_status['honba_sticks']
            
            for player in self.players:
                player.update_log_round_end(end_status)
            self.game_log['round_cnt'] += 1
            self.game_log['liuju_cnt'] += (end_status['status']=='exhaustive')

        # end of game
        player_scores = [(id, p.points) for id, p in enumerate(self.players)]
        rank_player_scores = sorted(player_scores, key=lambda x: -x[1])
        
        self.game_log['rank'] = [0, 0, 0, 0]
        self.game_log['score'] = [0, 0, 0, 0]
        for rank, (player_id, score) in enumerate(rank_player_scores):
            self.game_log['rank'][player_id] = rank + 1
            self.game_log['score'][player_id] = score

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

    def __init__(self, Game_table: GameTable, player_count, players: list[Player], wind, game, repeat_counter, reach_sticks, honba_sticks):
        self.player_count = player_count
        self.players = players
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

    def start(self):
        print('Round Start')
        #print(f'wind : {self.wind}, game : {self.game}, dora : {Tile.t34_to_grf(Tile.ind_to_bonus_dic[self.game_table.bonus_indicators[0]])}')
        # print('>'*50)
        print(f'wind : {self.wind}, game : {self.game}')
        for p in self.players:
            p.init_round()
        turn = self.game-1
        is_win = False
        is_over = False
        need_draw = True
        while (not self.game_table.no_tile_left() and not is_win and not is_over):
            draw = None
            if need_draw:
                draw = self.game_table.draw_tile()
                action = self.players[turn].can_draw_action(draw)

                if (action['type'] == 'zimo'):
                    self.process_zimo(action)
                    self.who_win = [turn]
                    self.is_win = True
                    self.is_zimo = True
                    self.win_from_who = turn
                    return
                elif (action['type'] == 'ankan'):
                    self.players[turn].draw_tile(draw)
                    continue
                elif (action['type'] == 'riichi'):
                    self.players[turn].do_draw_action(action)
                    self.players[turn].draw_tile(draw)
                    draw = action['to_discard']
                    self.game_table.riichi_status[turn] = True
                else:
                    self.players[turn].draw_tile(draw)

            discard = self.players[turn].discard_tile(draw)

            actions = self.get_discard_action(discard, turn)
            if (actions[0]['type'] == 'win'):
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
        self.who_win = []
        self.win_from_who = -1

    # choose a list discard actions
    def get_discard_action(self, discard, turn):
        dic = {'win': 5, 'minkan': 4, 'pon': 3, 'chi': 2, 'draw': 1, 'none': 0}
        res = [self.players[0].can_discard_action(discard, turn)]
        for i in range(1, 4):
            action = self.players[i].can_discard_action(discard, turn)
            if (dic[action['type']] > dic[res[0]['type']]):
                res = [action]
            elif (dic[action['type']] == dic[res[0]['type']]):
                res += [action]
        return res

    # process minkan, chi, pon
    def process_discard_action(self, action):
        if (action['type'] in ['minkan', 'pon', 'chi']):
            self.players[action['player']].do_discard_action(action)
            self.game_table.open_melds[action['player']
                                       ] += Tile.convert_bonuses(action['meld'])
            self.game_table.discard_tile(action['from'], action['tile'])
        else:
            self.game_table.discard_tile(action['from'], action['tile'])
        return (action['player'], action['need_draw'])

    def process_win(self, actions):
        for action in actions:
            player = action['player']
            from_player = action['from']
            tile = action['tile']
            win = self.players[player].get_score(
                tile, from_player, self.game-1 == player)
            # print('win')
            # print(
            #     f"Tile: {' '.join(Tile.t34_to_grf(self.players[player].tiles))}", end=' , ')
            # print(
            #     f"Melds: {' '.join(Tile.t34_to_grf(self.players[player].open_melds))}", end=' , ')
            # print(
            #     f"minkans: {' '.join(Tile.t34_to_grf(self.players[player].minkan))}")
            # print(
            #     f'player:{player}, from:{from_player}, score:{win["score_desc"]}, tile:{Tile.t34_to_grf(tile)}')
            # print(f'han: {win["han"]}, fu: {win["fu"]}')
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
        # print('zimo')
        # print(
        #     f"Tile: {' '.join(Tile.t34_to_grf(self.players[player].tiles))}", end=' , ')
        # print(
        #     f"Melds: {' '.join(Tile.t34_to_grf(self.players[player].open_melds))}", end=' , ')
        # print(
        #     f"minkans: {' '.join(Tile.t34_to_grf(self.players[player].minkan))}")
        # print(
        #     f'player:{player}, from:{player}, score:{win["score_desc"]}, tile:{Tile.t34_to_grf(tile)}')
        # print(f'han: {win["han"]}, fu: {win["fu"]}')
        self.players[player].points += win['score']
        self.game_table.points[player] += win['score']
        for other_player in other_players:
            if (other_player == dealer):
                self.players[other_player].points -= win['zimo_lose']['dealer']
                self.game_table.points[other_player] -= win['zimo_lose']['dealer']
            else:
                self.players[other_player].points -= win['zimo_lose']['other']
                self.game_table.points[other_player] -= win['zimo_lose']['other']

    def round_end(self):
        if not self.is_win and self.is_over:
            # print('liuju')
            # for i in range(4):
            #     self.players[i].display()
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
                    player.set_round_wind(self.wind)
            ending_status = {"status": "exhaustive", "wind":  self.wind,
                             "game": self.game, "repeat_counter": self.repeat_counter, "honba_sticks": self.honba_sticks, "reach_sticks": self.reach_sticks}
        else:
            # for i in range(4):
            #     self.players[i].display()
            # self.game_table.display()
            if self.game - 1 in self.who_win:
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
                    player.set_round_wind(self.wind)
            ending_status = {"status": "Win", "is_zimo": self.is_zimo,
                             "win_players": self.who_win, "win_from_who": self.win_from_who, "wind":  self.wind, "game": self.game, "repeat_counter": self.repeat_counter, "honba_sticks": self.honba_sticks, "reach_sticks": self.reach_sticks}

        print(f'Round End')
        # print('<'*50)
        # self.players[0].gameboard.display()
        # print(*self.players[0].get_state(),sep='\n')
        return ending_status
