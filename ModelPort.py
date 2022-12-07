from MahjongKit.MahjongKit import Tile, Meld, Partition, WinWaitCal
from Player import Player
from keras.models import load_model
import tensorflow as tf
import numpy as np
import copy
import json


class ModelPort(Player):

    hand = None  # 1*[4*34] dynamic
    self_open_meld = None  # 1*[4*34] dynamic
    all_reveal_tiles = None  # 1*[4*34] dynamic
    self_discard_order = None  # 1*[20巡*34] dynamic
    self_score = None  # 1*[1*34] static
    self_reach_status = None  # 1*[1*34] dynamic
    opponents_open_hend = None  # 3*[4*34] dynamic
    opponents_discards_order = None  # 3*[20巡*34] dynamic
    opponents_scores = None  # 3*[1*34] static
    opponents_reach_status = None  # 3*[1*34] dynamic
    doras = None  # 1*[4*34] dynamic
    round_wind = None  # 1*[1*34] static
    self_wind = None  # 1*[1*34] static
    opponents_winds = None  # 3*[1*34] static

    def __init__(self, gameboard, model_file):
        self.model = load_model(model_file)
        super().__init__(gameboard)

    def get_state(self):
        self.__opponents_index = [(self.seat+i) % 4 for i in range(1, 4)]
        self.set_static()
        self.update_dynamic()
        state = []
        state += self.hand
        state += self.self_open_meld
        state += self.opponents_open_hend[0]
        state += self.opponents_open_hend[1]
        state += self.opponents_open_hend[2]
        state += self.self_discard_order
        state += self.opponents_discards_order[0]
        state += self.opponents_discards_order[1]
        state += self.opponents_discards_order[2]
        state += self.all_reveal_tiles
        state += [self.self_reach_status]
        state += self.opponents_reach_status
        state += self.doras
        state += [self.self_score]
        state += self.opponents_scores
        state += [self.round_wind]
        state += [self.self_wind]
        state += self.opponents_winds
        json.dump(state, open('state.json', 'a+'))
        return state

    def set_static(self):
        self.__set_static_self_score()
        self.__set_static_opponents_scores()
        self.__set_static_round_wind()
        self.__set_static_self_wind()
        self.__set_static_opponents_winds()

    # self_score        # 1*[1*34] static
    def __set_static_self_score(self):
        raw_score = self.points if(self.points < 50000) else 50000
        res = self.get_34_zero()
        for i in range(int(raw_score/50000*34)):
            res[i] = 1
        self.self_score = res

    # opponents_scores  # 3*[1*34] static
    def __set_static_opponents_scores(self):
        res = self.get_34_zeros(3)
        for i, player in enumerate(self.__opponents_index):
            if(self.gameboard.points[player] < 50000):
                raw_score = self.gameboard.points[player]
            else:
                raw_score = 50000
            for j in range(int(raw_score/50000*34)):
                res[i][j] = 1
        self.opponents_scores = res

    #  round_wind       # 1*[1*34] static
    def __set_static_round_wind(self):
        raw_wind = self.gameboard.wind
        res = self.get_34_zero()
        res[raw_wind+27] = 1
        self.round_wind = res

    # self_wind         # 1*[1*34] static
    def __set_static_self_wind(self):
        raw_wind = self.wind34
        res = self.get_34_zero()
        res[raw_wind] = 1
        self.self_wind = res

    # opponents_winds   # 3*[1*34] static
    def __set_static_opponents_winds(self):
        res = self.get_34_zeros(3)
        for i in range(3):
            res[i][((self.wind+i+1) % 4)+27] = 1
        self.opponents_winds = res

    def update_dynamic(self):
        self.__update_dynamic_hand()
        self.__update_dybanic_self_open_meld()
        self.__update_dynamic_all_reveal_tiles()
        self.__update_dynamic_self_discard_order()
        self.__update_dynamic_self_reach_status()
        self.__update_dynamic_opponents_open_hend()
        self.__update_dynamic_opponents_discards_order()
        self.__update_dynamic_opponents_reach_status()
        self.__update_dynamic_doras()

    # dynamic_hand              1*[4*34] dynamic
    def __update_dynamic_hand(self):
        res = self.get_34_zeros(4)
        for tile in self.tiles:
            the_tile = Tile.convert_bonus(tile)
            i = 0
            while(res[i][the_tile] == 1):
                i += 1
            res[i][the_tile] = 1
        self.hand = res

    # self_open_meld            1*[4*34] dynamic
    def __update_dybanic_self_open_meld(self):
        res = self.get_34_zeros(4)
        for tile in self.gameboard.open_melds[self.seat]:
            cv_tile = Tile.convert_bonus(tile)
            cnt = 0
            while(res[cnt][cv_tile] == 1):
                cnt += 1
            res[cnt][cv_tile] = 1
        self.self_open_meld = res

    # all_reveal_tiles          1*[4*34] dynamic
    def __update_dynamic_all_reveal_tiles(self):
        all_reveal = copy.deepcopy(self.gameboard.bonus_indicators)
        for i in range(4):
            all_reveal += self.gameboard.discard_tiles[i]
            all_reveal += self.gameboard.open_melds[i]
        res = self.get_34_zeros(4)
        for tile in all_reveal:
            cv_tile = Tile.convert_bonus(tile)
            cnt = 0
            while(res[cnt][cv_tile] == 1):
                cnt += 1
                if cnt > 3:
                    cnt = 3
                    break
            res[cnt][cv_tile] = 1
        self.all_reveal_tiles = res

    # self_discard_order        1*[20巡*34] dynamic
    def __update_dynamic_self_discard_order(self):
        raw_discard = [Tile.convert_bonus(i) for i in self.gameboard.discard_tiles[self.seat]]
        res = self.get_34_zeros(20)
        for i, tile in enumerate(raw_discard):
            if(i == 20):
                break
            res[i][tile] = 1
        self.self_discard_order = res

    # self_reach_status         1*[1*34] dynamic
    def __update_dynamic_self_reach_status(self):
        if(self.is_riichi):
            res = self.get_34_one()
        else:
            res = self.get_34_zero()
        self.self_reach_status = res

    # _opponents_open_hend      3*[4*34] dynamic
    def __update_dynamic_opponents_open_hend(self):
        res = [self.get_34_zeros(4) for _ in range(3)]
        for i, player in enumerate(self.__opponents_index):
            for tile in self.gameboard.open_melds[player]:
                cv_tile = Tile.convert_bonus(tile)
                cnt = 0
                while(res[i][cnt][cv_tile] == 1):
                    cnt += 1
                res[i][cnt][cv_tile] = 1
        self.opponents_open_hend = res

    # opponents_discards_order  3*[20巡*34] dynamic
    def __update_dynamic_opponents_discards_order(self):
        res = [self.get_34_zeros(20) for _ in range(3)]
        for i, player in enumerate(self.__opponents_index):
            for j, tile in enumerate(self.gameboard.discard_tiles[player]):
                if(j == 20):
                    break
                cv_tile = Tile.convert_bonus(tile)
                res[i][j][cv_tile] = 1
        self.opponents_discards_order = res

    # opponents_reach_status    3*[1*34] dynamic
    def __update_dynamic_opponents_reach_status(self):
        res = []
        for player in self.__opponents_index:
            if(self.gameboard.riichi_status[player]):
                res.append(self.get_34_one())
            else:
                res.append(self.get_34_zero())
        self.opponents_reach_status = res

    # dynamic_doras             1*[4*34] dynamic TODO
    def __update_dynamic_doras(self):
        res = self.get_34_zeros(4)
        for indi in self.gameboard.bonus_indicators:
            dora = Tile.ind_to_bonus_dic[indi]
            cnt = 0
            while(res[cnt][dora] == 1):
                cnt += 1
            res[cnt][dora] = 1
        self.doras = res

    def get_34_zeros(self, dim):
        if(dim == 1):
            return self.get_34_zero()
        return [self.get_34_zero() for _ in range(dim)]

    def get_34_zero(self):
        return [0 for _ in range(34)]

    def get_34_one(self):
        return [1 for _ in range(34)]

    # overide
    def to_discard_tile(self):
        state = np.array(self.get_state()).reshape(1, 34, 121, 1)
        raw = self.model.predict(state)

        res = []
        for tile, val in enumerate(raw[0]):
            res.append({'tile': tile, 'percent': val})
        res = sorted(res, key=lambda x: -x['percent'])

        for i in range(5):
            print(f'{Tile.t34_to_grf(res[i]["tile"])} :{res[i]["percent"]:.5f}', end=' ')

        print(f'\nhand: {" ".join(Tile.t34_to_grf(self.tiles))}')
        i = 0
        cnv_tiles = [Tile.convert_bonus(tile) for tile in self.tiles]
        while(res[i]['tile'] not in cnv_tiles):
            i += 1
        final = cnv_tiles.index(res[i]['tile'])
        print(f'chose:{Tile.t34_to_grf(self.tiles[final])} which is {i}th in prediction.')

        return {'tile': self.tiles[final]}
