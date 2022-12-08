import MahjongKit.MahjongKit as mjk
import pandas as pd
import multiprocessing as mp
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

        def init_score(self):
            self.score = 25000

        def __init__(self):
            self.init()
            self.init_score()

        def __str__(self):
            fl = False
            for i in range(4):
                fl = fl or self.hand[i] != self.base_state
            if not fl:
                return f'hand34 : {self.hand34}, hand : {self.hand}'
            else:
                return ""

        def init(self):
            self.action = ""
            self.expect_chow = [self.base_state]
            self.expect_reach = [self.base_state]
            self.expect_minkan = [self.base_state]
            self.expect_pon = [self.base_state]
            self.expect_discard = [self.base_state]
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
        self.discard_data = []
        self.pon_data = []
        self.chow_data = []
        self.minkan_data = []
        self.reach_data = []
        self.player_names = []
        self.dan = {}
        self.wind_to_id = {}
        self.States = [TrainingData.GameState(), TrainingData.GameState(
        ), TrainingData.GameState(), TrainingData.GameState()]

    def process_player_states(self, player_state: mjk.PreProcessing.PlayerState, next_state: mjk.PreProcessing.PlayerState):
        if (player_state.a_action == None):
            return
        if player_state.a_action['type'] == 'init_hand':
            if (player_state.name not in self.player_names):
                self.player_names.append(player_state.name)
                self.dan[player_state.name] = player_state.dan
            # print(self.player_names)
            player_id = self.player_names.index(player_state.name)
            self.States[player_id].init()
            self.States[player_id].player_wind = player_state.s_player_wind
            self.wind_to_id[player_state.s_player_wind] = self.player_names.index(
                player_state.name)
            self.set_tile(self.States[player_id].self_wind,
                          player_state.s_player_wind)
            # set self wind
            self.set_tile(
                self.States[player_id].round_wind, player_state.s_round_wind)
            self.States[player_id].discard34 = player_state.s_discard34
            self.States[player_id].hand34 = player_state.s_hand34
            self.set_hand(player_id, player_state.s_hand34)
            self.States[player_id].meld34 = player_state.s_meld34
            # print('init_done')
            # set round wind
            return
        self.open_melds = [self.base_state for _ in range(4)]
        player_index = self.player_names.index(player_state.name)
        self.set_hand(player_index, player_state.s_hand34)
        self.set_melds_to_open_hand(player_index, player_state.s_meld34)
        self.set_minkan_to_open_hand(player_index, player_state.s_minkan)
        self.set_ankan_to_open_hand(player_index, player_state.s_ankan)
        self.set_reveal_tiles(player_index, player_state.s_revealed)
        self.set_discard_tiles(player_index, player_state.s_discard34)
        self.set_reach_status(player_index, player_state.s_reach)
        self.set_doras(player_index, player_state.s_bonus_tiles_34)
        self.set_self_score(player_index, player_state.score)
        self.States[player_index].score = player_state.score
        self.States[player_index].hand34 = player_state.s_hand34
        self.States[player_index].meld34 = player_state.s_meld34
        self.States[player_index].discard34 = player_state.s_discard34
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
        is_tenhou = self.dan[player_state.name] == '天鳳' or self.dan[player_state.name] == '十段'

        if Action == None:
            return
        self.States[player_index].action = Action['type']
        if (Action['type'] == 'drop' and is_tenhou):
            self.States[player_index].expect_discard = [self.base_state]
            self.set_tile(
                self.States[player_index].expect_discard, Action['tile'])
            self.dump_discard_data(self.States[player_index])
        if (Action['type'] == 'reach_drop' and is_tenhou):
            self.States[player_index].expect_reach = [self.full_state]
            self.dump_reach_data(self.States[player_index])
        if (player_state.s_reach == False and self.can_reach(self.States[player_index]) and is_tenhou):
            self.dump_reach_data(self.States[player_index])
        # check opponent's action
        if (not ((player_state.a_result == None) ^ (player_state.a_action == None))):
            return
        if (not (Action['type'] == 'reach_drop' or Action['type'] == 'drop')):
            return
        else:
            self.States[player_index].hand34.remove(Action['tile'])
        tile = Action['tile']
        next_action = next_state.a_action
        if (next_action == None):
            return
        for i in range(3):
            next_p = player_state.s_player_wind + i + 1
            next_p = next_p - 4 if next_p > mjk.Tile.NORTH else next_p
            opp_id = self.wind_to_id.get(next_p, -1)
            if is_tenhou and i == 0 and self.can_chow(self.States[opp_id], tile):
                self.States[player_index].expect_chow = [self.base_state]
                # print(
                #     f'chow : from player {player_index}, opp player : {opp_id}, {self.States[opp_id].hand34}, {tile}')
                if next_action['type'] == 'chow':
                    self.States[opp_id].expect_chow = [self.full_state]
                self.dump_chow_data(self.States[opp_id])
            elif is_tenhou and self.can_pon(self.States[opp_id], tile):
                self.States[player_index].expect_pon = [self.base_state]
                # print(
                #     f'pon : from player {player_index}, opp player : {opp_id}, {self.States[opp_id].hand34}, {tile}')
                if next_action['type'] == 'pon' and opp_id == self.wind_to_id[next_state.s_player_wind]:
                    self.States[opp_id].expect_pon = [self.full_state]
                self.dump_pon_data(self.States[opp_id])
            elif is_tenhou and self.can_kan(self.States[opp_id], tile):
                self.States[player_index].expect_minkan = [self.base_state]
                if next_action['type'] == 'minkan' and opp_id == self.wind_to_id[next_state.s_player_wind]:
                    self.States[opp_id].expect_minkan = [self.full_state]
                self.dump_minkan_data(self.States[opp_id])

    def can_chow(self, state: GameState, drop):
        tile34 = state.hand34
        return mjk.Partition.can_chi(tile34, drop)

    def can_pon(self, state: GameState, drop):
        tile34 = state.hand34
        return mjk.Partition.can_pon(tile34, drop)

    def can_kan(self, state: GameState, drop):
        tile34 = state.hand34
        return mjk.Partition.can_minkan(tile34, drop)

    def can_reach(self, state: GameState):
        tile34 = state.hand34
        return mjk.Partition.can_riichi(tile34)

    def set_hand(self, player_id, hand34):
        self.States[player_id].hand = [self.base_state for _ in range(4)]
        for tile in hand34:
            self.set_tile(self.States[player_id].hand, tile)

    def set_melds_to_open_hand(self, player_id, melds):
        for meld in melds:
            for tile in meld:
                self.set_tile(self.States[player_id].open_melds, tile)

    def set_minkan_to_open_hand(self, player_id, minkans):
        for minkan in minkans:
            for tile in minkan:
                self.set_tile(self.States[player_id].open_melds, tile)

    def set_ankan_to_open_hand(self, player_id, ankans):
        for ankan in ankans:
            for tile in ankan:
                self.set_tile(self.States[player_id].open_melds, tile)

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
        for turn in range(min(len(discard_34), 20)):
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
        for turn in range(min(20, len(self.States[opp_id].discard34))):
            self.set_single_tile(
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
        self.States[player_id].opponents_score[seat] = [
            1 for _ in range(score34)] + [0 for _ in range(34 - score34)]

    def set_single_tile(self, table, tile):
        table[tile] = 1

    def set_tile(self, table, tile):
        for i in range(4):
            if table[i][tile] == 0:
                table[i][tile] = 1
                return

    def is_next(self, player_id, opp_id):
        return True if opp_id - player_id == (1 or 3) else False

    def states_to_bmp(self, gs: GameState):
        bmp = gs.hand+gs.open_melds  # bitmap
        for i in range(3):
            bmp += gs.opponents_open_hand[i]
        bmp += gs.self_discard_tiles
        for i in range(3):
            bmp += gs.opponents_discard_tiles[i]
        bmp += gs.all_reveal_tiles
        bmp += gs.reach_status
        bmp += gs.opponents_reach_status
        bmp += gs.doras
        bmp += gs.self_score
        bmp += gs.opponents_score
        bmp += gs.round_wind
        bmp += gs.self_wind
        bmp += gs.opponents_wind
        return bmp

    def dump_discard_data(self, gs: GameState):
        discard_bmp = self.states_to_bmp(gs)
        discard_bmp += gs.expect_discard
        self.discard_data.append(discard_bmp)

    def dump_chow_data(self, game_state: GameState):
        print(game_state)
        chow_bmp = self.states_to_bmp(game_state)
        chow_bmp += game_state.expect_chow
        self.chow_data.append(chow_bmp)

    def dump_pon_data(self, game_state: GameState):
        pon_bmp = self.states_to_bmp(game_state)
        pon_bmp += game_state.expect_pon
        self.pon_data.append(pon_bmp)

    def dump_minkan_data(self, game_state: GameState):
        minkan_bmp = self.states_to_bmp(game_state)
        minkan_bmp += game_state.expect_minkan
        self.minkan_data.append(minkan_bmp)

    def dump_reach_data(self, game_state: GameState):
        reach_bmp = self.states_to_bmp(game_state)
        reach_bmp += game_state.expect_reach
        self.reach_data.append(reach_bmp)

    def append_state(self, state):
        self.States.append(state)

    def form34_to_bin(self, data):
        res = []
        for test_c in data:
            one_test = []
            for lst34 in test_c:
                k = 0
                for i in range(34):
                    k <<= 1
                    k += lst34[i]
                one_test.append(k)
            res.append(one_test)
        return res

    def dump_all(self):
        datas_name = ['discard', 'chow', 'pon', 'minkan', 'reach']
        datas = [self.discard_data, self.chow_data,
                 self.pon_data, self.minkan_data, self.reach_data]
        for i in range(len(datas)):
            datas[i] = self.form34_to_bin(datas[i])
        for i in range(5):
            df = pd.DataFrame(datas[i])
            df.to_csv(f'TrainingData/{datas_name[i]}_data.csv', mode='a+',
                      header=False, index=False)


def generate_training_data(num, level):
    glc = mjk.GameLogCrawler()
    glc.db_show_tables()
    gene = glc.db_get_logs_where_players_lv_gr(level)
    for _ in range(num):
        td = TrainingData()
        log = next(gene)
        print(f'Generating level > {level} training data: {_+1}/{num}')
        result = mjk.PreProcessing.process_one_log(log)
        if result == None:
            continue
        for k, v in result.items():
            present_state = v[0]
            for state in v[1:]:
                td.process_player_states(present_state, state)
                present_state = state
        td.dump_all()


def check_log_format(log):
    res = mjk.PreProcessing.process_one_log(log)
    if res == None:
        return
    for k, v in res.items():
        print("Round {}".format(k))
        for state in v:
            print(state)


def check_nth_log(num, level):
    glc = mjk.GameLogCrawler()
    glc.db_show_tables()
    gene = glc.db_get_logs_where_players_lv_gr(level)
    log = None
    for _ in range(num):
        log = next(gene)
    mjk.GameLogCrawler.prt_log_format(log)
    # check_log_format(log)
    result = mjk.PreProcessing.process_one_log(log)
    if result == None:
        print('This log is bugged :(')
        return
    td = TrainingData()
    for k, v in result.items():
        present_state = v[0]
        for state in v[1:]:
            td.process_player_states(present_state, state)
            present_state = state
    td.dump_all()


def generate_trainging_data_after_nth(num, level, count):
    glc = mjk.GameLogCrawler()
    # glc.db_show_tables()
    gene = glc.db_get_logs_where_players_lv_gr(level)
    for _ in range(count):
        log = next(gene)
    for _ in range(num):
        log = next(gene)
        td = TrainingData()
        print(
            f'Generating level >= {level+1} training data: {_ + 1 + count}/{num + count}')
        # check_log_format(log)
        # mjk.GameLogCrawler.prt_log_format(log)
        result = mjk.PreProcessing.process_one_log(log)
        if result == None:
            continue
        for k, v in result.items():
            present_state = v[0]
            for state in v[1:]:
                td.process_player_states(present_state, state)
                present_state = state
        td.dump_all()


if __name__ == '__main__':
    mode = int(input(
        'What mode do you want to run? (1: generate data, 2: check n-th log, 3: generate after n-th log): '))
    if mode == 1:
        N = int(input('How much logs are using for training data? '))
        L = int(input('What is the minimum level of players? '))
        generate_training_data(N, L - 1)
    elif mode == 2:
        N = int(input('Which log do you want to check? '))
        L = int(input('What is the minimum level of players? '))
        check_nth_log(N, L - 1)
    elif mode == 3:
        C = int(input('How much logs already generated? '))
        N = int(input('How much logs are using for training data? '))
        L = int(input('What is the minimum level of players? '))
        process_list = []
        splN = N//8
        for i in range(8):
            p = mp.Process(target=generate_trainging_data_after_nth, args=(
                splN, L - 1, C + i * splN))
            p.start()
            process_list.append(p)
        for p in process_list:
            p.join()
        # generate_trainging_data_after_nth(N, L - 1, C)
