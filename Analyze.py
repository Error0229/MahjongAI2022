from Game.LocalGame import FullGame
def GameLogCollect(game):
    # rank  
    # Ron, houjuu, tsumo counts 
    # score
    pass
def AnalyzeResult(data):
    pass
if __name__ =='__main__':
    results = {}
    for i in range(1000):
        game = FullGame(4)
        game.game_start()
        results[f"Game{i}"] = GameLogCollect(game)
    AnalyzeResult(results) 
