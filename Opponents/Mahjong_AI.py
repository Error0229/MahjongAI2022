class Mahjong_AI:
    # hand_partition, meld: list of tuple(partition_str,index_int)
    # hand_partition ex: {seq-complete:[start_tile_seq1, start_tile_seq2, etch],  pair:tile}

    # return dict : {yaku_name: [num_waiting,[waiting_tiles_list], tiles_used_list], partition_used}
    def yaku_check(self,partition_seq, partition_triplet, partition_pair,meld):
        NO_TERMINAL_HONOR_TILES = [1,2,3,4,5,6,7,10,11,12,13,14,15,16,19,20,21,22,23,24,25,26]
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
            else: # +2 waiting tiles for every seq-com under 3
                num_waiting = num_waiting + ((3 - num_seq_com) * 2)
                for x  in partition_seq['seq-complete']:
                    tiles_used_list.append(x)
                    tiles_used_list.append(x + 1)
                    tiles_used_list.append(x + 2)
                num_waiting = num_waiting - len(partition_seq['seq-middle'])
                for x in partition_seq['seq-middle']:
                    tiles_needed_list.append(x + 1) # need index tile + 1
                    num_waiting = num_waiting + 1
                    tiles_used_list.append(x)
                    tiles_used_list.append(x + 2)
                for x in partition_seq['seq-one-way']:
                    if x % 9 == 0: # 123 one way
                        tiles_needed_list.append(x + 2)
                        num_waiting = num_waiting + 1
                        tiles_used_list.append(x)
                        tiles_used_list.append(x + 1)
                    else: # 789 one way
                        tiles_needed_list.append(x - 1)
                        num_waiting = num_waiting + 1
                        tiles_used_list.append(x)
                        tiles_used_list.append(x + 1)
            num_seq_two = len(partition_seq['seq-two-way'])
            if num_seq_two == 0: 
                num_waiting = num_waiting + 1 # need +1 tiles to make two
                for x in partition_seq['single']:
                    mod_var = x % 9
                    if 7 > mod_var > 1 and x < 26:
                        tiles_needed_list.append([x-1, x+1]) # every single needs + or - 1 to become 2-way
                        tiles_used_list.append(x)

            else: # -1 waiting tile for every two-way-seq over the needed 1
                num_waiting = num_waiting - num_seq_two
                for x in partition_seq['seq-two-way']:
                    tiles_needed_list.append([x-1, x+2]) # each 2-way is waiting for x-1 or x+2
                    tiles_used_list.append(x)
                    tiles_used_list.append(x + 1)
                    num_waiting = num_waiting + 1
            if len(partition_seq['pair']) == 0: #add 1 if there is no pair
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
        else: num_waiting = 99
        return_dict.setdefault("pinfu", [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'seq'])
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
                        if len(v) > 1: #can complete pair for triplet
                            triplet_num_waiting = triplet_num_waiting + len(v) - 1
                            tiles_needed_list.append(tile)
                if k == 'seq-complete':
                    if mod_var == 6: # 789 sequence
                        triplet_num_waiting = triplet_num_waiting + 1
                        tiles_needed_list.append(tile - 1) # need tile 6
                        tiles_used_list.append(tile)
                        tiles_used_list.append(tile + 1)
                    if mod_var == 0: # 123 sequence
                        tiles_needed_list.append(tile + 3) # need tile 4
                        tiles_used_list.append(tile + 1)
                        tiles_used_list.append(tile + 2)
                    else:
                        tiles_used_list.append(tile)
                        tiles_used_list.append(tile + 1)
                        tiles_used_list.append(tile + 2)
                elif k == 'seq-one-way':
                    if mod_var == 0: # Have already added 1 waiting tile in previous check
                        triplet_num_waiting = triplet_num_waiting + 1
                        tiles_needed_list.extend([tile+2, tile+3]) # need 3, 4
                        # tiles_used_list.append(tile + 1)
                    else:
                        triplet_num_waiting = triplet_num_waiting + 2
                        tiles_needed_list.extend([tile-1, tile-2]) # need 7, 6
                        # tiles_used_list.append(tile)
                elif k == 'seq-two-way':
                    if mod_var == 6: #78 two way
                        triplet_num_waiting = triplet_num_waiting + 1
                        tiles_needed_list.append(tile - 1)
                        # tiles_used_list.append(tile)
                        # tiles_used_list.append(tile + 1)
                    elif mod_var == 1: #23 two way
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
                    if mod_var == 6: # 7_9 sequence 
                        triplet_num_waiting = triplet_num_waiting + 2
                        tiles_needed_list.extend([tile+1, tile-1]) # need 6, 8
                        # tiles_used_list.append(tile)
                    elif mod_var == 0: # 1_3 sequence
                        triplet_num_waiting = triplet_num_waiting + 1 # already added one from before
                        tiles_needed_list.extend([tile+1, tile+3])
                        # tiles_used_list.append(tile+2)
                    else:
                        triplet_num_waiting = triplet_num_waiting + 1
                        tiles_needed_list.append(tile + 1) # need middle tile
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
                    if mod_var == 6: # 789 sequence
                        seq_num_waiting = seq_num_waiting + 1
                        temp_waiting_list.append(tile - 1) # need tile 6
                        temp_used_list.append(tile)
                        temp_used_list.append(tile + 1)
                    if mod_var == 0: # 123 sequence
                        temp_waiting_list.append(tile + 3) # need tile 4
                        temp_used_list.append(tile + 1)
                        temp_used_list.append(tile + 2)
                elif k == 'seq-one-way':
                    if mod_var == 0: # Have already added 1 waiting tile in previous check
                        seq_num_waiting = seq_num_waiting + 1
                        temp_waiting_list.extend([tile+2, tile+3]) # need 3, 4
                        # temp_used_list.append(tile + 1)
                    else:
                        seq_num_waiting = seq_num_waiting + 2
                        temp_waiting_list.extend([tile-1, tile-2]) # need 7, 6
                        # temp_used_list.append(tile)
                elif k == 'seq-two-way':
                    if mod_var == 6: #78 two way
                        seq_num_waiting = seq_num_waiting + 1
                        temp_waiting_list.append(tile - 1)
                        # temp_used_list.append(tile)
                        # temp_used_list.append(tile + 1)
                    elif mod_var == 1: #23 two way
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
                    if mod_var == 6: # 7_9 sequence 
                        seq_num_waiting = seq_num_waiting + 2
                        temp_waiting_list.extend([tile+1, tile-1]) # need 6, 8
                        # temp_used_list.append(tile)
                    elif mod_var == 0: # 1_3 sequence
                        seq_num_waiting = seq_num_waiting + 1 # already added one from before
                        temp_waiting_list.extend([tile+1, tile+3])
                        # temp_used_list.append(tile+2)
                    else:
                        seq_num_waiting = seq_num_waiting + 1
                        temp_waiting_list.append(tile + 1) # need middle tile
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
        return_dict.setdefault('all-simple', [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), return_str])
        num_waiting = 0
        tiles_needed_list.clear()
        tiles_used_list.clear()

        # 3. honor yaku
        # condition: check if honor triplet exist
        num_waiting = 99 # if no honor tiles in hand, it will be an empy list
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
        return_dict.setdefault('honor-yaku', [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'tri'])
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
                    temp_waiting_list = [t + suit_offset for t in temp_waiting_list]
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
                    if  num_waiting > temp_waiting:
                        num_waiting = temp_waiting
                        tiles_needed_list = temp_waiting_list[:]
                        tiles_used_list = temp_used_list[:]        
        else: num_waiting = 99
        return_dict.setdefault('two-identical-seq', [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'seq'])
        num_waiting = 0
        tiles_needed_list.clear()
        tiles_used_list.clear()
        ## above Christoph 1-4 ##

        # 5. straight
        # condtion: 3 seq with index 0, 3, 6
        if len(meld) > 1: # if > 1 exposed triplet
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

            for k, v in partition_seq.items(): # unique tile counted = 1, else 0
                for tile in v:
                    if tile < 27:
                        if 'seq-complete' in k:
                            if tile < 7:
                                suit_wan[tile] = suit_wan[tile + 1] = suit_wan[tile + 2] = 1
                                
                            elif 8 < tile < 16:
                                suit_pin[(tile % 9)] = suit_pin[(tile % 9) + 1] = suit_pin[(tile % 9) + 2] = 1

                            else:
                                suit_sou[(tile % 9)] = suit_sou[(tile % 9) + 1] = suit_sou[(tile % 9) + 2] = 1
                                    
                        if 'single' or 'pair' or 'triplet' in k and (tile < 27):
                            if tile < 9:
                                suit_wan[tile] = 1
                                        
                            elif 8 < tile < 18:
                                suit_pin[(tile % 9)] = 1

                            else:
                                suit_sou[(tile % 9)] = 1

            straight_counts[0] = suit_wan.count(1) # get the suit with the most unique tiles counted
            straight_counts[1] = suit_pin.count(1)
            straight_counts[2] = suit_sou.count(1)

            if (num_waiting > (9 - straight_counts[0])):
                num_waiting = 9 - straight_counts[0]
                closestS = 0
            if (num_waiting > (9 - straight_counts[1])):
                num_waiting = 9 - straight_counts[1]
                closestS = 1
            if (num_waiting > (9 - straight_counts[2])):
                num_waiting = 9 - straight_counts[2]
                closestS = 2

            if num_waiting == 9: # if all honors
                num_waiting = 99

            else:
                if closestS == 0: # append to waiting and used tiles lists
                    for i in range (0, 9):
                        if suit_wan[i] == 0:
                            tiles_needed_list.append(i)
                        else:
                            tiles_used_list.append(i)

                if closestS == 1:
                    for i in range (0, 9):
                        if suit_pin[i] == 0:
                            tiles_needed_list.append((i + 9))
                        else:
                            tiles_used_list.append((i + 9))

                if closestS == 2:
                    for i in range (0, 9):
                        if suit_sou[i] == 0:
                            tiles_needed_list.append((i + 18))
                        else:
                            tiles_used_list.append((i + 18))

            return_dict.setdefault("straight", [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'seq'])
            num_waiting = 0
            tiles_needed_list.clear()
            tiles_used_list.clear()

        # 6. three color seq
        # condition: 3 seq with the same index after mod 9
        if(len(meld)<2):
            min_waiting = 9
            waiting_tiles_list = ()
            used_tiles_list = ()

            for i in range(7):
                waiting_count = 9
                temp_wait_list = [i,i+1,i+2,i+9,i+10,i+11,i+18,i+19,i+20]
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

            
            value_list = [min_waiting, waiting_tiles_list, used_tiles_list, 'seq']
            return_dict.setdefault('3-color-seq', value_list)     

        # 7. three color triplet
        # condition: 3 triplet with the same index
        num_waiting = 9
        tiles_needed_list = []
        tiles_used_list = []    
        if len(meld) > 1: # if > 1 exposed sequence
            num_waiting = 99

        else:
            closest_index = 0
            suit_wanT = [0] * 9
            suit_pinT = [0] * 9
            suit_souT = [0] * 9
            closestT = [0] * 9

            for k, v in partition_triplet.items(): # find and store # of tiles at indexes respective to suits
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

            for i in range (0, 9): # find and store the closest 3-color-triplet setup
                closestT[i] = [suit_wanT[i], suit_pinT[i], suit_souT[i], (suit_wanT[i] + suit_pinT[i] + suit_souT[i])]
                if (9 - closestT[i][3]) < 0:
                    closestT[i][3] = 9
                if  num_waiting > (9 - closestT[i][3]):
                    num_waiting = 9 - closestT[i][3]
                    closest_index = i

            if num_waiting == 9: # if all honors
                num_waiting = 99

            else:
                for i in range (0, 3): # append needed & used tiles lists
                    if closestT[closest_index][i] < 3:
                        if i == 0:
                            for j in range (0, (3 - closestT[closest_index][i])):
                                tiles_needed_list.append(closest_index)
                            for j in range (0, closestT[closest_index][i]):
                                tiles_used_list.append(closest_index)

                        if i == 1:
                            for j in range (0, (3 - closestT[closest_index][i])):
                                tiles_needed_list.append(closest_index + 9)
                            for j in range (0, closestT[closest_index][i]):
                                tiles_used_list.append(closest_index + 9)

                        if i == 2:
                            for j in range (0, (3 - closestT[closest_index][i])):
                                tiles_needed_list.append(closest_index + 18)
                            for j in range (0, closestT[closest_index][i]):
                                tiles_used_list.append(closest_index + 18)

                    else: # 3 or 4 tiles under value i in a suit (no need to append needed tiles list)
                        if i == 0:
                            for j in range (0, 3):
                                tiles_used_list.append(closest_index)

                        if i == 1:
                            for j in range (0, 3):
                                tiles_used_list.append(closest_index + 9)

                        if i == 2:
                            for j in range (0, 3):
                                tiles_used_list.append(closest_index + 18)

            return_dict.setdefault("3-color-triplet", [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'tri'])
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
        if tri_num_triplet == 4: # 4 tri
            num_waiting = 0
            need_tri = 0
        else: # less than 4 tri
            need_tri = 4 - tri_num_triplet # triplet to complete
            num_waiting = need_tri * 2
            if(need_tri - tri_num_pair < 0):
                num_waiting = tri_num_pair + 2 * (need_tri - tri_num_pair) 
            else: 
                num_waiting = num_waiting - tri_num_pair # -1 for each extra pair            
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
        return_dict.setdefault("all_triplet", [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'tri'])

        # 9. terminal in all meld
        # condition: (seq + triplet) = 4, index is 1 or 9 or honor, for seq check index+1 and index+2 
        num_waiting = 0
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
                        if((index % 9) in (0, 8)): # 111 OR 999
                            num_com = num_com + 1
                            tiles_used_list.extend([index, index, index])
                    else: # Honor
                        num_com = num_com + 1
                        tiles_used_list.extend([index, index, index])
                if index < 27:       
                    if 'seq-complete' in k: 
                        if ((index % 9) in (0, 6)): # 123 OR 789
                            num_com = num_com + 1
                            tiles_used_list.extend([index, index+1, index+2])
                        if ((index % 9) in (1, 5)): # 234 OR 678
                            num_almost = num_almost + 1
                            if ((index % 9) == 1):
                                tiles_used_list_almost.extend([index, index + 1]) #23
                                tiles_needed_list_almost.extend([index - 1]) 
                            if ( (index % 9) == 5):
                                tiles_used_list_almost.extend([index + 1, index + 2]) #78
                                tiles_needed_list_almost.extend([index + 3])
                        if ((index % 9) in (2, 4)): # 345 OR 567
                            num_two = num_two + 1
                            if ((index % 9) == 2):
                                tiles_used_list_two.extend([index]) #3
                                tiles_needed_list_two.extend([index - 2, index - 1]) #12
                            if ((index % 9)== 4):
                                tiles_used_list_two.extend([index + 2]) #7
                                tiles_needed_list_two.extend([index + 3, index + 4]) #89         
                    if 'seq-one-way' in k: # 12(3) OR (7)89     
                        if ((index % 9) == 0): # 12(3)
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend([index + 2]) # 3
                            temp_used.extend([index, index + 1])
                            tiles_used_list_almost.extend([index, index + 1])
                        if ((index % 9) == 7): # (7)89
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend(index - 1) # 7
                            temp_used.extend([index, index + 1])
                            tiles_used_list_almost.extend([index, index + 1])
                    if 'seq-two-way' in k: # (1)23 OR 78(9) 
                        if ((index % 9) == 1): # (1)23
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend([index - 1]) # 1
                            temp_used.extend([index, index + 1])
                            tiles_used_list_almost.extend([index, index + 1])
                        if ((index % 9) == 6): # 78(9)
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend([index + 2]) # 9
                            temp_used.extend([index, index + 1])
                            tiles_used_list_almost.extend([index, index + 1])                      
                    if 'seq-middle' in k: # 1(2)3 OR 7(8)9
                        if ((index % 9) == 0): # 1(2)3
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend([index + 1]) # 2
                            temp_used.extend([index, index + 2])
                            tiles_used_list_almost.extend([index, index + 2])
                        if ((index % 9) == 6): # 7(8)9
                            num_almost = num_almost + 1
                            tiles_needed_list_almost.extend([index + 1]) # 8
                            temp_used.extend([index, index + 2])
                            tiles_used_list_almost.extend([index, index + 2])                     
                    if 'pair' in k:
                        if((index % 9) in (0, 8)): #11 or 99
                            num_almost = num_almost + 1
                            pair_used = pair_used + 1
                            tiles_needed_list_almost.extend([index]) # 1 or 9
                            tiles_used_list_almost.extend([index, index])
                    if 'single' in k:
                        if index not in temp_used:
                            if((num_com + num_almost) < 4):
                                if((index % 9) in (0, 6)): # 1 or 7             
                                    num_two = num_two + 1 
                                    tiles_needed_list_two.extend([index + 1, index + 2]) #23 or 89
                                    tiles_used_list_two.extend([index])
                                if((index % 9) in (1, 7)): # 2 or 8
                                    num_two = num_two + 1
                                    tiles_needed_list_two.extend([index - 1, index + 1]) #13 or 79
                                    tiles_used_list_two.extend([index])                       
                                if((index % 9) in (2, 8)): #3 or 9
                                    num_two = num_two + 1
                                    tiles_needed_list_two.extend([index - 1, index - 2]) #12 or 78
                                    tiles_used_list_two.extend([index])
                else:
                    if 'pair' in k: # honor pair
                        num_almost = num_almost + 1
                        pair_used = pair_used + 1
                        tiles_needed_list_almost.extend([index]) # 1 or 9
                        tiles_used_list_almost.extend([index, index])
                    if 'single' in k: # honor single
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
        return_dict.setdefault("terminal_in_all", [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'seq'])
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
            else: num_waiting = 0                     
        else: num_waiting = 99         
        return_dict.setdefault("seven_pairs", [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), 'pair'])
        tiles_needed_list.clear()
        tiles_used_list.clear()        
        ## above Lee 8-10 ##
        ## Riichi Check # need 4 melds and 1 pair
        return_str = ''
        num_melds = len(partition_seq['seq-complete']) + len(partition_seq['triplet'])
        num_pair = 1 if (len(partition_seq['pair']) > 0) else 0
        seq_num_waiting = 14 - (num_melds * 3 + num_pair * 2)

        num_melds = len(partition_triplet['seq-complete']) + len(partition_triplet['triplet'])
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
        return_dict.setdefault("riichi", [num_waiting, tuple(tiles_needed_list), tuple(tiles_used_list), return_str])
        
        return return_dict

    def is_riichi(self, hand_partition, meld):
        num_melds = len(hand_partition['seq-complete']) + len(hand_partition['triplet']) + len(meld)
        num_pairs = len(hand_partition['pair'])
        return (num_melds == 4 and num_pairs == 1)
        

def main():
    mai = Mahjong_AI()
    partition_seq = {'seq-complete':[1, 5], 'seq-middle': [], 'seq-two-way': [], 'pair': [5,7], 
                        'triplet': [20], 'single': [17], 'seq-one-way': []}
    partition_triplet = {'seq-complete':[1, 5], 'seq-middle': [], 'seq-two-way': [], 'pair': [5,7], 
                        'triplet': [20], 'single': [17], 'seq-one-way': []}
    partition_pair = {'seq-complete':[1, 5], 'seq-middle': [], 'seq-two-way': [], 'pair': [5,7], 
                        'triplet': [20], 'single': [17], 'seq-one-way': []}                                                
    meld = []
    print(mai.yaku_check(partition_seq, partition_triplet, partition_pair, meld))


if __name__ == '__main__':
    main()
