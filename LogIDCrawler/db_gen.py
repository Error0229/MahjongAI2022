import requests as req
import json
import GLC


def insert_players():
    glc = GLC.GameLogCrawler()
    with open('players.json', 'r') as f:
        players = json.load(f)
    for player in players:
        print(player['username'], player['level'], player['pt'])
        glc._db_insert_names([player['username']])
        glc._db_update_player_level(
            player['username'], player['level'], player['pt'])


def crawl_logs_by_refid(count, level):
    glc = GLC.GameLogCrawler()
    glc.db_show_tables()
    glc.batch_crawl_logs(level, count)


def insert_refids():
    glc = GLC.GameLogCrawler()
    with open('all_log.json', 'r') as f:
        rfds = json.load(f)
    for refid in rfds:
        glc._db_insert_refid(refid['refid'], refid['players'])


def crawl_pid():
    player_url = 'https://nodocchi.moe/api/graderank.php?playernum=4&orderby=0&rg=0'
    player_res = req.get(player_url)
    player_json = player_res.json()
    player_lst = player_json
    all_player = []
    for player in player_lst:
        all_player.append(
            {'username': player['username'], 'level': player['grade'], 'pt': player['pt']})
    json.dump(all_player, open('players.json', 'w'), indent=4)
    all_log = []
    for player in all_player:
        name = player['username']
        url = f'https://nodocchi.moe/api/listuser.php?name={name}'
        print(f'crawling {name}...')
        res = req.get(url)
        if res.status_code == 200:
            print(f"crwal player {name} success")
        else:
            print(f"crawl failed, skip player {name}")
            continue

        datas = res.json()
        lst = datas['list']
        for data in lst:
            if data['playernum'] == '4' and data['sctype'] == 'c':
                refid = data['url']
                id_start = refid.find('log=')+4
                all_log.append({'refid': refid[id_start::], 'players': [
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


def excute_all(c, l):
    crawl_pid()
    insert_players()
    insert_refids()
    crawl_logs_by_refid(c, l)


if __name__ == '__main__':
    crawl_log_count = 10000
    crawl_log_level = 19
    excute_all(crawl_log_count, crawl_log_level)
