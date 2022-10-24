import random

# import MahjongKit as mjkit
import MahjongAgent as mjagent

import MahjongAgent as ma
import Mahjong_AI as mai


def main():
    test_hands = [
        [1, 2,  3,  4,  5,  6,  9,  10, 11, 15, 16, 32, 32, 33],
        [0, 2,  3,  4,  5,  6,  9,  10, 11, 15, 16, 32, 32, 33],
        [1, 1,  2,  2,  3,  3,  5,  5,  6,  6,  10, 10, 12, 12],
        [0, 0,  0,  1,  2,  4,  5,  5,  5,  6,  6,  15, 16, 17],
        [1, 2,  3,  5,  5,  5,  6,  6,  6,  14, 15, 16, 19, 19],
        [0, 3,  4,  8,  10, 10, 15, 18, 19, 20, 20, 31, 32, 33],
        [10, 10, 10, 11, 11, 11, 12, 12, 12, 13, 13, 13, 33, 31]
    ]

    agent = ma.MahjongAgent(0)
    ai = mai.Mahjong_AI()
    for i in test_hands:
        print("Testing Hand {}".format(i))
        print("Seq Part {}".format(agent.partition_dict(i, 'seq')))
        print("Tri Part {}".format(agent.partition_dict(i, 'tri')))
        print(ai.yaku_check(agent.partition_dict(i, 'seq'), agent.partition_dict(
            i, 'tri'), agent.partition_dict(i, 'pair'), ''))
        print("="*20)


if __name__ == '__main__':
    main()
