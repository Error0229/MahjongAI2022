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
        fig, ax = plt.subplots()
        
        ax.set(xlabel='game', ylabel='rank')
        ax.set_yticks(np.arange(1, 5, 1))
        ax.set_ylim(0, 5)
    
        ax.set_xticks(np.arange(0, game_count, 1))
        ax.tick_params(axis="both", direction="in")
    
        ax.plot([data[i]['rank'][0] for i in range(game_count)], 'c', label=player_names[0])
        ax.plot([data[i]['rank'][1] for i in range(game_count)], 'm', label=player_names[1])
        ax.plot([data[i]['rank'][2] for i in range(game_count)], 'y', label=player_names[2])
        ax.plot([data[i]['rank'][3] for i in range(game_count)], 'k', label=player_names[3])
        ax.invert_yaxis()
        ax.legend()
        plt.show()

    def show_score_chart():
        fig, ax = plt.subplots()
        
        ax.set(xlabel='game', ylabel='score')
        ax.set_yticks(np.arange(0, 50001, 5000))
        ax.set_ylim(0, 50000)
    
        ax.set_xticks(np.arange(0, game_count, 1))
        ax.tick_params(axis="both", direction="in")
    
        ax.plot([data[i]['score'][0] for i in range(game_count)], 'c', label=player_names[0])
        ax.plot([data[i]['score'][1] for i in range(game_count)], 'm', label=player_names[1])
        ax.plot([data[i]['score'][2] for i in range(game_count)], 'y', label=player_names[2])
        ax.plot([data[i]['score'][3] for i in range(game_count)], 'k', label=player_names[3])
        ax.legend()
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


game_count = 2

if __name__ =='__main__':
    results = []
    for i in range(game_count):
        print(f'game {i+1}/{game_count}')
        game = FullGame(4)
        game.game_start()
        results.append(GameLogCollect(game))
    open('result.txt', 'w').write(str(results))
    # print(results)
    # results = test_data()
    AnalyzeResult(results) 
