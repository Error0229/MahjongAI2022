from Game.LocalGame import FullGame
import matplotlib.pyplot as plt
import numpy as np

def GameLogCollect(game):
    '''
    WIP:
    ron chance, make_other_ron chance
    
    player_log:
        shaintin: list of list of int
        legal_predict: list of list of int
        ron_cnt: int
        houjuu_cnt: int
        tsumo_cnt: int
        tenpai_cnt: int

    game_log:
        rank: list of 4 int
        score: list of 4 int
        liuju_cnt: int
        round_cnt: int
    '''
    res = {}
    
    res['shantin'] = [game.players[i].player_log['shantin'] for i in range(4)]
    res['legal_predict'] = [game.players[i].player_log['legal_predict'] for i in range(4)]
    res['ron_cnt'] = [game.players[i].player_log['ron_cnt'] for i in range(4)]
    res['houjuu_cnt'] = [game.players[i].player_log['houjuu_cnt'] for i in range(4)]
    res['tsumo_cnt'] = [game.players[i].player_log['tsumo_cnt'] for i in range(4)]
    res['tenpai_cnt'] = [game.players[i].player_log['tenpai_cnt'] for i in range(4)]
    res['rank'] = game.game_log['rank']
    res['score'] = game.game_log['score']
    res['liuju_cnt'] = game.game_log['liuju_cnt']
    res['round_cnt'] = game.game_log['round_cnt']
    return res

