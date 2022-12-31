from Game.LocalGame import FullGame

def GameLogCollect(game):
    # rank  
    # Ron, houjuu, tsumo counts 
    # score
    res = {}
    res['score'] = [game.players[i].log['score'] for i in range(4)] 
    return res

def AnalyzeResult(data):
    for i in range(game_count):
        print(f'Game{i}---------------------')
        print(0, data[f'Game{i}']['score'][0])
        print(1, data[f'Game{i}']['score'][1])
        print(2, data[f'Game{i}']['score'][2])
        print(3, data[f'Game{i}']['score'][3])

game_count = 3

if __name__ =='__main__':
    results = {}
    for i in range(game_count):
        game = FullGame(4)
        game.game_start()
        results[f"Game{i}"] = GameLogCollect(game)
    AnalyzeResult(results) 

