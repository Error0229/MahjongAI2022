import random
import Pro

class FullGame():

    def __init__(self, player_count, players):
        self.round_number = 0
        self.game_table = GameTable()
        # tmp_players = players
        tmp_players = [Pro.Pro(self.game_table) for i in range(player_count)]
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
            player.init_tiles(self.game_table.draw_tile(13))


    # round post last tile to players
    # get their responds
    # chose one to proceed (win > pon/kan > chi > none)
    # draw to player if need draw
    # get discard tile and repeat
    def run(self, round_number):
        turn = self.dealer
        draw = self.game_table.draw_tile()
        is_win = False
        is_over = False

        # action: [int:discard]
        # currently need: discard, action_player, need_draw
        action = self.players[turn].draw(draw) # player draw func
        while(action[0] != -1):
            discard = action[0]
            turn = action[1]

            # get actions from players
            actions = [None for i in self.player_count]
            for id,player in enumerate(self.players):
                if(id != turn):
                    actions[id] = player.action(discard, turn) # player action function (how do the player handle the tile)
            
            # somehow get the right action
            action = actions[0]

            # if need_draw
            if(action[2]):
                action = self.players[turn].draw(draw)
        


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