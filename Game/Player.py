from MahjongKit.MahjongKit import Tile, Meld, Partition, WinWaitCal
import random
import copy

# add shantin changing records
# add legal/inlegal discard records
# add Ron, houjuu, tsumo counts

class Player:
    wind = 0
    wind34 = 0
    selfwind = 0
    roundwind34 = 0
    seat = 0
    tiles = []
    discard_tiles = []
    points = 0
    gameboard = None
    open_melds = []
    ankan = []
    minkan = []
    is_riichi = False
    
    def __init__(self, gameboard):
        self.tiles = []
        self.discard_tiles = []
        self.points = 25000
        self.gameboard = gameboard
        self.open_melds = []
        self.ankan = []
        self.is_status = False
        self.player_log = {'shantin': [], 'legal_predict': [], 'ron_cnt':0, 'houjuu_cnt':0, 'tsumo_cnt':0, 'tenpai_cnt':0}

    def init_tiles(self, tiles):
        self.tiles = tiles

    def set_round_wind(self, wind):
        self.roundwind34 = wind+27

    def set_seat(self, seat):
        self.seat = seat

    def set_wind(self, wind):
        self.wind = wind
        self.wind34 = wind + 27

    def init_round(self):
        self.is_riichi = False
        self.player_log['shantin'].append([])
        self.player_log['legal_predict'].append([])

    def discard_tile(self, last=None):
        # tile = self.tiles[random.randint(0, len(self.tiles)-1)]
        if(self.is_riichi):
            tile = last
        else:
            tile = self.to_discard_tile()['tile']
        self.tiles.remove(tile)
        self.discard_tiles.append(tile)
        #self.gameboard.discard_tile(self.seat, tile)
        # self.display()
        self.player_log['shantin'][-1].append(self.get_shantin())
        return tile

    # return {'tile':int, 'shantin':int}
    def to_discard_tile(self, new_hand=None, new_meld=[]):
        is_check = [False for i in range(34)]
        res = None
        for id in range(len(self.tiles)):
            if(new_hand==None):
                hand = copy.deepcopy(self.tiles)
            else:
                hand = copy.deepcopy(new_hand)
            new_tile = hand.pop(id)
            if (is_check[Tile.convert_bonus(new_tile)]):
                # perfer to discard the normal tile over bonus tile
                if(Tile.convert_bonus(new_tile) == Tile.convert_bonus(res['tile'])):
                    res['tile'] = Tile.convert_bonus(new_tile)
                continue
            else:
                is_check[Tile.convert_bonus(new_tile)] = True
            check = {'tile': new_tile, 'shantin': self.get_shantin(hand, new_meld)}
            if (res == None):
                res = check
            else:
                if (res['shantin'] < check['shantin']):
                    continue
                else:
                    res = check
        return res

    def draw_tile(self, tile):
        self.tiles.append(tile)
        self.tiles.sort()

    def display(self):
        print(f'player {self.seat}, Wind: {Tile.t34_to_grf(self.wind34)}', end=' , ')
        print(f'score: {self.points}', end=' , ')
        print(f'riichi: {self.is_riichi}', end=' , ')
        str_tile = f"Tile: {' '.join(Tile.t34_to_grf(self.tiles))}"
        str_meld = f"Melds: {' '.join(Tile.t34_to_grf(self.open_melds))}"
        str_minkan = f"minkans: {' '.join(Tile.t34_to_grf(self.minkan))}"
        print(f"{str_tile:<31} , {str_meld:<20} , {str_minkan:<20}")
        print(f'shantin: {self.player_log["shantin"]}')

    def get_shantin(self, new_tiles=None, new_meld=[]):
        if (new_tiles == None):
            hand = self.tiles
        else:
            hand = new_tiles
        melds = self.open_melds + new_meld
        bonus_chr = list(
            filter(lambda f: f in [self.wind34, self.roundwind34, 31, 32, 33], hand))
        all_shantin = Partition.shantin_multiple_forms(hand, melds, bonus_chr)
        if(min([i for i in list(all_shantin.values())])<0):
            return 0
        else:
            return min([i for i in list(all_shantin.values())])

    # only return list of tiles waiting
    def get_waiting(self, is_draw, is_dealer):
        hand = Tile.convert_bonuses(self.tiles)
        bonus_tiles = [34, 35, 36]
        bonus_num = 0

        for i in self.tiles:
            if (i in [34, 35, 36]):
                # bonus_tiles.append(i)
                bonus_num += 1
        for _meld in self.open_melds + self.minkan + self.ankan:
            for _tile in _meld:
                if (_tile in bonus_tiles):
                    bonus_num += 1
        for i in self.gameboard.bonus_indicators:
            bonus_tiles.append(Tile.ind_to_bonus_dic[i])
        bonus_num += len([i for i in hand if i in bonus_tiles])
        waiting = WinWaitCal.waiting_calculation(hand, self.open_melds, self.minkan, self.ankan, is_draw, self.wind34, self.roundwind34,
                                                 self.is_riichi, bonus_num, bonus_tiles, self.gameboard.honba_sticks, self.gameboard.reach_sticks, is_dealer)
        return list(waiting.keys())
        # WinWaitCal.waiting_calculation(hand, melds, minkan, ankan, is_zimo, self.seat, self.wind, is_riichi, bonus_num, bonus_tiles, benchan, reach_stick, is_dealer)

    def get_score(self, tile, from_player, is_dealer):
        is_zimo = (from_player == self.seat)
        hand = Tile.convert_bonuses(self.tiles)
        bonus_tiles = [34, 35, 36]
        bonus_num = 0
        for i in self.tiles:
            if (i in [34, 35, 36]):
                # bonus_tiles.append(i)
                bonus_num += 1
        for i in self.gameboard.bonus_indicators:
            bonus_tiles.append(Tile.ind_to_bonus_dic[i])
        if is_zimo:
            for i in self.gameboard.hidden_bonus_indicators:
                bonus_tiles.append(Tile.ind_to_bonus_dic[i])
        bonus_num += len([i for i in hand if i in bonus_tiles])
        for _meld in self.open_melds + self.minkan + self.ankan:
            for _tile in _meld:
                if (_tile in bonus_tiles):
                    bonus_num += 1
        win = WinWaitCal.score_calculation(hand, tile, self.open_melds, self.minkan, self.ankan, is_zimo, self.wind34, self.roundwind34,
                                           self.is_riichi, bonus_num, bonus_tiles, self.gameboard.honba_sticks, self.gameboard.reach_sticks, is_dealer)
        return win

    '''
    action dict contain:
        type:       str (win, chi, pon, minkan, draw, none, ... )
        player:     int (player who do the action)
        from:       int (discard tile form the player / draw tile from self)
        tile:       int (discard tile)
        meld:       [int, int, int] (for chi, pon, minkan) ([] if win, draw, none)
        need_draw:  bool (True if draw, minkan)
    
    discard_action:
        win, minkan, pon, chi, draw, none
    
    draw_action:
        zimo, ankan, riichi, none
    '''
    def can_discard_action(self, tile, from_player):
        if(self.seat == from_player):
            return {'type': 'none', 'player': self.seat, 'from': from_player, 'tile': tile,
                    'meld': [], 'need_draw': False}
        discard_actions = self.can_win(tile, from_player)           # add win
        if(discard_actions != []):
            return discard_actions[0]
        discard_actions += self.can_draw(tile, from_player)         # add draw/none
        if(not self.is_riichi):
            discard_actions += self.can_pon(tile, from_player)      # add pon
            discard_actions += self.can_chi(tile, from_player)      # add chi
            discard_actions += self.can_minkan(tile, from_player)   # add minkan
        
        least_shantin = self.to_discard_tile()['shantin']
        best_action = discard_actions[0]
        for action in discard_actions[1::]:
            new_hand = copy.deepcopy(self.tiles) + action['meld']
            for t in action['meld']:
                new_hand.remove(t)
            if(action['type']=='chi' or action['type']=='pon'):
                new_shanten = self.to_discard_tile(new_hand, [action['meld']])['shantin']
                if(new_shanten < least_shantin):
                    least_shantin = new_shanten
                    best_action = action
            elif(action['type']=='minkan'):
                new_shanten = self.get_shantin(new_hand, [action['meld']])
                if(new_shanten < least_shantin):
                    least_shantin = new_shanten
                    best_action = action
        return best_action

    def do_discard_action(self, discard_action):
        if (discard_action['type'] == 'chi' or discard_action['type'] == 'pon'):
            self.open_melds.append(discard_action['meld'])
        elif discard_action['type'] == 'minkan':
            self.minkan.append(discard_action['meld'])
        self.tiles.append(discard_action['tile'])
        for tile in discard_action['meld']:
            self.tiles.remove(tile)
        
    def can_chi(self, tile, from_player):
        if ((self.seat - from_player) % 4 == 1):
            melds = []
            convert_tile = Tile.convert_bonus(tile)
            for parts in Partition.partition(self.tiles):
                for part in parts:
                    # put part with 2 different tiles in melds
                    if (len(part) == 2 and (part[0] != part[1]) and (part not in melds)):
                        melds.append(part)
            # complete every meld, and check if it is in the chow index
            melds = list(map(lambda x: sorted(x+[convert_tile]), melds))
            melds = list(filter(lambda x: (x in Tile.index_to_chow), melds))
            if (len(melds) > 0):
                ress = []
                for m in melds:
                    if ((4 in m) and (34 in (self.tiles + [tile]))):
                        meld = [(34 if (t == 4) else t) for t in m]
                    elif ((13 in m) and (35 in (self.tiles + [tile]))):
                        meld = [(35 if (t == 13) else t) for t in m]
                    elif ((22 in m) and (36 in (self.tiles + [tile]))):
                        meld = [(36 if (t == 22) else t) for t in m]
                    else:
                        meld = m
                    ress.append({'type': 'chi', 'player': self.seat, 'from': from_player,
                                 'tile': tile, 'meld': meld, 'need_draw': False})
                return ress
        return []

    def can_pon(self, tile, from_player):
        convert_hands = Tile.convert_bonuses(self.tiles)
        convert_tile = Tile.convert_bonus(tile)
        if (convert_hands.count(convert_tile) >= 2):
            if ((convert_tile == 4) and (34 in (self.tiles + [tile]))):
                meld = [4, 4, 34]
            elif ((convert_tile == 13) and (35 in (self.tiles + [tile]))):
                meld = [13, 13, 35]
            elif ((convert_tile == 22) and (36 in (self.tiles + [tile]))):
                meld = [22, 22, 36]
            else:
                meld = [tile, tile, tile]
            return [{'type': 'pon', 'player': self.seat, 'from': from_player,
                     'tile': tile, 'meld': meld, 'need_draw': False}]
        return []

    def can_minkan(self, tile, from_player):
        convert_hands = Tile.convert_bonuses(self.tiles)
        convert_tile = Tile.convert_bonus(tile)
        if (convert_hands.count(convert_tile) == 3):
            if ((convert_tile == 4) and (34 in (self.tiles + [tile]))):
                meld = [4, 4, 4, 34]
            elif ((convert_tile == 13) and (35 in (self.tiles + [tile]))):
                meld = [13, 13, 13, 35]
            elif ((convert_tile == 22) and (36 in (self.tiles + [tile]))):
                meld = [22, 22, 22, 36]
            else:
                meld = [tile, tile, tile, tile]
            return [{'type': 'minkan', 'player': self.seat, 'from': from_player,
                     'tile': tile, 'meld': meld, 'need_draw': True}]
        return []

    def can_draw(self, tile, from_player):
        if ((self.seat - from_player) % 4 == 1):
            return [{'type': 'draw', 'player': self.seat, 'from': from_player, 'tile': tile,
                    'meld': [], 'need_draw':True}]
        return [{'type': 'none', 'player': self.seat, 'from': from_player, 'tile': tile,
                'meld': [], 'need_draw':False}]

    def can_win(self, tile, from_player):
        if (tile in self.get_waiting(False, self.gameboard.game-1 == self.seat)):
            return [{'type': 'win', 'player': self.seat, 'from': from_player, 'need_draw': False, 'tile': tile}]
        return []

    def can_draw_action(self, tile):
        draw_actions = self.can_zimo(tile)
        if(draw_actions != []):
            return draw_actions[0]
        if(not self.is_riichi):
            draw_actions += self.can_riichi(tile)
        draw_actions += self.can_ankan(tile)
        draw_actions += [{'type': 'discard'}]
        return draw_actions[0]
        # return random.choice(draw_actions)

    def do_draw_action(self, draw_action):
        if(draw_action['type'] == 'ankan'):
            self.open_melds += draw_action['meld']
            self.tiles.append(draw_action['tile'])
            for tile in draw_action['meld']:
                self.tiles.remove(tile)
        elif(draw_action['type'] == 'riichi'):
            self.is_riichi = True

    def can_ankan(self, tile):
        convert_hands = Tile.convert_bonuses(self.tiles)
        convert_tile = Tile.convert_bonus(tile)
        if (convert_hands.count(convert_tile) == 3):
            if ((convert_tile == 4) and (34 in (self.tiles + [tile]))):
                meld = [4, 4, 4, 34]
            elif ((convert_tile == 13) and (35 in (self.tiles + [tile]))):
                meld = [13, 13, 13, 35]
            elif ((convert_tile == 22) and (36 in (self.tiles + [tile]))):
                meld = [22, 22, 22, 36]
            else:
                meld = [tile, tile, tile, tile]
            return [{'type': 'ankan', 'player': self.seat, 'from': self.seat,
                     'tile': tile, 'meld': meld, 'need_draw': True}]
        return []

    def can_riichi(self, tile):
        if(self.open_melds != []):
            return []
        hand = copy.deepcopy(self.tiles)
        hand.append(tile)

        is_check = []
        waiting = []
        to_discard = None
        for id, tile in enumerate(hand):
            tile = Tile.convert_bonus(tile)
            if(tile in is_check):
                continue
            is_check += [tile]
            new_hand = [Tile.convert_bonus(hand[i]) for i in range(len(hand)) if i != id]
            new_waiting = WinWaitCal.waiting_calculation(new_hand, [], [], self.ankan, True, self.wind34, self.roundwind34,
                                                         True, 0, [], 0, 0, False)
            new_waiting = list(new_waiting)
            if(len(waiting) < len(new_waiting)):
                waiting = new_waiting
                to_discard = tile
        if(waiting != []):
            return [{'type': 'riichi', 'player': self.seat, 'from': self.seat, 'tile': tile, 'need_draw': False, 'to_discard': to_discard}]
        return []

    def can_zimo(self, tile):
        if (tile in self.get_waiting(True, self.gameboard.game-1 == self.seat)):
            return [{'type': 'zimo', 'player': self.seat, 'from': self.seat, 'tile': tile, 'need_draw': False}]
        return []

    def update_log_round_end(self, status):
        if(status['status'] == 'Win'):
            if(self.seat in status['win_players']):
                if(status['is_zimo']):
                    self.player_log['tsumo_cnt'] += 1
                else:
                    self.player_log['ron_cnt'] += 1
            elif(status['is_zimo']==False and status['win_from_who']==self.seat):
                self.player_log['houjuu_cnt'] += 1

        if(self.is_tenpai):
            self.player_log['tenpai_cnt'] += 1

    @ property
    def is_tenpai(self):
        return len(self.get_waiting(False, self.gameboard.game-1 == self.seat))
