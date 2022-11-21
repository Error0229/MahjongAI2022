import MahjongKit as mjk
import numpy as np
from copy import deepcopy as dcp

""" States in 34 form
hand                                            : 1 * [4 * 34] V
all reveal tiles                                : 1 * [4 * 34] V
self discard tiles in order                     : 1 * [20巡 * 34] V
self score                                      : 1 * [1 * 34]
self reach status                               : 1 * [1 * 34] V
opponent left, right, across open hend          : 3 * [4 * 34] V
opponents discard tiles in order                : 3 * [20巡 * 34] V
opponent left, right, opposite score            : 3 * [1 * 34]
opponents reach status                          : 3 * [1 * 34] V
doras                                           : 1 * [4 * 34] V
Round wind                                      : 1 * [1 * 34] V
self wind                                       : 1 * [1 * 34] V
opponents wind                                  : 3 * [1 * 34] V
we don't consider about red fives
score calculation => score / 50000 * 34
"""


class TrainingData:
    @property
    def base_state(self):
        return [0 for _ in range(34)]

    @property
    def full_state(self):
        return [1 for _ in range(34)]

    class GameState:
        @property
        def base_state(self):
            return [0 for _ in range(34)]

        @property
        def full_state(self):
            return [1 for _ in range(34)]
        # base_state = list(0 for i in range(34))
        # full_state = list(1 for i in range(34))

        def __init__(self):
            self.action = ""
            self.expect_chow = [self.base_state]
            self.expect_reach = [self.base_state]
            self.expect_minkan = [self.base_state]
            self.expect_pon = [self.base_state]
            self.expect_discard = [self.base_state]
            self.score = 25000
            self.open_melds = [self.base_state for _ in range(4)]
            self.hand = [self.base_state for _ in range(4)]
            self.all_reveal_tiles = [self.base_state for _ in range(4)]
            self.self_discard_tiles = [self.base_state for _ in range(20)]
            self.opponents_discard_tiles = [
                [self.base_state for _ in range(20)] for _ in range(3)]
            self.opponents_open_hand = [
                [self.base_state for _ in range(4)] for _ in range(3)]
            self.reach_status = [self.base_state]
            self.opponents_reach_status = [self.base_state for _ in range(3)]
            self.doras = [self.base_state for _ in range(4)]
            self.self_score = [self.base_state]
            self.opponents_score = [self.base_state for _ in range(3)]
            self.round_wind = [self.base_state]
            self.self_wind = [self.base_state]
            self.opponents_wind = [self.base_state for _ in range(3)]
            self.player_wind = -1
            self.discard34 = []
            self.hand34 = []
            self.meld34 = []
            self.minkan34 = []
            self.ankan34 = []

    def __init__(self):
        self.player_names = []
        self.dan = {}
        self.wind_to_id = {}
        self.States = [TrainingData.GameState(), TrainingData.GameState(
        ), TrainingData.GameState(), TrainingData.GameState()]

    def process_player_states(self, player_state: mjk.PreProcessing.PlayerState, next_state):
        if (player_state.a_action == None):
            return
        if player_state.a_action['type'] == 'init_hand' and player_state.name not in self.player_names:
            self.player_names.append(player_state.name)
            print(self.player_names)
            player_id = self.player_names.index(player_state.name)
            self.dan[player_state.name] = player_state.dan
            self.player_wind = player_state.s_player_wind
            self.wind_to_id[player_state.s_player_wind] = self.player_names.index(
                player_state.name)
            self.set_tile(self.States[player_id].self_wind,
                          player_state.s_player_wind)
            # set self wind
            self.set_tile(
                self.States[player_id].round_wind, player_state.s_round_wind)
            self.discard34 = player_state.s_discard34
            self.hand34 = player_state.s_hand34
            self.meld34 = player_state.s_meld34
            print('init_done')
            # set round wind
            return
        player_index = self.player_names.index(player_state.name)
        self.set_hand(player_index, player_state.s_hand34)
        self.set_melds_to_hand(player_index, player_state.s_meld34)
        self.set_minkan_to_hand(player_index, player_state.s_minkan)
        self.set_ankan_to_hand(player_index, player_state.s_ankan)
        self.set_reveal_tiles(player_index, player_state.s_revealed)
        self.set_discard_tiles(player_index, player_state.s_discard34)
        self.set_reach_status(player_index, player_state.s_reach)
        self.set_doras(player_index, player_state.s_bonus_tiles_34)
        self.set_self_score(player_index, player_state.score)
        self.States[player_index].score = player_state.score
        self.hand34 = player_state.s_hand34
        self.meld34 = player_state.s_meld34
        # opponent parts need to know the wind relation
        for i in range(3):
            next_p = player_state.s_player_wind + i + 1
            next_p = next_p - 4 if next_p > mjk.Tile.NORTH else next_p
            opp_id = self.wind_to_id.get(next_p, -1)
            if opp_id != -1:
                self.set_opp_open_hand(player_index, i, opp_id)
                self.set_opp_discards(player_index, i, opp_id)
                self.set_opp_wind(player_index, i, opp_id)
                self.set_opp_reach_status(player_index, i, opp_id)
                self.set_opp_score(player_index, i, opp_id)
        Action = player_state.a_action
        if Action == None:
            return
        self.States[player_index].action = Action['type']

        if (Action['type'] == 'drop' and self.dan == '天鳳'):
            self.set_tile(
                self.States[player_index].expect_discard, Action['tile'])
            self.dump_discrd_data(self.States[player_index])
        if (Action['type'] == 'reach_drop' and self.dan == '天鳳'):
            self.States[player_index].expect_reach = [self.full_state]
            self.dump_reach_data(self.States[player_index])
        # check opponent's action
        if (player_state.a_result == None or player_state.a_action == None):
            return
        next_action = next_state.a_action['type']

        for i in range(3):
            next_p = player_state.s_player_wind + i + 1
            next_p = next_p - 4 if next_p > mjk.Tile.NORTH else next_p
            opp_id = self.wind_to_id.get(next_p, -1)
            if i == 0 and self.can_chow(self.States[opp_id]):
                if next_action == 'chow':
                    self.States[opp_id].expect_chow = [self.full_state]
                self.dump_chow_data(self.States[opp_id])
            elif self.can_pon(self.States[opp_id]):
                if next_action == 'pon' and opp_id == self.wind_to_id[next_state.s_player_wind]:
                    self.States[opp_id].expect_pon = [self.full_state]
                self.dump_pon_data(self.States[opp_id])
            elif self.can_kan(self.States[opp_id]):
                if next_action == 'minkan' and opp_id == self.wind_to_id[next_state.s_player_wind]:
                    self.States[opp_id].expect_minkan = [self.full_state]
                self.dump_minkan_data(self.States[opp_id])

    def can_chow(self, state):
        return False

    def can_pon(self, state):
        return False

    def can_kan(self, state):
        return False

    def set_hand(self, player_id, hand34):
        self.States[player_id].hand = [self.base_state for _ in range(4)]
        for tile in hand34:
            self.set_tile(self.States[player_id].hand, tile)

    def set_melds_to_hand(self, player_id, melds):
        for meld in melds:
            for tile in meld:
                self.set_tile(self.States[player_id].hand, tile)

    def set_minkan_to_hand(self, player_id, minkans):
        for minkan in minkans:
            for tile in minkan:
                self.set_tile(self.States[player_id].hand, tile)

    def set_ankan_to_hand(self, player_id, ankans):
        for ankan in ankans:
            for tile in ankan:
                self.set_tile(self.States[player_id].hand, tile)

    def set_reveal_tiles(self, player_id, revealed):
        self.States[player_id].all_reveal_tiles = [
            self.base_state for _ in range(4)]
        for tile in range(34):
            for _ in range(revealed[tile]):
                self.set_tile(
                    self.States[player_id].all_reveal_tiles, tile)

    def set_discard_tiles(self, player_id, discard_34):
        self.States[player_id].self_discard_tiles = [
            self.base_state for _ in range(20)]
        for turn in range(len(discard_34)):
            self.set_single_tile(
                self.States[player_id].self_discard_tiles[turn], discard_34[turn])

    def set_reach_status(self, player_id, reach):
        if reach:
            self.States[player_id].reach_status = [self.full_state]

    def set_opp_open_hand(self, player_id, seat, opp_id):
        self.States[player_id].opponents_open_hand[seat] = [
            self.base_state for _ in range(4)]
        for meld in self.States[opp_id].meld34:
            for tile in meld:
                self.set_tile(
                    self.States[player_id].opponents_open_hand[seat], tile)
        for ankan in self.States[opp_id].ankan34:
            for tile in ankan:
                self.set_tile(
                    self.States[player_id].opponents_open_hand[seat], tile)
        for minkan in self.States[opp_id].minkan34:
            for tile in minkan:
                self.set_tile(
                    self.States[player_id].opponents_open_hand[seat], tile)

    def set_opp_discards(self, player_id, seat, opp_id):
        self.States[player_id].opponents_discard_tiles[seat] = [
            self.base_state for _ in range(20)]
        for turn in range(len(self.States[opp_id].discard34)):
            self.set_tile(
                self.States[player_id].opponents_discard_tiles[seat][turn], self.States[opp_id].discard34[turn])

    def set_opp_wind(self, player_id, seat, opp_id):
        self.set_single_tile(self.States[player_id].opponents_wind[seat],
                             self.States[opp_id].player_wind)

    def set_opp_reach_status(self, player_id, seat, opp_id):
        if self.States[opp_id].reach_status:
            self.States[player_id].opponents_reach_status[seat] = self.full_state

    def set_doras(self, player_id, dora_indicators):
        self.States[player_id].doras = [self.base_state for _ in range(4)]
        for tile in dora_indicators:
            self.set_tile(self.States[player_id].doras, tile)

    def set_self_score(self, player_id, score):
        score34 = int(score/50000 * 34)
        self.States[player_id].self_score = [[1 for i in range(
            score34)] + [0 for i in range(34 - score34)]]

    def set_opp_score(self, player_id, seat, opp_id):
        score34 = int(self.States[opp_id].score/50000 * 33)
        if score34 >= 34:
            score34 = 33
        self.States[player_id].opponents_score[seat] = [[
            1 for i in range(score34)] + [0 for i in range(34 - score34)]]

    def set_single_tile(self, table, tile):
        table[tile] = 1

    def set_tile(self, table, tile):

        for i in range(4):
            # print(i, tile)
            # print(table)
            if table[i][tile] == 0:
                table[i][tile] = 1
                # print('set_tile')
                break
        # print('end_for')

    def is_next(self, player_id, opp_id):
        return True if opp_id - player_id == (1 or 3) else False

    def dump_discard_data(self, game_state: GameState):

        pass

    def dump_chow_data(self, game_state: GameState):

        pass

    def dump_pon_data(self, game_state: GameState):

        pass

    def dump_minkan_data(self, game_state: GameState):

        pass

    def dump_reach_data(self, game_state: GameState):

        pass

    def append_state(self, state):
        self.States.append(state)

    def log_to_training_data(self):
        datas = mjk.PreProcessing.process_one_log(log)

        for round_num, actions in datas.items():
            print(f"Round {round_num}")
            for action in actions:
                self.process_player_states(action)


if __name__ == '__main__':
    glc = mjk.GameLogCrawler()
    glc.db_show_tables()
    gene = glc.db_get_logs_where_players_lv_gr(19)
    log = next(gene)
    # print(log)
    td = TrainingData()
    result = mjk.PreProcessing.process_one_log(log)
    present_state = None
    for k, v in result.items():
        print(f"Round {k}")
        # if k > 1:
        #     break
        ft = True
        for state in v:
            if ft:
                ft = False
                present_state = state
                continue
            td.process_player_states(present_state, state)
            print(state)
            present_state = state
