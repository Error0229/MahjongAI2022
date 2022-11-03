import requests as req
import bs4
import json


if __name__ == '__main__':
    player_url = 'https://nodocchi.moe/api/graderank.php?playernum=4&orderby=0&rg=0'
    player_res = req.get(player_url)
    player_json = player_res.json()
    player_lst = player_json
    all_player = []
    for player in player_lst:
        all_player.append(
            {'username': player['username'], 'level': player['grade'], 'pt': player['pt']})
    # json.dump(all_player, open('players.json', 'w'), indent=4)
    all_log = []
    for player in all_player:
        name = player['username']
        url = f'https://nodocchi.moe/api/listuser.php?name={name}'
        print(f'Crawling {name}...')
        res = req.get(url)
        if res.status_code == 200:
            print(f"Crwal player {name} success")
        else:
            print(f"Crawl failed, skip player {name}")
            continue

        datas = res.json()
        lst = datas['list']
        for data in lst:
            if data['playernum'] == '4' and data['sctype'] == 'c':
                refid = data['url']
                id_start = refid.find('log=')+4
                all_log.append({'refid': refid[id_start::]+'\n', 'players': [
                               data['player1'], data['player2'], data['player3'], data['player4']]})
        print(f"Player {name}'s data process done")
    print(f'All log size : {len(all_log)}')
    st = set()
    log_without_repeat = []
    for log in all_log:
        if log['refid'] not in st:
            st.add(log['refid'])
            log_without_repeat.append(log)
    print(f'Log without repeat size : {len(log_without_repeat)}')
    json.dump(log_without_repeat, open('all_log.json', 'w'), indent=4)
