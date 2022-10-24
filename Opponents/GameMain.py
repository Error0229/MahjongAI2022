import OpponentClass
import MahjongAgent
import GameBoard


def main():
    round_num = 1
    op1 = OpponentClass.OpponentClass()
    op2 = OpponentClass.OpponentClass()
    op3 = OpponentClass.OpponentClass()
    oppo_list = [op1, op2, op3]
    round_wind = input('Please input the round wind')
    self_wind = input('Please input the self wind')
    dora_indic = input('Please input the dora indicator')

    board = GameBoard.GameBoard(oppo_list, dora_indic, round_wind, self_wind)
    agent = MahjongAgent.MahjongAgent(board)

    while (True):

        for i in range(14):
            stdin = int(input('Please input your hand : ' + '\n'))
            agent.hand_add(stdin)

        round_discard = []

        opponent1_discard = int(
            input('Please input the opponent 1 dicard'+'\n'))
        board.opponent_getter(1).discard_add(opponent1_discard)
        round_discard.append(opponent1_discard)

        opponent2_discard = int(
            input('Please input the opponent 2 discard'+'\n'))
        board.opponent_getter(2).discard_add(opponent2_discard)
        round_discard.append(opponent2_discard)

        opponent3_discard = int(
            input('Please input the opponent 3 discard'+'\n'))
        board.opponent_getter(3).discard_add(opponent3_discard)
        round_discard.append(opponent3_discard)

        for tile in round_discard:
            agent.tile_count_update(tile)

        agent_discard = agent.to_discard_tile()

        print(f'Round {round_num}: ')
        print('Your hand: ', agent.hand_getter())
        print('opponent1_discard: ', board.opponent_getter(
            1).discard_getter(), '\n')
        print('opponent2_discard: ', board.opponent_getter(
            2).discard_getter(), '\n')
        print('opponent3_discard: ', board.opponent_getter(
            3).discard_getter(), '\n')
        print('agent_discard: ', agent_discard, '\n')


if __name__ == "__main__":
    main()