def AnalyzeResult(data):
    # only show the score chart of the first game
    player_names = ['cnn0', 'greedy0', 'cnn1', 'greedy1']
    game_count = len(data)
    
    def show_shantin_chart():
        lst = [[], [], [], []]
        for player_id in range(4):
            for game_id in range(game_count):
                lst[player_id] += data[game_id]['shantin'][player_id]

        res = [[], [], [], []]
        action_cnts = [0, 0, 0, 0]
        is_left = True
        i = 0
        while(is_left):
            is_left = False
            for player_id in range(4):
                cnt_shantin = 0
                sum_shantin = 0
                for llst in lst[player_id]:
                    if(i<len(llst)):
                        sum_shantin += llst[i]
                        cnt_shantin += 1
                        is_left = True
                if(cnt_shantin>0):
                    action_cnts[player_id] += 1
                    res[player_id].append(sum_shantin/cnt_shantin)
            i += 1

        fig, ax = plt.subplots(2, 2)
        for player_id in range(4):
            sub_ax = ax[player_id//2][player_id%2]
            sub_ax.set(xlabel='action', ylabel='shantin', title=player_names[player_id])
            sub_ax.set_yticks(np.arange(0, 7, 1))
            sub_ax.set_ylim(0, 6)
            sub_ax.set_xticks(np.arange(0, action_cnts[player_id], 1))
            sub_ax.tick_params(axis="both", direction="in")
            sub_ax.plot(res[player_id])
        plt.show()
        
    def show_legal_chart():
        lst = [[], [], [], []]
        for player_id in range(4):
            for game_id in range(game_count):
                lst[player_id] += data[game_id]['legal_predict'][player_id]
        
        res = [[], [], [], []]
        predict_cnts = [0, 0, 0, 0]
        is_left = True
        i = 0
        while(is_left):
            is_left = False
            for player_id in range(4):
                cnt_predict = 0
                sum_predict = 0
                for llst in lst[player_id]:
                    if(i<len(llst)):
                        sum_predict += (llst[i]==-1)
                        cnt_predict += 1
                        is_left = True
                if(cnt_predict>0):
                    predict_cnts[player_id] += 1
                    res[player_id].append(sum_predict/cnt_predict)
            i += 1
        
        fig, ax = plt.subplots(2, 2)
        for player_id in range(4):
            sub_ax = ax[player_id//2][player_id%2]
            sub_ax.set(xlabel='predict', ylabel='legal', title=player_names[player_id])
            sub_ax.set_yticks(np.arange(0, 1.01, 0.1))
            sub_ax.set_yticklabels([f'{i:.0%}' for i in np.arange(0, 1.01, 0.1)])
            sub_ax.set_ylim(0, 1)
            sub_ax.set_xticks(np.arange(0, predict_cnts[player_id], 1))
            sub_ax.tick_params(axis="both", direction="in")
            #sub_ax.plot(res[player_id])
            sub_ax.bar(np.arange(0, predict_cnts[player_id], 1), res[player_id], width=0.75)
        plt.show()

    def show_rank_chart():
        fig, ax = plt.subplots(2, 2)
        for player_id in range(4):
            sub_ax = ax[player_id//2][player_id%2]
            rank_cnt = [0, 0, 0, 0]
            for game_id in range(game_count):
                rank_cnt[data[game_id]['rank'][player_id]-1] += 1
            percents = [i/game_count for i in rank_cnt]
            sub_ax.set(title=player_names[player_id])
            sub_ax.pie(percents, labels=[f'rank{i+1}' for i in range(4)], autopct='%1.1f%%')    
        plt.show()

    def show_score_chart():
        scores = [[], [], [], []]
        for game_id in range(game_count):
            for player_id in range(4):
                scores[player_id].append(data[game_id]['score'][player_id])
        fig, ax = plt.subplots()
        ax.boxplot(scores, whis=[0, 100], patch_artist=True,
            medianprops={"color": "orange", "linewidth": 1.5},
            boxprops={"color": "C0", "facecolor":"C0", "linewidth": 1.5},
            whiskerprops={"color": "C0", "linewidth": 1.5},
            capprops={"color": "C0", "linewidth": 1.5})
        ax.set_xticklabels(player_names)
        ax.set_title('score')
        ax.set_xlabel('player')
        ax.set_ylabel('score')
        plt.show()
    
    def show_ron_chart():
        total_round = 0
        total_liuju = 0
        player_stats = [{'ron':0, 'houjuu':0, 'tsumo':0} for _ in range(4)]
        for game_id in range(game_count):
            total_round += data[game_id]['round_cnt']
            total_liuju += data[game_id]['liuju_cnt']
            for player_id in range(4):
                player_stats[player_id]['ron'] += data[game_id]['ron_cnt'][player_id]
                player_stats[player_id]['houjuu'] += data[game_id]['houjuu_cnt'][player_id]
                player_stats[player_id]['tsumo'] += data[game_id]['tsumo_cnt'][player_id]
        
        fig, ax = plt.subplots(2, 2)
        for player_id in range(4):
            sub_ax = ax[player_id//2][player_id%2]
            sub_ax.set(title=player_names[player_id])
            sub_ax.pie(list(player_stats[player_id].values()) + [total_liuju], labels=list(player_stats[player_id].keys()) + ['liuju'], autopct='%1.1f%%')
        plt.show()

    def show_tenpai_chart():
        total_round = 0
        tenpai_cnts = [0, 0, 0, 0]
        for game_id in range(game_count):
            total_round += data[game_id]['round_cnt']
            for player_id in range(4):
                tenpai_cnts[player_id] += data[game_id]['tenpai_cnt'][player_id]
        
        fig, ax = plt.subplots(2, 2)
        for player_id in range(4):
            sub_ax = ax[player_id//2][player_id%2]
            sub_ax.set(title=player_names[player_id])
            non_tenpai_cnt = total_round - tenpai_cnts[player_id]
            sub_ax.pie([tenpai_cnts[player_id], non_tenpai_cnt], labels=['tenpai', 'non-tenpai'], autopct='%1.1f%%')
        plt.show()
        
    show_shantin_chart()
    show_legal_chart()
    show_rank_chart()
    show_score_chart()
    show_ron_chart()
    show_tenpai_chart()


game_count = 1

def load_test():
    res = []
    f = open('result.txt', 'r')
    for line in f.readlines():
        if(line=='\n'):
            print('aa')
        res += eval(line)
    f.close()
    return res

if __name__ =='__main__':
    for i in range(game_count):
        print(f'game {i+1}/{game_count}')
        game = FullGame(4)
        game.game_start()
        result = GameLogCollect(game)
        open('result.txt', 'a').write(str([result]) + '\n')
    AnalyzeResult(load_test()) 
