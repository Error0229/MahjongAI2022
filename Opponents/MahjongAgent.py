from collections import defaultdict
from GameBoard import GameBoard
import Mahjong_AI
import numpy as np
import pickle


class MahjongAgent:

    wan = [1, 1, 3, 1, 2, 3, 0, 0, 1]  # 0-8
    so = [0, 0, 0, 1, 0, 0, 0, 2, 1]  # 9-17
    pin = [1, 1, 0, 1, 0, 0, 0, 0, 0]  # 18-26
    honor = [0, 0, 0, 0, 0, 0, 0]
    hands = [wan, so, pin]
    gameboard = None
    hand = []
    open_meld = []
    partition = {}
    efficiency_map = {}
    num_remain_tile = 70
    tile_count = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
                  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]

    han = 0
    fu = 20

    def __init__(self, gameboard):
        self.hand = []
        self.open_meld = []
        self.gameboard = gameboard
        self.tile_count = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
                           4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
        self.num_remain_tile = 83
        self.fu = 20
        self.han = 0
        self.seq_meld = 0
        self.tri_meld = 0
    # def __init__(self):
    #     self.han = 0
    #     self.used_tile = 0
    #     self.seq_meld = 0
    #     self.tri_meld = 0

    # sequence_two-way * 0.7 * 0.24
    # sequence_middle * 0.01
    # def new_partition(self):
    #     pair = []
    #     for t in self.hands:
    #         sequence = {}
    #         triplet = {}
    #         kang_triplet = []
    #         for x in range(len(t)):
    #             if(t[x] == 4):
    #                 # mark index as kang_triplet
    #                 kang_triplet.append(x)
    #             if(t[x] == 3):
    #                 # mark index as triplet
    #                 print("triplet at:" + str(x))
    #                 triplet.update(str(x),x)
    #             elif(t[x] == 2):
    #                 # mark index as pair
    #                 print("pair at:" + str(x))
    #                 pair.append(x)
    #             elif(x<=6):
    #                 if(t[x] >= 1 and t[x+1]>=1 and t[x+2]>=1):
    #                     true_count = 0
    #                     if(t[x] >= 3):
    #                         true_count += 1
    #                     if(t[x] >= 3):
    #                         continue
    #                     else:
    #                         # mark index as sequence-complete
    #                         print("sequence complete at:" + str(x))
    #                         sequence.update(str(x),x)

    #         for num in sequence:
    #             if (sequence.get(num) in triplet or sequence.get(num+1) in triplet or sequence(num+2) in triplet):
    #                 # mark sequence index with triplet overlap

    #                 print("sequence complete plus pair")

    def tenpai_status_check(self, hand):
        return_list = {}
        single_tile = []
        value_list = []
        if(len(hand) % 3 == 1):
            return return_list

        if(len(hand) == 14):
            # check seven-pairs
            pair_count = 0
            x = 0
            while x < 13:
                if(hand[x] == hand[x+1]):
                    pair_count += 1
                    x += 2
                else:
                    single_tile.append(hand[x])
                    x += 1
            if(x == 13):
                single_tile.append(hand[x])

            if(pair_count == 7):
                for tile in hand:
                    return_list.setdefault(tile, tile)
                return return_list

            if(pair_count == 6):
                return_list.setdefault(single_tile[0], [single_tile[1]])
                return_list.setdefault(single_tile[1], [single_tile[0]])
                return return_list

        if(len(hand) == 2):
            return_list.setdefault(hand[0], [hand[1]])
            return_list.setdefault(hand[1], [hand[0]])
            # print(return_list)
            return return_list

        if(len(hand) == 3):

            left_dis = hand[1] - hand[0]
            right_dis = hand[2] - hand[1]

            if(hand[0]//9 == hand[1]//9 and left_dis <= 2):
                if(hand[1] - hand[0] == 2):
                    # sequence-middle
                    return_list.setdefault(hand[2], [hand[1]-1])
                else:
                    # two-way or one-way
                    left = hand[0] - 1
                    right = hand[1] + 1
                    if(left//9 == right//9):
                        # two-way
                        return_list.setdefault(hand[2], [left, right])
                    else:
                        # one-way
                        if(left < 0):
                            return_list.setdefault(hand[2], [right])

                        elif((right-1) % 9 >= 5):
                            return_list.setdefault(hand[2], [left])
                        else:
                            return_list.setdefault(hand[2], [right])

            if(hand[1]//9 == hand[2]//9 and right_dis <= 2):
                if(hand[2] - hand[1] == 2):
                    # sequence-middle
                    return_list.setdefault(hand[0], [hand[2]-1])
                else:
                    # two-way or one-way
                    left = hand[1] - 1
                    right = hand[2] + 1
                    if(left // 9 == right // 9):
                        # two-way
                        return_list.setdefault(hand[0], [left, right])
                    else:
                        if (left < 0):
                            return_list.setdefault(hand[0], [right])
                        # one-way
                        elif((right-1) % 9 >= 5):
                            return_list.setdefault(hand[0], [left])
                        else:
                            return_list.setdefault(hand[0], [right])

        if(len(hand) == 5):
            remain = []
            for x in range(len(hand)-2):
                remain = self.seq_extract(hand, x)
                remain = self.pair_extract(remain)
                remain = self.tri_extract(remain)
                if(len(remain) != 5):
                    # double pair waiting
                    if(len(remain) == 1):
                        y = 0
                        while y < len(hand):
                            if(hand[y] != remain[0]):
                                value_list.append(hand[y])
                                y += 2
                            else:
                                y += 1
                        return_list.setdefault(remain[0], value_list)
                    # print("check point 1")
                    extend_dict = self.tenpai_status_check(remain)
                    for key in extend_dict:
                        if(key in return_list):
                            for item in extend_dict[key]:
                                if (item not in return_list[key]):
                                    return_list[key].append(item)
                        else:
                            return_list.setdefault(key, extend_dict[key])

        if(len(hand) > 5):
            # print("greater 5")
            remain = []
            for x in range(len(hand)-2):
                remain = self.seq_extract(hand, x)
                remain = self.tri_extract(remain)
                if(len(remain) < len(hand)):
                    # print("check point 2")
                    extend_dict = self.tenpai_status_check(remain)
                    for key in extend_dict:
                        if(key in return_list):
                            for item in extend_dict[key]:
                                if (item not in return_list[key]):
                                    return_list[key].append(item)
                        else:
                            return_list.setdefault(key, extend_dict[key])

        # print("final:")
        # print(return_list)
        return return_list

    def pair_extract(self, hand):
        remain = []
        x = 0
        while x < (len(hand)-1):
            if (hand[x] == hand[x+1]):
                x += 2
                continue
            remain.append(hand[x])
            x += 1
        if(x < len(hand)):
            remain.append(hand[x])
        # print("extract pair:")
        # print(remain)
        return remain

    def tri_extract(self, hand):
        remain = []
        x = 0
        while x < (len(hand)-2):
            if(hand[x] == hand[x+1] == hand[x+2]):
                x += 3
                continue
            remain.append(hand[x])
            x += 1

        if(x < len(hand)):
            remain.append(hand[x])
        if(x < len(hand)-1):
            remain.append(hand[x+1])

        # print("extract tri:")
        # print(remain)
        return remain

    def seq_extract(self, hand, index):

        remain = []
        remain.extend(hand[0:index])
        partial_hand = hand[index:]
        index_1_count = 0
        index_2_count = 0
        index_3_count = 0
        index_1_move = 0
        index_2_move = 0
        index_3_move = 0
        x = 0
        value = partial_hand[0]
        while x < (len(partial_hand)-2):

            # print(partial_hand)
            if(index_1_move == 0):
                value = partial_hand[x]
                index_1_count = partial_hand.count(value)
                # print(value)

            # no more possible sequences beyong tile 25
            if(value >= 25):
                # print("greater than 15")
                remain.extend(partial_hand[x:])
                return remain

            # if three values are within the same type
            if (value // 9 == (value+2) // 9):

                if(index_2_move == 0):
                    index_2_count = partial_hand.count(value+1)
                    # print(value+1)
                if(index_3_move == 0):
                    index_3_count = partial_hand.count(value+2)
                    # print(value+2)

                # print(str(index_1_count) + "," + str(index_2_count) + "," + str(index_3_count))

                # if there are at least one instance of each value
                if (index_1_count > 0 and index_2_count > 0 and index_3_count > 0):

                    # if the numbers of each value are the same
                    if(index_1_count == index_2_count == index_3_count):

                        # loop index advance move sum * 3
                        x += ((index_1_count)*3 + index_1_move +
                              index_2_move + index_3_move)

                        # full reset
                        index_1_count = 0
                        index_2_count = 0
                        index_3_count = 0
                        index_1_move = 0
                        index_2_move = 0
                        index_3_move = 0
                        continue
                    # if the first value is the smallest
                    if (index_1_count <= index_2_count and index_1_count <= index_3_count):

                        # index_2 and index_3 -= index_1, index_2_move and 3_move += index_1
                        index_2_count -= index_1_count
                        index_3_count -= index_1_count
                        index_2_move += index_1_count
                        index_3_move += index_1_count

                        # loop index advance index_1_move + index_1_count
                        if(index_2_count == 0):
                            x += (index_1_move+index_1_count+index_2_move)
                            index_1_count = index_3_count
                            index_1_move = index_3_move

                            index_2_count = 0
                            index_2_move = 0
                            index_3_count = 0
                            index_3_move = 0

                            value += 2
                            continue

                        elif(index_3_count == 0):

                            remain.extend([(value+1)
                                          for i in range(index_2_count)])

                            x += (index_1_move+index_1_count +
                                  index_2_move+index_2_count+index_3_move)

                            # full reset
                            index_1_count = 0
                            index_1_move = 0
                            index_2_count = 0
                            index_2_move = 0
                            index_3_count = 0
                            index_3_move = 0

                            continue

                        else:
                            x += (index_1_move+index_1_count)
                            # index_1 = index_2, index_2 = index_3, index_3 = 0
                            index_1_count = index_2_count
                            index_1_move = index_2_move
                            index_2_count = index_3_count
                            index_2_move = index_3_move
                            index_3_count = 0
                            index_3_move = 0
                            value += 1
                            continue

                    elif (index_2_count <= index_1_count and index_2_count <= index_3_count):

                        index_1_count -= index_2_count
                        index_3_count -= index_2_count
                        index_1_move += index_2_count
                        index_3_move += index_2_count

                        remain.extend([value for i in range(index_1_count)])
                        if(index_3_count == 0):
                            x += (index_1_move + index_1_count +
                                  index_2_move + index_2_count + index_3_move)

                            # full reset
                            index_1_count = 0
                            index_2_count = 0
                            index_3_count = 0
                            index_1_move = 0
                            index_2_move = 0
                            index_3_move = 0
                            continue

                        else:
                            x += (index_1_move + index_1_count +
                                  index_2_count + index_2_move)
                            index_1_count = index_3_count
                            index_1_move = index_3_move
                            index_2_count = 0
                            index_2_move = 0
                            index_3_count = 0
                            index_3_move = 0
                            value += 2
                            continue

                    elif (index_3_count <= index_1_count and index_3_count <= index_2_count):

                        # remaining
                        index_1_count -= index_3_count
                        index_2_count -= index_3_count

                        index_1_move += index_3_count
                        index_2_move += index_3_count

                        remain.extend([value for i in range(index_1_count)])
                        remain.extend([(value+1)
                                      for i in range(index_2_count)])
                        # move index by the tile
                        x += (index_1_move + index_1_count + index_2_move +
                              index_2_count + index_3_count + index_3_move)

                        # full reset
                        index_1_count = 0
                        index_2_count = 0
                        index_3_count = 0
                        index_1_move = 0
                        index_2_move = 0
                        index_3_move = 0
                        continue

            x += (index_1_count + index_1_move)
            remain.extend([value for i in range(index_1_count)])
            # print("# of index 1 added to remain "+ str(index_1_count))
            index_1_count = index_2_count
            index_1_move = index_2_move
            index_2_count = index_3_count
            index_2_move = index_3_move
            index_3_count = 0
            index_3_move = 0
            value += 1

        # seq_extract v1.0
        # remain = []
        # remain.extend(hand[0:index])
        # duplicate = []
        # x = index
        # while x < (len(hand)-2):
        #     if(hand[x]//9 == hand[x+2]//9):
        #         while(hand[x] == hand[x+1] or hand[x+1] == hand[x+2]):
        #             if(hand[x] == hand[x+1]):
        #                 hand.count

        #         if(hand[x]+2 == hand[x+1]+1 == hand[x+2]):
        #             x+=3
        #             continue

        #     remain.append(hand[x])
        #     x+=1
        x += (index_1_move + index_2_move + index_3_move)

        if(x < len(partial_hand)-1):
            remain.append(partial_hand[x+1])
        if(x <= len(partial_hand)-1):
            remain.append(partial_hand[x])
        # print("extract seq:")
        # print(remain)
        return sorted(remain)

    def single_handParti(self, attr):
        current_list = self.hands[attr]

        for x in range(len(current_list)):

            self.efficiency_map.setdefault(str(attr*9+x), 0)
            if(current_list[x] == 4):
                # 1 KAN or 1 triplet + possible sequence
                self.partition.setdefault("KAN-triplet", [])
                self.partition["KAN-triplet"].append(attr*9+x)

            if(current_list[x] == 3):
                # 1 triplet or 1 pair + possible sequence
                self.partition.setdefault("triplet", [])
                self.partition["triplet"].append(attr*9+x)
            if(current_list[x] == 2):
                # 1 pair
                self.partition.setdefault("pair", [])
                self.partition["pair"].append(attr*9+x)

            if(x == 7 and current_list[x] >= 1):
                if(current_list[x-1] == 0 and current_list[x+1] >= 1):
                    self.partition.setdefault("sequence_one-way", [])
                    self.partition["sequence_one-way"].append(attr*9+x-1)

            if(x < len(current_list)-2 and current_list[x] >= 1):
                if(current_list[x+1] == 0 and current_list[x+2]):
                    # sequence middle
                    self.partition.setdefault("sequence_middle", [])
                    self.partition["sequence_middle"].append(attr*9+x)
                if(current_list[x+1] >= 1 and current_list[x+2] == 0):
                    # sequence two-way
                    if(x == 0):
                        self.partition.setdefault("sequence_one-way", [])
                        self.partition["sequence_one-way"].append(attr*9+x)
                    else:
                        self.partition.setdefault("sequence_two-way", [])
                        self.partition["sequence_two-way"].append(attr*9+x)
                if(current_list[x+1] >= 1 and current_list[x+2] >= 1):
                    # sequence complete
                    self.partition.setdefault("sequence_complete", [])
                    self.partition["sequence_complete"].append(attr*9+x)

                else:
                    self.partition.setdefault("single", [])
                    self.partition["single"].append(attr*9+x)
            elif(current_list[x] == 1):
                self.partition.setdefault("single", [])
                self.partition["single"].append(attr*9+x)

    # print tiles that are used in all the possible partitions

    def used_tile(self):
        used_tile_list = {}
        self.efficiency_map = defaultdict(int)
        for key in self.partition:
            for index in self.partition[key]:
                if("middle" in key):
                    self.efficiency_map[index] += 1
                    self.efficiency_map[index+2] += 1
                elif("two-way" in key):
                    self.efficiency_map[index] += 1
                    self.efficiency_map[index+1] += 1
                else:
                    self.efficiency_map[index] += 1
        print(self.efficiency_map)
        return used_tile_list

    # print tiles that are needed for incomplete sequences
    def tile_needed(self, input):
        waiting_tile_list = []
        for index in self.partition[input]:
            if("pair" in input or "single" in input):
                # get remaining tile at certain location
                # modify efficiency map value based on remaining tile
                value = self.remaining_tile(index) * 0.1
                self.efficiency_map[str(index)] += value

                waiting_tile_list.append(index)
            if("middle" in input):
                waiting_tile_list.append(index+1)
            if("two-way" in input):
                # can add a condition check to eliminate negative index
                waiting_tile_list.append(index-1)
                waiting_tile_list.append(index+2)
            if("one-way" in input):
                if(index % 9 == 0):
                    waiting_tile_list.append(index+2)
                else:
                    waiting_tile_list.append(index)
        waiting_tile_list.sort()
        return waiting_tile_list

    def tile_use_count(self):
        for t in self.partition:
            for index in self.partition[t]:
                if("two-way" in t):
                    self.efficiency_map[str(index-1)] += 1
                    self.efficiency_map[str(index)] += 1
                    self.efficiency_map[str(index+1)] += 1
                elif("sequence" in t):
                    self.efficiency_map[str(index)] += 1
                    self.efficiency_map[str(index+1)] += 1
                    self.efficiency_map[str(index+2)] += 1
                else:
                    self.efficiency_map[str(index)] += 1

    def tile_efficiency(self):
        # get the lowest value(s) from the efficiency map
        # if multiple
        return None

    def partition_dict(self, hand, parti_type):
        return_dict = {}
        if("seq" in parti_type):
            # sequence
            hand_1 = self.seq_extract(hand, 0)
            temp_list = self.locate_index(hand, hand_1, True)
            seq_dict = self.inc_seq_extract(hand_1)

            return_dict.setdefault("seq-complete", temp_list)
            return_dict.setdefault("seq-two-way", seq_dict["seq-two-way"])
            return_dict.setdefault("seq-one-way", seq_dict["seq-one-way"])
            return_dict.setdefault("seq-middle", seq_dict["seq-middle"])

            # triplet
            hand_2 = self.tri_extract(hand_1)
            temp_list_2 = self.locate_index(hand_1, hand_2, False)
            return_dict.setdefault("triplet", temp_list_2)

            # pair
            hand_3 = self.pair_extract(hand_2)
            temp_list_3 = self.locate_index(hand_2, hand_3, False)
            return_dict.setdefault("pair", temp_list_3)
            return_dict.setdefault("single", hand_3)

        elif("tri" in parti_type):
            # triplet
            hand_1 = self.tri_extract(hand)
            temp_list = self.locate_index(hand, hand_1, False)
            return_dict.setdefault("triplet", temp_list)

            # sequence
            hand_2 = self.seq_extract(hand_1, 0)
            temp_list_2 = self.locate_index(hand_1, hand_2, True)
            return_dict.setdefault("seq-complete", temp_list_2)

            seq_dict = self.inc_seq_extract(hand_2)
            return_dict.setdefault("seq-two-way", seq_dict["seq-two-way"])
            return_dict.setdefault("seq-one-way", seq_dict["seq-one-way"])
            return_dict.setdefault("seq-middle", seq_dict["seq-middle"])

            # pair
            hand_3 = self.pair_extract(hand_2)
            temp_list_3 = self.locate_index(hand_2, hand_3, False)
            return_dict.setdefault("pair", temp_list_3)
            return_dict.setdefault("single", hand_3)

        else:
            # seven pairs
            hand_1 = self.pair_extract(hand)
            temp_list = self.locate_index(hand, hand_1, False)
            return_dict.setdefault("pair", temp_list)
            return_dict.setdefault("single", hand_1)

        # print(return_dict)
        return return_dict

    def locate_index(self, hand_bef, hand_aft, isSeq):
        return_list = []
        index = 0
        diff = []
        # find the difference
        while index < len(hand_bef):
            value = hand_bef[index]
            count_after = hand_aft.count(value)
            count_before = hand_bef.count(value)
            if(count_after < count_before):
                diff.extend([value for i in range(count_before-count_after)])
                index += count_before
            else:
                index += 1

        if(isSeq == False):
            return_list = list(dict.fromkeys(diff))
            return return_list

        # the tile value
        tile = 0
        while tile < 25:
            if (len(diff) == 0):
                break

            num_tile_1 = diff.count(tile)
            if(num_tile_1 == 0):
                tile += 1
                continue

            elif(diff.count(tile+1) > 0 and diff.count(tile+2) > 0):
                return_list.append(tile)
                diff.remove(tile)
                diff.remove(tile+1)
                diff.remove(tile+2)

            else:
                tile += 1

        return return_list

    def inc_seq_extract(self, hand):
        return_dict = {}
        return_dict.setdefault("seq-two-way", [])
        return_dict.setdefault("seq-one-way", [])
        return_dict.setdefault("seq-middle", [])
        x = 0
        while x < 25:
            first_tile = hand.count(x)
            if(first_tile > 0):
                second_tile = 0
                third_tile = 0

                # only valid if the tiles are the same types
                if(x // 9 == (x+1) // 9):
                    second_tile = hand.count(x+1)
                if(x // 9 == (x+2) // 9):
                    third_tile = hand.count(x+2)

                # if there are two consecutive tiles
                if(second_tile > 0):
                    if(x % 9 == 0 or x % 9 == 8):
                        return_dict["seq-one-way"].extend(
                            [x]*min(first_tile, second_tile))
                    else:
                        return_dict["seq-two-way"].extend(
                            [x]*min(first_tile, second_tile))

                    x += 1

                elif(third_tile > 0):
                    if((x+2) // 9 == (x+3) // 9 and hand.count(x+3) == 0):
                        return_dict["seq-middle"].extend([x]
                                                         * min(first_tile, third_tile))

                    if(third_tile == 1 and hand.count(x+3) == 0):
                        x += 1

            x += 1

        return return_dict

    # 1. Determine a list of goals for the yaku (by the tile distance and needed tile remaining to calculate the possibility) and have a threshold.
    def yaku_goal_list(self, yaku_dict):
        prob_dict = {}
        for yaku in yaku_dict:
            num_waiting = yaku_dict[yaku][0]
            waiting_tile_list = yaku_dict[yaku][1]
            partition_str = yaku_dict[yaku][3]
            poss = 1
            # 1 - (1-p1)*(1-p2)
            # p1*p2
            choice_list = []
            for item in waiting_tile_list:
                if(type(item) is int):
                    print(item)
                    temp_p = 1 - \
                        (1 - (self.tile_count[item]/self.num_remain_tile))**5
                    choice_list.append(temp_p)

                else:
                    temp_total = 0
                    for index in item:
                        temp_total += self.tile_count[index]
                    temp_p = 1 - (1 - (temp_total/self.num_remain_tile))**5
                    choice_list.append(temp_p)

            sorted(choice_list, reverse=True)
            i = 0
            for item in choice_list:
                poss *= item
                i += 1
                if (i >= num_waiting):
                    break

            print(yaku, ':', poss)
            prob_dict.setdefault(yaku, poss)

        print(prob_dict)

    # 2. Determine the tiles used in these yaku, modified by the possibility of that yaku and the point value to give these tile a weight.
        # yaku that are set up as goals
        tile_weight_dict = {}
        for yaku in prob_dict:
            prob = prob_dict[yaku]
            # calculate yaku's point value
            # 1 han
            used_tile_list = yaku_dict[yaku][2]
            print(yaku)
            print(used_tile_list)
            han, seq, tri = self.han_seq_tri_getter(yaku)
            point_value = self.point_calculation(30, han)

            for tile in used_tile_list:
                if(tile in tile_weight_dict):
                    tile_weight_dict[tile] += point_value*prob
                else:
                    tile_weight_dict.setdefault(tile, point_value*prob)

    # 3. For incomplete seq or single tile, calculate the possibility of some sort of advancing (for example, from single tile to seq-two-way, or from seq-one-way to seq-two-way etc). Give tiles weight based on that possibility. Then we have a list of tiles with weight, the one with the least weight should be the least important.
        partition = self.partition_dict(self.hand, 'seq')
        point_value = self.point_calculation(30, 1)
        for tile in partition['seq-two-way']:
            total_remain = self.tile_count_getter(
                tile-1) + self.tile_count_getter(tile+2)
            prob_weight = total_remain / self.num_remain_tile * point_value
            if(tile in tile_weight_dict):
                tile_weight_dict[tile] += prob_weight
            else:
                tile_weight_dict.setdefault(tile, prob_weight)
            if((tile+1) in tile_weight_dict):
                tile_weight_dict[tile+1] += prob_weight
            else:
                tile_weight_dict.setdefault(tile+1, prob_weight)

        for tile in partition['seq-one-way']:
            if(tile % 9 == 0):
                total_remain = self.tile_count_getter(tile+2)
            else:
                total_remain = self.tile_count_getter(tile-1)
            prob_weight = total_remain / self.num_remain_tile * point_value
            if(tile in tile_weight_dict):
                tile_weight_dict[tile] += prob_weight
            else:
                tile_weight_dict.setdefault(tile, prob_weight)
            if((tile+1) in tile_weight_dict):
                tile_weight_dict[tile+1] += prob_weight
            else:
                tile_weight_dict.setdefault(tile+1, prob_weight)

        for tile in partition['seq-middle']:
            prob_weight = self.tile_count_getter(
                tile+1) / self.num_remain_tile * point_value
            if(tile in tile_weight_dict):
                tile_weight_dict[tile] += prob_weight
            else:
                tile_weight_dict.setdefault(tile, prob_weight)
            if((tile+2) in tile_weight_dict):
                tile_weight_dict[tile+2] += prob_weight
            else:
                tile_weight_dict.setdefault(tile+2, prob_weight)

        for tile in partition['pair']:
            prob_weight = self.tile_count_getter(
                tile) / self.num_remain_tile * point_value
            if(tile in tile_weight_dict):
                tile_weight_dict[tile] += prob_weight
            else:
                tile_weight_dict.setdefault(tile, prob_weight)

        for tile in partition['single']:
            prob = self.tile_count_getter(tile) / self.num_remain_tile
            if(tile in tile_weight_dict):
                tile_weight_dict[tile] += prob
            else:
                tile_weight_dict.setdefault(tile, prob)

        return tile_weight_dict

    def predict_opponent(self, opponent_num):
        input = np.zeros((14, 47))
        opponent = self.gameboard.opponent_getter(opponent_num)
        mlp = pickle.load(open('mlp_model.sav', 'rb'))
        for i in range(14):
            tile = self.hand[i]
            tile_attr = tile // 9
            tile_num = tile % 9
            input[i][34 + tile_attr] = 1
            input[i][37 + tile_num] = 1

            for discard in opponent.discard_getter():
                input[i][discard] = 1

        prediction = mlp.predict_proba(input)

        return prediction

    def to_discard_tile(self):
        ma = Mahjong_AI.Mahjong_AI()
        partition_seq = self.partition_dict(self.hand, 'seq')
        print('Partition: ', partition_seq)

        partition_tri = self.partition_dict(self.hand, 'tri')
        partition_pair = self.partition_dict(self.hand, 'pair')
        yaku_dict = self.yaku_check(
            partition_seq, partition_tri, partition_pair, self.open_meld)
        print('Yaku_dict: ', yaku_dict)

        tile_weight = self.yaku_goal_list(yaku_dict)
        print('Tile_weight_dict: ', tile_weight)

        min_weight = np.inf
        min_tile = None
        for tile in tile_weight:
            if (tile_weight[tile] < min_weight):
                min_weight = tile_weight[tile]
                min_tile = tile

        return min_tile

    def try_to_call_meld(self, tile136, might_call_chi):

        return None, None

    def should_call_kan(self, tile136, from_opponent):

        return False, False

    def can_call_reach(self):

        return False, 0

    def han_seq_tri_getter(self, han_string):
        if('pinfu' in han_string):
            return 1, 4, 0

        if('all-simple' in han_string):
            return 1, 0, 0

        if('honor-yaku' in han_string):
            return 1, 0, 1

        if('two-identical-seq' in han_string):
            return 1, 2, 0

        if('straight' in han_string):
            return 2, 3, 0

        if('3-color-seq' in han_string):
            return 2, 3, 0

        if('3-color-triplet' in han_string):
            return 2, 0, 3

        if('all_triplet' in han_string):
            return 2, 0, 4

        if('terminal_in_all' in han_string):
            return 2, 0, 0

        if('seven_pairs' in han_string):
            return 2, -1, -1

        if('riichi' in han_string):
            return 1, 0, 0

    def point_calculation(self, fu, han):
        if(han <= 4):
            basic_points = fu*2**(han+2)
            if(basic_points > 2000):
                return 2000
            else:
                return basic_points

        elif(han == 5):
            return 2000

        elif(han <= 7):
            return 3000

        elif(han <= 10):
            return 4000

        elif(han <= 12):
            return 6000

        else:
            return 8000

    def tile_count_getter(self, index):
        return self.tile_count[index]

    def tile_count_update(self, index):
        self.tile_count[index] -= 1

    def hand_add(self, tile):
        self.hand.append(tile)
        sorted(self.hand)

    def hand_discard(self, tile):
        self.hand.remove(tile)

    def hand_getter(self):
        return self.hand

    def yaku_check(self, partition_seq, partition_triplet, partition_pair, meld):
        NO_TERMINAL_HONOR_TILES = [
            1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26]
        return_dict = {}
        num_waiting = 0
        tiles_needed_list = []
        tiles_used_list = []
        # 1. pinfu
        # condition: all concealed hand, 3 seq-complete, 1 seq-two-way, 1 pair
        if len(meld) == 0:
            num_waiting = 1
            num_seq_com = len(partition_seq['seq-complete'])
            if num_seq_com > 3:
                num_waiting = 99
            else:  # +2 waiting tiles for every seq-com under 3
                num_waiting = num_waiting + ((3 - num_seq_com) * 2)
                for x in partition_seq['seq-complete']:
                    tiles_used_list.append(x)
                    tiles_used_list.append(x + 1)
                    tiles_used_list.append(x + 2)
                num_waiting = num_waiting - len(partition_seq['seq-middle'])
                for x in partition_seq['seq-middle']:
                    tiles_needed_list.append(x + 1)  # need index tile + 1
                    num_waiting = num_waiting + 1
                    tiles_used_list.append(x)
                    tiles_used_list.append(x + 2)
                for x in partition_seq['seq-one-way']:
                    if x % 9 == 0:  # 123 one way
                        tiles_needed_list.append(x + 2)
                        num_waiting = num_waiting + 1
                        tiles_used_list.append(x)
                        tiles_used_list.append(x + 1)
                    else:  # 789 one way
                        tiles_needed_list.append(x - 1)
                        num_waiting = num_waiting + 1
                        tiles_used_list.append(x)
                        tiles_used_list.append(x + 1)
            num_seq_two = len(partition_seq['seq-two-way'])
            if num_seq_two == 0:
                num_waiting = num_waiting + 1  # need +1 tiles to make two
                for x in partition_seq['single']:
                    mod_var = x % 9
                    if 7 > mod_var > 1 and x < 26:
                        # every single needs + or - 1 to become 2-way
                        tiles_needed_list.append([x-1, x+1])
                        tiles_used_list.append(x)

            else:  # -1 waiting tile for every two-way-seq over the needed 1
                num_waiting = num_waiting - num_seq_two
                for x in partition_seq['seq-two-way']:
                    # each 2-way is waiting for x-1 or x+2
                    tiles_needed_list.append([x-1, x+2])
                    tiles_used_list.append(x)
                    tiles_used_list.append(x + 1)
                    num_waiting = num_waiting + 1
            if len(partition_seq['pair']) == 0:  # add 1 if there is no pair
                num_waiting = num_waiting + 1
                for t in partition_seq['single']:
                    possible_pairs_list = []
                    if t not in tiles_used_list:
                        possible_pairs_list.append(t)
                    tiles_needed_list.extend(possible_pairs_list)
                    tiles_used_list.extend(possible_pairs_list)
            elif len(partition_seq['pair']) > 1:
                num_waiting = num_waiting + len(partition_seq['pair']) - 1
                for t in partition_seq['pair']:
                    if 7 > t % 9 > 1 and t < 26:
                        tiles_needed_list.extend([t + 1, t + 2, t - 1, t - 2])
                    elif t % 9 == 7:
                        tiles_needed_list.extend([t + 1, t - 1, t - 2])
                    elif t % 9 == 8:
                        tiles_needed_list.extend([t - 1, t - 2])
                    elif t % 9 == 1:
                        tiles_needed_list.extend([t - 1, t + 1, t + 2])
                    elif t % 9 == 0:
                        tiles_needed_list.extend([t + 1, t + 2])
                    tiles_used_list.append(t)
            else:
                for t in partition_seq['pair']:
                    tiles_used_list.append(t)
                    tiles_used_list.append(t)
            if num_waiting > len(tiles_needed_list):
                temp_single_list = partition_seq['single'][:]
                try:
                    for t in partition_seq['seq-two-way']:
                        temp_single_list.remove(t)
                        temp_single_list.remove(t + 1)
                    for t in partition_seq['seq-one-way']:
                        temp_single_list.remove(t)
                        temp_single_list.remove(t + 1)
                    for t in partition_seq['seq-middle']:
                        temp_single_list.remove(t)
                        temp_single_list.remove(t + 2)
                except ValueError:
                    pass
                for t in temp_single_list:
                    if 7 > t % 9 > 1 and t < 26:
                        tiles_needed_list.extend([t + 1, t + 2, t - 1, t - 2])
                    elif t % 9 == 7:
                        tiles_needed_list.extend([t + 1, t - 1, t - 2])
                    elif t % 9 == 8:
                        tiles_needed_list.extend([t - 1, t - 2])
                    elif t % 9 == 1:
                        tiles_needed_list.extend([t - 1, t + 1, t + 2])
                    elif t % 9 == 0:
                        tiles_needed_list.extend([t + 1, t + 2])
                for t in partition_seq['triplet']:
                    if 6 > t % 9 > 2 and t < 26:
                        tiles_needed_list.extend([t + 1, t + 2, t - 1, t - 2])
                    elif t % 9 == 7:
                        tiles_needed_list.extend([t + 1, t - 1, t - 2])
                    elif t % 9 == 1:
                        tiles_needed_list.extend([t - 1, t + 1, t + 2])
                if num_waiting > len(tiles_needed_list):
                    num_waiting = 99
        else:
            num_waiting = 99
        return_dict.setdefault("pinfu", [num_waiting, tuple(
            tiles_needed_list), tuple(tiles_used_list), 'seq'])
        num_waiting = 0
        tiles_needed_list.clear()
        tiles_used_list.clear()

        # 2. all simple
        # condition: check each partition's index != 1 or 9 or honor, and for sequence, index+1 and index+2 if necessary
        triplet_num_waiting = 0
        seq_num_waiting = 0
        temp_waiting_list = []
        temp_used_list = []
        return_str = ""
        for k, v in partition_triplet.items():
            for tile in v:
                mod_var = tile % 9
                if mod_var == 0 or mod_var == 8 or tile > 26:
                    triplet_num_waiting = triplet_num_waiting + 1
                    if k == 'triplet':
                        triplet_num_waiting = triplet_num_waiting + 2
                    elif k == 'pair':
                        triplet_num_waiting = triplet_num_waiting + 1
                else:
                    if 'seq' not in k:
                        tiles_used_list.append(tile)
                    if k == 'triplet':
                        tiles_used_list.append(tile)
                        tiles_used_list.append(tile)
                    elif k == 'pair':
                        tiles_used_list.append(tile)
                        if len(v) > 1:  # can complete pair for triplet
                            triplet_num_waiting = triplet_num_waiting + \
                                len(v) - 1
                            tiles_needed_list.append(tile)
                if k == 'seq-complete':
                    if mod_var == 6:  # 789 sequence
                        triplet_num_waiting = triplet_num_waiting + 1
                        tiles_needed_list.append(tile - 1)  # need tile 6
                        tiles_used_list.append(tile)
                        tiles_used_list.append(tile + 1)
                    if mod_var == 0:  # 123 sequence
                        tiles_needed_list.append(tile + 3)  # need tile 4
                        tiles_used_list.append(tile + 1)
                        tiles_used_list.append(tile + 2)
                    else:
                        tiles_used_list.append(tile)
                        tiles_used_list.append(tile + 1)
                        tiles_used_list.append(tile + 2)
                elif k == 'seq-one-way':
                    if mod_var == 0:  # Have already added 1 waiting tile in previous check
                        triplet_num_waiting = triplet_num_waiting + 1
                        tiles_needed_list.extend([tile+2, tile+3])  # need 3, 4
                        # tiles_used_list.append(tile + 1)
                    else:
                        triplet_num_waiting = triplet_num_waiting + 2
                        tiles_needed_list.extend([tile-1, tile-2])  # need 7, 6
                        # tiles_used_list.append(tile)
                elif k == 'seq-two-way':
                    if mod_var == 6:  # 78 two way
                        triplet_num_waiting = triplet_num_waiting + 1
                        tiles_needed_list.append(tile - 1)
                        # tiles_used_list.append(tile)
                        # tiles_used_list.append(tile + 1)
                    elif mod_var == 1:  # 23 two way
                        triplet_num_waiting = triplet_num_waiting + 1
                        tiles_needed_list.append(tile + 2)
                        # tiles_used_list.append(tile)
                        # tiles_used_list.append(tile + 2)
                    else:
                        triplet_num_waiting = triplet_num_waiting + 1
                        tiles_needed_list.append([tile-1, tile+2])
                        # tiles_used_list.append(tile)
                        # tiles_used_list.append(tile + 1)
                elif k == 'seq-middle':
                    if mod_var == 6:  # 7_9 sequence
                        triplet_num_waiting = triplet_num_waiting + 2
                        tiles_needed_list.extend([tile+1, tile-1])  # need 6, 8
                        # tiles_used_list.append(tile)
                    elif mod_var == 0:  # 1_3 sequence
                        triplet_num_waiting = triplet_num_waiting + 1  # already added one from before
                        tiles_needed_list.extend([tile+1, tile+3])
                        # tiles_used_list.append(tile+2)
                    else:
                        triplet_num_waiting = triplet_num_waiting + 1
                        tiles_needed_list.append(tile + 1)  # need middle tile
                        # tiles_used_list.append(tile)
                        # tiles_used_list.append(tile + 2)
        for k, v in partition_seq.items():
            for tile in v:
                mod_var = tile % 9
                if mod_var == 0 or mod_var == 8 or tile > 26:
                    seq_num_waiting = seq_num_waiting + 1
                    if k == 'pair':
                        seq_num_waiting = seq_num_waiting + 1
                    elif k == 'triplet':
                        seq_num_waiting = seq_num_waiting + 2
                else:
                    temp_used_list.append(tile)
                    if k == 'triplet':
                        temp_used_list.append(tile)
                        temp_used_list.append(tile)
                    elif k == 'pair':
                        temp_used_list.append(tile)
                        if len(v) > 1:
                            seq_num_waiting = seq_num_waiting + len(v) - 1
                            temp_waiting_list.append(tile)
                if k == 'seq-complete':
                    if mod_var == 6:  # 789 sequence
                        seq_num_waiting = seq_num_waiting + 1
                        temp_waiting_list.append(tile - 1)  # need tile 6
                        temp_used_list.append(tile)
                        temp_used_list.append(tile + 1)
                    if mod_var == 0:  # 123 sequence
                        temp_waiting_list.append(tile + 3)  # need tile 4
                        temp_used_list.append(tile + 1)
                        temp_used_list.append(tile + 2)
                elif k == 'seq-one-way':
                    if mod_var == 0:  # Have already added 1 waiting tile in previous check
                        seq_num_waiting = seq_num_waiting + 1
                        temp_waiting_list.extend([tile+2, tile+3])  # need 3, 4
                        # temp_used_list.append(tile + 1)
                    else:
                        seq_num_waiting = seq_num_waiting + 2
                        temp_waiting_list.extend([tile-1, tile-2])  # need 7, 6
                        # temp_used_list.append(tile)
                elif k == 'seq-two-way':
                    if mod_var == 6:  # 78 two way
                        seq_num_waiting = seq_num_waiting + 1
                        temp_waiting_list.append(tile - 1)
                        # temp_used_list.append(tile)
                        # temp_used_list.append(tile + 1)
                    elif mod_var == 1:  # 23 two way
                        seq_num_waiting = seq_num_waiting + 1
                        temp_waiting_list.append(tile + 2)
                        # temp_used_list.append(tile)
                        # temp_used_list.append(tile + 2)
                    else:
                        seq_num_waiting = seq_num_waiting + 1
                        temp_waiting_list.append([tile-1, tile+2])
                        # temp_used_list.append(tile)
                        # temp_used_list.append(tile + 1)
                elif k == 'seq-middle':
                    if mod_var == 6:  # 7_9 sequence
                        seq_num_waiting = seq_num_waiting + 2
                        temp_waiting_list.extend([tile+1, tile-1])  # need 6, 8
                        # temp_used_list.append(tile)
                    elif mod_var == 0:  # 1_3 sequence
                        seq_num_waiting = seq_num_waiting + 1  # already added one from before
                        temp_waiting_list.extend([tile+1, tile+3])
                        # temp_used_list.append(tile+2)
                    else:
                        seq_num_waiting = seq_num_waiting + 1
                        temp_waiting_list.append(tile + 1)  # need middle tile
                        # temp_used_list.append(tile)
                        # temp_used_list.append(tile + 2)
        if seq_num_waiting < triplet_num_waiting:
            num_waiting = seq_num_waiting
            tiles_needed_list = temp_waiting_list[:]
            tiles_used_list = temp_used_list[:]
            return_str = 'seq'
        else:
            num_waiting = triplet_num_waiting
            return_str = 'tri'
        if num_waiting > len(tiles_needed_list):
            tiles_needed_list.append(NO_TERMINAL_HONOR_TILES[:])
        return_dict.setdefault(
            'all-simple', [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), return_str])
        num_waiting = 0
        tiles_needed_list.clear()
        tiles_used_list.clear()

        # 3. honor yaku
        # condition: check if honor triplet exist
        num_waiting = 99  # if no honor tiles in hand, it will be an empy list
        for t in partition_triplet['single']:
            if t >= 27:
                num_waiting = 2
                tiles_needed_list.append(t)
                tiles_needed_list.append(t)
                tiles_used_list.append(t)
        for t in partition_triplet['pair']:
            if t >= 27:
                num_waiting = 1
                tiles_needed_list.clear()
                tiles_used_list.clear()
                tiles_needed_list.append(t)
                tiles_used_list.append(t)
                tiles_used_list.append(t)
        if any(t >= 27 for t in partition_triplet['triplet']):
            num_waiting = 0
            tiles_needed_list.clear()
            tiles_used_list.append(t)
            tiles_used_list.append(t)
            tiles_used_list.append(t)
        return_dict.setdefault(
            'honor-yaku', [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'tri'])
        num_waiting = 0
        tiles_needed_list.clear()
        tiles_used_list.clear()

        # 4. two identical seq
        # condition: all concealed hand, 2 seq with same index
        # current only checks partial seq with eachother, not checking singles etc
        if len(meld) == 0:
            num_waiting = 6
            for suit in range(2):
                suit_offset = suit * 9
                for i in range(7):
                    temp_waiting = 6
                    temp_waiting_list = [i, i+1, i+2, i, i+1, i+2]
                    temp_waiting_list = [
                        t + suit_offset for t in temp_waiting_list]
                    temp_used_list = []

                    for tile in partition_seq['seq-complete']:
                        if tile % 9 == i:
                            if tile in temp_waiting_list:
                                temp_waiting -= 3
                                temp_waiting_list.remove(tile)
                                temp_waiting_list.remove(tile+1)
                                temp_waiting_list.remove(tile+2)
                                temp_used_list.append(tile)
                                temp_used_list.append(tile+1)
                                temp_used_list.append(tile+2)

                    for tile in partition_seq['triplet']:
                        if tile % 9 in [i, i+1, i+2]:
                            if tile in temp_waiting_list:
                                temp_waiting -= 1
                                temp_waiting_list.remove(tile)
                                temp_used_list.append(tile)

                    for tile in partition_seq['pair']:
                        if tile % 9 in [i, i+1, i+2]:
                            if tile in temp_waiting_list:
                                temp_waiting -= 1
                                temp_waiting_list.remove(tile)
                                temp_used_list.append(tile)

                    for tile in partition_seq['single']:
                        if tile % 9 in [i, i+1, i+2]:
                            if tile in temp_waiting_list:
                                temp_waiting -= 1
                                temp_waiting_list.remove(tile)
                                temp_used_list.append(tile)
                    if num_waiting > temp_waiting:
                        num_waiting = temp_waiting
                        tiles_needed_list = temp_waiting_list[:]
                        tiles_used_list = temp_used_list[:]
        else:
            num_waiting = 99
        return_dict.setdefault(
            'two-identical-seq', [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'seq'])
        num_waiting = 0
        tiles_needed_list.clear()
        tiles_used_list.clear()
        ## above Christoph 1-4 ##

        # 5. straight
        # condtion: 3 seq with index 0, 3, 6
        if len(meld) > 1:  # if > 1 exposed triplet
            num_waiting = 99
        # 3 arrays (9 total tiles per suit)
        # seq-complete partition check (ID suit; modify array) --> singles, pairs, and triplets (check for tiles in similar range (variable-- if yes))
        else:
            closestS = 0
            num_waiting = 9
            straight_counts = [0] * 3
            suit_wan = [0] * 9
            suit_pin = [0] * 9
            suit_sou = [0] * 9

            for k, v in partition_seq.items():  # unique tile counted = 1, else 0
                for tile in v:
                    if tile < 27:
                        if 'seq-complete' in k:
                            if tile < 7:
                                suit_wan[tile] = suit_wan[tile +
                                                          1] = suit_wan[tile + 2] = 1

                            elif 8 < tile < 16:
                                suit_pin[(tile % 9)] = suit_pin[(
                                    tile % 9) + 1] = suit_pin[(tile % 9) + 2] = 1

                            else:
                                suit_sou[(tile % 9)] = suit_sou[(
                                    tile % 9) + 1] = suit_sou[(tile % 9) + 2] = 1

                        if 'single' or 'pair' or 'triplet' in k and (tile < 27):
                            if tile < 9:
                                suit_wan[tile] = 1

                            elif 8 < tile < 16:
                                suit_pin[(tile % 9)] = 1

                            else:
                                suit_sou[(tile % 9)] = 1

            # get the suit with the most unique tiles counted
            straight_counts[0] = suit_wan.count(1)
            straight_counts[1] = suit_pin.count(1)
            straight_counts[2] = suit_sou.count(1)

            if (num_waiting > (9 - straight_counts[0])):
                num_waiting = 9 - straight_counts[0]
                closestS = 0
            if (num_waiting > (9 - straight_counts[1])):
                num_waiting = 9 - straight_counts[1]
                closestS = 1
            if (num_waiting > (9 - straight_counts[2])):
                num_waiting = 9 - straight_counts[0]
                closestS = 2

            if num_waiting == 9:  # if all honors
                num_waiting = 99

            else:
                if closestS == 0:  # append to waiting and used tiles lists
                    for i in range(0, 9):
                        if suit_wan[i] == 0:
                            tiles_needed_list.append(i)
                        else:
                            tiles_used_list.append(i)

                if closestS == 1:
                    for i in range(0, 9):
                        if suit_pin[i] == 0:
                            tiles_needed_list.append((i + 9))
                        else:
                            tiles_used_list.append((i + 9))

                if closestS == 2:
                    for i in range(0, 9):
                        if suit_sou[i] == 0:
                            tiles_needed_list.append((i + 18))
                        else:
                            tiles_used_list.append((i + 18))

            return_dict.setdefault("straight", [num_waiting, tuple(
                tiles_needed_list), tuple(tiles_used_list), 'seq'])
            num_waiting = 0
            tiles_needed_list.clear()
            tiles_used_list.clear()

        # 6. three color seq
        # condition: 3 seq with the same index after mod 9
        if(len(meld) < 2):
            min_waiting = 9
            waiting_tiles_list = ()
            used_tiles_list = ()

            for i in range(7):
                waiting_count = 9
                temp_wait_list = [i, i+1, i+2, i +
                                  9, i+10, i+11, i+18, i+19, i+20]
                temp_use_list = []
                for index in partition_seq['seq-complete']:
                    if (index % 9 == i):
                        if index in temp_wait_list:
                            waiting_count -= 3
                            temp_wait_list.remove(index)
                            temp_wait_list.remove(index+1)
                            temp_wait_list.remove(index+2)
                            temp_use_list.append(index)
                            temp_use_list.append(index+1)
                            temp_use_list.append(index+2)

                for index in partition_seq['triplet']:
                    if (index % 9 == i):
                        if(index in temp_wait_list):
                            waiting_count -= 1
                            temp_wait_list.remove(index)
                            temp_use_list.append(index)

                for index in partition_seq['pair']:
                    if(index % 9 == i):
                        if(index in temp_wait_list):
                            waiting_count -= 1
                            temp_wait_list.remove(index)
                            temp_use_list.append(index)

                for index in partition_seq['single']:
                    if (index % 9 >= i and index % 9 <= i+2):
                        if(index in temp_wait_list):
                            waiting_count -= 1
                            temp_wait_list.remove(index)
                            temp_use_list.append(index)

                if(waiting_count < min_waiting):
                    min_waiting = waiting_count
                    waiting_tiles_list = tuple(temp_wait_list)
                    used_tiles_list = tuple(temp_use_list)

            value_list = [min_waiting, waiting_tiles_list,
                          used_tiles_list, 'seq']
            return_dict.setdefault('3-color-seq', value_list)

        # 7. three color triplet
        # condition: 3 triplet with the same index
        num_waiting = 9
        tiles_needed_list = []
        tiles_used_list = []
        if len(meld) > 1:  # if > 1 exposed sequence
            num_waiting = 99

        else:
            closest_index = 0
            suit_wanT = [0] * 9
            suit_pinT = [0] * 9
            suit_souT = [0] * 9
            closestT = [0] * 9

            for k, v in partition_triplet.items():  # find and store # of tiles at indexes respective to suits
                for tile in v:
                    if tile < 27:
                        if 'triplet' in k:
                            if tile < 9:
                                suit_wanT[tile] += 3

                            elif 8 < tile < 18:
                                suit_pinT[(tile % 9)] += 3

                            else:
                                suit_souT[(tile % 9)] += 3

                        if 'pair' in k:
                            if tile < 9:
                                suit_wanT[tile] += 2

                            elif 8 < tile < 18:
                                suit_pinT[(tile % 9)] += 2

                            else:
                                suit_souT[(tile % 9)] += 2

                        if 'single' in k:
                            if tile < 9:
                                suit_wanT[tile] += 1

                            elif 8 < tile < 18:
                                suit_pinT[(tile % 9)] += 1

                            else:
                                suit_souT[(tile % 9)] += 1

                        if 'seq-complete' in k:
                            if tile < 7:
                                suit_wanT[tile] += 1
                                suit_wanT[(tile + 1)] += 1
                                suit_wanT[(tile + 2)] += 1

                            elif 8 < tile < 16:
                                suit_pinT[(tile % 9)] += 1
                                suit_pinT[((tile % 9) + 1)] += 1
                                suit_pinT[((tile % 9) + 2)] += 1

                            else:
                                suit_souT[(tile % 9)] += 1
                                suit_souT[((tile % 9) + 1)] += 1
                                suit_souT[((tile % 9) + 2)] += 1

            for i in range(0, 9):  # find and store the closest 3-color-triplet setup
                closestT[i] = [suit_wanT[i], suit_pinT[i], suit_souT[i],
                               (suit_wanT[i] + suit_pinT[i] + suit_souT[i])]
                if (9 - closestT[i][3]) < 0:
                    closestT[i][3] = 9
                if num_waiting > (9 - closestT[i][3]):
                    num_waiting = 9 - closestT[i][3]
                    closest_index = i

            if num_waiting == 9:  # if all honors
                num_waiting = 99

            else:
                for i in range(0, 3):  # append needed & used tiles lists
                    if closestT[closest_index][i] < 3:
                        if i == 0:
                            for j in range(0, (3 - closestT[closest_index][i])):
                                tiles_needed_list.append(closest_index)
                            for j in range(0, closestT[closest_index][i]):
                                tiles_used_list.append(closest_index)

                        if i == 1:
                            for j in range(0, (3 - closestT[closest_index][i])):
                                tiles_needed_list.append(closest_index + 9)
                            for j in range(0, closestT[closest_index][i]):
                                tiles_used_list.append(closest_index + 9)

                        if i == 2:
                            for j in range(0, (3 - closestT[closest_index][i])):
                                tiles_needed_list.append(closest_index + 18)
                            for j in range(0, closestT[closest_index][i]):
                                tiles_used_list.append(closest_index + 18)

                    # 3 or 4 tiles under value i in a suit (no need to append needed tiles list)
                    else:
                        if i == 0:
                            for j in range(0, 3):
                                tiles_used_list.append(closest_index)

                        if i == 1:
                            for j in range(0, 3):
                                tiles_used_list.append(closest_index + 9)

                        if i == 2:
                            for j in range(0, 3):
                                tiles_used_list.append(closest_index + 18)

            return_dict.setdefault(
                "3-color-triplet", [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'tri'])
            num_waiting = 0
            tiles_needed_list.clear()
            tiles_used_list.clear()

        ## above Dane  5-7 ##

        tiles_needed_list = []
        tiles_used_list = []

        tri_num_pair = len(partition_triplet['pair'])
        tri_num_triplet = len(partition_triplet['triplet'])
        #tri_num_seq = len(partition_triplet['seq-complete'])
        need_tri = 0

        pair_num_pair = len(partition_pair['pair'])

        # 8. all triplet
        # condition: 4 triplet ( or quads) with 1 pair
        if tri_num_triplet == 4:  # 4 tri
            num_waiting = 0
            need_tri = 0
        else:  # less than 4 tri
            need_tri = 4 - tri_num_triplet  # triplet to complete
            num_waiting = need_tri * 2
            if(need_tri - tri_num_pair < 0):
                num_waiting = tri_num_pair + 2 * (need_tri - tri_num_pair)
            else:
                num_waiting = num_waiting - tri_num_pair  # -1 for each extra pair
        for k, v in partition_triplet.items():
            for index in v:
                if 'triplet' in k:
                    tiles_used_list.extend([index, index, index])
                if 'pair' in k:
                    if need_tri > 0:
                        tiles_used_list.extend([index, index])
                        tiles_needed_list.extend([index])
                if 'single' in k:
                    if ((need_tri - tri_num_pair) > 0):
                        tiles_used_list.extend([index])
                        tiles_needed_list.extend([index])
        return_dict.setdefault("all_triplet", [num_waiting, tuple(
            tiles_needed_list), tuple(tiles_used_list), 'tri'])

        # 9. terminal in all meld
        # condition: (seq + triplet) = 4, index is 1 or 9 or honor, for seq check index+1 and index+2
        num_com = 0
        num_almost = 0
        num_two = 0
        pair_used = 0
        tiles_needed_list.clear()
        tiles_used_list.clear()
        tiles_needed_list_almost = []
        tiles_needed_list_two = []
        tiles_used_list_almost = []
        tiles_used_list_two = []
        temp_used = []

        for k, v in partition_seq.items():
            for index in v:
                if 'triplet' in k:
                    if index < 27:
                        if((index % 9) in (0, 8)):  # 111 OR 999
                            num_com = num_com + 1
                            tiles_used_list.extend([index, index, index])
                    else:  # Honor
                        num_com = num_com + 1
                        tiles_used_list.extend([index, index, index])
                if index < 27:
                    if 'seq-complete' in k:
                        if ((index % 9) in (0, 6)):  # 123 OR 789
                            num_com = num_com + 1
                            tiles_used_list.extend([index, index+1, index+2])
                        if ((index % 9) in (1, 5)):  # 234 OR 678
                            num_almost = num_almost + 1
                            if ((index % 9) == 1):
                                tiles_used_list_almost.extend(
                                    [index, index + 1])  # 23
                                tiles_needed_list_almost.extend([index - 1])
                            if ((index % 9) == 5):
                                tiles_used_list_almost.extend(
                                    [index + 1, index + 2])  # 78
                                tiles_needed_list_almost.extend([index + 3])
                        if ((index % 9) in (2, 4)):  # 345 OR 567
                            num_two = num_two + 1
                            if ((index % 9) == 2):
                                tiles_used_list_two.extend([index])  # 3
                                tiles_needed_list_two.extend(
                                    [index - 2, index - 1])  # 12
                            if ((index % 9) == 4):
                                tiles_used_list_two.extend([index + 2])  # 7
                                tiles_needed_list_two.extend(
                                    [index + 3, index + 4])  # 89
                    if 'seq-one-way' in k:  # 12(3) OR (7)89
                        if ((index % 9) == 0):  # 12(3)
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend([index + 2])  # 3
                            temp_used.extend([index, index + 1])
                            tiles_used_list_almost.extend([index, index + 1])
                        if ((index % 9) == 7):  # (7)89
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend(index - 1)  # 7
                            temp_used.extend([index, index + 1])
                            tiles_used_list_almost.extend([index, index + 1])
                    if 'seq-two-way' in k:  # (1)23 OR 78(9)
                        if ((index % 9) == 1):  # (1)23
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend([index - 1])  # 1
                            temp_used.extend([index, index + 1])
                            tiles_used_list_almost.extend([index, index + 1])
                        if ((index % 9) == 6):  # 78(9)
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend([index + 2])  # 9
                            temp_used.extend([index, index + 1])
                            tiles_used_list_almost.extend([index, index + 1])
                    if 'seq-middle' in k:  # 1(2)3 OR 7(8)9
                        if ((index % 9) == 0):  # 1(2)3
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend([index + 1])  # 2
                            temp_used.extend([index, index + 2])
                            tiles_used_list_almost.extend([index, index + 2])
                        if ((index % 9) == 6):  # 7(8)9
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend([index + 1])  # 8
                            temp_used.extend([index, index + 2])
                            tiles_used_list_almost.extend([index, index + 2])
                    if 'pair' in k:
                        if((index % 9) in (0, 8)):  # 11 or 99
                            num_almost = num_almost + 1
                            pair_used = pair_used + 1
                            tiles_needed_list_almost.extend([index])  # 1 or 9
                            tiles_used_list_almost.extend([index, index])
                    if 'single' in k:
                        if index not in temp_used:
                            if((num_com + num_almost) < 4):
                                if((index % 9) in (0, 6)):  # 1 or 7
                                    num_two = num_two + 1
                                    tiles_needed_list_two.extend(
                                        [index + 1, index + 2])  # 23 or 89
                                    tiles_used_list_two.extend([index])
                                if((index % 9) in (1, 7)):  # 2 or 8
                                    num_two = num_two + 1
                                    tiles_needed_list_two.extend(
                                        [index - 1, index + 1])  # 13 or 79
                                    tiles_used_list_two.extend([index])
                                if((index % 9) in (2, 8)):  # 3 or 9
                                    num_two = num_two + 1
                                    tiles_needed_list_two.extend(
                                        [index - 1, index - 2])  # 12 or 78
                                    tiles_used_list_two.extend([index])
                else:
                    if 'pair' in k:  # honor pair
                        num_almost = num_almost + 1
                        pair_used = pair_used + 1
                        tiles_needed_list_almost.extend([index])  # 1 or 9
                        tiles_used_list_almost.extend([index, index])
                    if 'single' in k:  # honor single
                        if index not in temp_used:
                            if((num_com + num_almost) < 4):
                                num_two = num_two + 1
                                tiles_needed_list_two.extend([index, index])
                                tiles_used_list_two.extend([index])

        needed_com = 4 - num_com
        if needed_com > 0:
            if ((needed_com - num_almost) < 1):
                num_waiting = needed_com
                tiles_used_list.extend(tiles_used_list_almost)
                tiles_needed_list.extend(tiles_needed_list_almost)
            elif ((needed_com - num_almost - num_two) < 1):
                needed_com = needed_com - num_almost
                num_waiting = num_almost + (2 * needed_com)
                tiles_used_list.extend(tiles_used_list_almost)
                tiles_used_list.extend(tiles_used_list_two)
                tiles_needed_list.extend(tiles_needed_list_almost)
                tiles_needed_list.extend(tiles_needed_list_two)
            else:
                needed_com = needed_com - num_almost - num_two
                num_waiting = num_almost + (2 * num_two) + (3 * needed_com)
                tiles_used_list.extend(tiles_used_list_almost)
                tiles_used_list.extend(tiles_used_list_two)
                tiles_needed_list.extend(tiles_needed_list_almost)
                tiles_needed_list.extend(tiles_needed_list_two)
        else:
            num_waiting = 0
        return_dict.setdefault("terminal_in_all", [num_waiting, tuple(
            tiles_needed_list), tuple(tiles_used_list), 'seq'])
        tiles_used_list_almost.clear()
        tiles_used_list_two.clear()
        tiles_needed_list_almost.clear()
        tiles_needed_list_two.clear()
        tiles_used_list_almost.clear()
        tiles_used_list_two.clear()

        # 10. seven pair
        # condition: 7 pair partition
        tiles_needed_list.clear()
        tiles_used_list.clear()
        temp_used.clear()
        if len(meld) == 0:
            if pair_num_pair < 7:
                num_waiting = 7 - pair_num_pair
                for k, v in partition_pair.items():
                    for index in v:
                        if ('pair' in k):
                            tiles_used_list.extend([index, index])
                        if ('single' in k):
                            tiles_needed_list.extend([index])
            else:
                num_waiting = 0
        else:
            num_waiting = 99
        return_dict.setdefault("seven_pairs", [num_waiting, tuple(
            tiles_needed_list), tuple(tiles_used_list), 'pair'])
        tiles_needed_list.clear()
        tiles_used_list.clear()
        ## above Lee 8-10 ##
        # Riichi Check # need 4 melds and 1 pair
        return_str = ''
        num_melds = len(partition_seq['seq-complete']
                        ) + len(partition_seq['triplet'])
        num_pair = 1 if (len(partition_seq['pair']) > 0) else 0
        seq_num_waiting = 14 - (num_melds * 3 + num_pair * 2)

        num_melds = len(
            partition_triplet['seq-complete']) + len(partition_triplet['triplet'])
        num_pair = 1 if (len(partition_seq['pair']) > 0) else 0
        triplet_num_waiting = 14 - (num_melds * 3 + num_pair * 2)
        closest_partition = partition_seq if seq_num_waiting < triplet_num_waiting else partition_triplet
        num_waiting = seq_num_waiting if seq_num_waiting < triplet_num_waiting else triplet_num_waiting
        return_str = 'seq' if seq_num_waiting < triplet_num_waiting else 'tri'
        pairs_list = []

        for t in closest_partition['seq-complete']:
            tiles_used_list.extend([t, t + 1, t + 2])
        for t in closest_partition['triplet']:
            tiles_used_list.extend([t, t, t])
        if len(closest_partition['pair']) > 1:
            for t in closest_partition['pair']:
                pairs_list.extend([t, t])
            tiles_used_list.extend(pairs_list)
        elif len(closest_partition['pair']) == 1:
            t = closest_partition['pair'][0]
            tiles_used_list.extend([t, t])
        return_dict.setdefault("riichi", [num_waiting, tuple(
            tiles_needed_list), tuple(tiles_used_list), return_str])

        return return_dict


# dummy = MahjongAgent(GameBoard())
# hand = [0, 0, 1, 1, 2, 2, 4, 4, 7, 7, 9, 9, 20, 30]
# hand_2 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
# hand_3 = [2, 3, 4, 6, 7, 8, 13, 14, 15, 16, 16, 19, 20, 23]
# hand_4 = [9, 10, 12, 13, 14, 19, 20, 21, 23, 24, 25, 30, 30, 31]
# hand_5 = [1, 2, 3, 4, 4, 4, 5, 6, 7, 7, 7, 9, 10, 12]
# hand_6 = [2, 2, 3, 3, 3, 4, 4, 4, 5, 11, 12]
# hand_7 = [2, 2, 3, 4, 5, 5, 12, 13, 13, 14, 14, 15, 22, 23]
# hand_test = [3, 4, 10, 10, 11, 12, 21, 21, 21, 26, 26, 26, 28, 28]

# yaku_check = {'pinfu': [2, [3, 7], [1, 2, 3], 'seq'], 'all-simple': [3,
#                                                                      [13, 15, 23], [3, 4, 5], 'seq'], 'tanyaou': [1, [6], [3, 6, 9], 'seq']}
# return_dict = dummy.tenpai_status_check(hand_test)
# print(list(return_dict.keys())[0])

# 3, 3, 5, 5, 5, 12, 13, 14, 18, 19, 21, 22, 23, 23
# 2, 11, 12, 13, 20, 21, 22, 28, 28, 29, 29
# imp 2, 2, 3, 4, 5, 5, 12, 13, 13, 14, 14, 15, 22, 23
# 1, 2, 2, 3, 12, 12, 19, 20, 21, 22, 23, 23, 24, 25
# 2, 3, 4, 12, 12, 14, 15, 16, 31, 31, 31
# 2, 2, 2, 4, 5, 6, 13, 14, 15, 16, 16, 21, 22, 23
# 3,3,4,4,5,5,5,6,6

# print(dummy.tenpai_status_check(hand_test))


# dummy = MahjongAgent()
# dummy.single_handParti(0)
# dummy.single_handParti(1)
# dummy.single_handParti(2)
# dummy.tile_use_count()
# print(len(dummy.partition))
# print(dummy.partition)
# print(dummy.tile_needed())
# print(dummy.efficiency_map)
