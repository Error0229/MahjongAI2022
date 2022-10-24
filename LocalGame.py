import random
import Pro


class FullGame():

    def __init__(self, player_count, players):
        self.round_number = 0
        # tmp_players = players
        tmp_players = [Pro.Pro() for i in range(player_count)]
        random.shuffle(tmp_players)
        self.round = Round(player_count, tmp_players, self.round_number, 0, 0)

    def start_round(self):
        self.round.run()

    @property
    def players(self):
        return self.round.players

    @property
    def player_count(self):
        return self.round.player_count

    @property
    def round_number(self):
        return self.round_number

    @property
    def game_table(self):
        return self.round.game_table


class Round():

    dealer = 0
    players = None
    player_count = 0
    reach_sticks = 0
    honba_sticks = 0

    def __init__(self, player_count, players, round_number, reach_sticks, honba_sticks):
        self.player_count = player_count
        self.players = players
        self.dealer = round_number % player_count
        self.reach_sticks = reach_sticks
        self.honba_sticks = honba_sticks
        self.game_table = GameTable(reach_sticks, honba_sticks)
        for player in self.players:
            player.init_tiles(self.game_table.get_tile(13))

    # WIP need player interaction, multiple winners, everything here suck
    def run(self, round_number):
        turn = self.dealer
        last_tile = -1
        new_tile = -1
        action = ''
        action_from_player = -1
        action_to_players = []

        # do draw: none, riichi, kon, nouth
        # no draw: chi, pon, win
        self.players[turn] = self.game_table.get_tile()
        last_tile = self.players[turn].discard()

        while (last_tile != -1):
            action = self.player_action()
            if (action == 'win'):
                pass
            elif (action == 'chi'):
                pass
            elif (action == 'pon'):
                pass
            elif (action == 'kon'):
                pass
            elif (action == 'riich'):
                pass
            elif (action == 'north'):
                pass
            elif(action ==):
                pass
            elif(action ==):
                pass
            elif(action ==):
                pass

    # WIP need player interaction

    def player_action(self):
        action = None
        last_tile = -1
        action_player = 1
        return action, last_tile, action_player


# WIP probably merge into round class
class GameTable():

    bonus_indicators = None
    remaining_count = 0
    revealed_tiles = None
    tiles = None

    def __init__(self):
        self.tiles = [i for j in range(4) for i in range(34)]
        self.tiles[4] = 34
        self.tiles[13] = 35
        self.tiles[22] = 36
        random.shuffle(self.tiles)
        # add -1 at the end of tiles, to prevent index error
        self.tiles.append(-1)
        self.bonus_indicators = [self.tiles[9]]
        self.remaining_count = 136

    def get_tile(self, num=1):
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
