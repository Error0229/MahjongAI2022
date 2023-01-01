from Game.LocalGame import FullGame
import matplotlib.pyplot as plt
import numpy as np

def GameLogCollect(game):
    '''
    WIP:
    ron chance, make_other_ron chance
    
    player_log:
        shaintin: shantin after every discard action
        ron: detial of ron consists of: score, han (have bug)

    game_log: (each item is a list of 4 elements)
        rank: ranks after every game ended
        score: scores after every game ended
    '''
    res = {}
    
    res['shantin'] = [game.players[i].player_log['shantin'] for i in range(4)]
    res['ron'] = [game.players[i].player_log['ron'] for i in range(4)]
    res['rank'] = game.game_log['rank']
    res['score'] = game.game_log['score']
    return res

def AnalyzeResult(data):
    # only show the score chart of the first game
    player_names = ['cnn0', 'cnn1', 'cnn2', 'greedy']
    
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
        

    def show_rank_chart():
        fig, ax = plt.subplots()
        
        ax.set(xlabel='game', ylabel='rank')
        ax.set_yticks(np.arange(0, 5, 1))
        ax.set_ylim(0, 5)
    
        ax.set_xticks(np.arange(0, game_count, 1))
        ax.tick_params(axis="both", direction="in")
    
        ax.plot([data[i]['rank'][0] for i in range(game_count)], 'c', label=player_names[0])
        ax.plot([data[i]['rank'][1] for i in range(game_count)], 'm', label=player_names[1])
        ax.plot([data[i]['rank'][2] for i in range(game_count)], 'y', label=player_names[2])
        ax.plot([data[i]['rank'][3] for i in range(game_count)], 'k', label=player_names[3])
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
    
    show_shantin_chart()



game_count = 2

if __name__ =='__main__':
    results = []
    for i in range(game_count):
        game = FullGame(4)
        game.game_start()
        results.append(GameLogCollect(game))
    AnalyzeResult(results) 


