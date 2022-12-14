# MahjongAI2022
Artificial Irrational Japanese Mahjong bot using basic CNN  
## Summary
This is a project for the NTUT 2022 AI course. 
In this project, we built a local Mahjong game and designed 2 types of AI players.The first type of AI is using a greedy algorithm to make it win as soon as possible. The second type of AI is using few CNN models to predict for all possible Mahjong actions, like discard, pong, kong, etc. The CNNs is trained by a dataset of top 200 players from tenhou.net.  

### Features
- Local Mahjong game
- Greedy Mahjong AI
- CNN Mahjong AI
- Log ID and game log Crawler
- Training data generator
- 4 types of CNN models

## Build
### Requirements
python 3.9.0
### Install
```bash
pip install -r requirements.txt
``` 

Install models from [Google drive](https://drive.google.com/drive/folders/1-S6VTXC1IxihaiXAqBHY9yerPFF0HCNC?usp=sharing)
and put them in the main folder.
### Run
```bash
python main.py
```
The default console output is a full game with 3 CNN AI players and 1 Gready AI player.

For every decision of the AI player, it will print some info about that prediction:
```bash
1/1 [==============================] - 0s 74ms/step
π :0.52726 π :0.28870 π :0.05076 π :0.03475 π :0.03465
hand: π π π π π π π π π  π π π π π
chose:π which is 0th in prediction.
```
And for every round end, it will print a summary of the round:
```bash
win
Tile: π π π π π π π π π π π π π , Melds:  , minkans:
player:3, from:0, score:20Fu/1Han --> 20η¬¦1Han700ηΉ 700ηΉ, tile:π
han: {'η«η΄(1Han)': 1}, fu: {'δΈ­εΌ ζε»(2Fu)': 2, 'ι¨εζΈθ£θ‘(10Fu)': 10}
player 0, Wind: π , score: 23700 , riichi: False , Tile: π π π π π π π π π  π  π π π , Melds:
, minkans:
player 1, Wind: π , score: 27000 , riichi: False , Tile: π π π π π π π π π π       , Melds: π π π
, minkans:
player 2, Wind: π , score: 23000 , riichi: False , Tile: π π π π π π π π π π       , Melds: π π π
, minkans:
player 3, Wind: π , score: 26300 , riichi: True , Tile: π π π π π π π π π π π π π , Melds:               ,

```

## Results
This part will describe in the report precisely.
# Downloads
Models: [Google drive](https://drive.google.com/drive/folders/1-S6VTXC1IxihaiXAqBHY9yerPFF0HCNC?usp=sharing)  
Training Data, gamelog.db [Google drive](https://drive.google.com/drive/folders/1S3AyABPsXYCukd1bYhUdIlt8OXBicPMb?usp=sharing)
