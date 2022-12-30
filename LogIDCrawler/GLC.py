# -*- coding: utf-8 -*-
import json

import os

import requests
import bs4
import sqlite3

__author__ = "Jianyang Tang"
__email__ = "jian4yang2.tang1@gmail.com"


class GameLogCrawler:

    seed = "Seria"

    level_dict = {'新人': 0, '１級': 1, '２級': 2, '３級': 3, '４級': 4, '５級': 5, '６級': 6, '７級': 7, '８級': 8, '９級': 9,
                  '初段': 10, '二段': 11, '三段': 12, '四段': 13, '五段': 14, '六段': 15, '七段': 16, '八段': 17, '九段': 18,
                  '十段': 19, '天鳳位': 20, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20}

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dbfile = dir_path + "/gamelog.db"
        self.conn = sqlite3.connect(dbfile)
        self.cs = self.conn.cursor()
        self._db_create_tables_if_not_exists()
        # self.cs.execute(f"CREATE TABLE IF NOT EXISTS ")

    def _db_show_table_structures(self, table_name):
        res = self.cs.execute(f"PRAGMA table_info('{table_name}');").fetchall()
        cnt = self.cs.execute(f"SELECT count(*) from '{table_name}'")
        print("TABLE '{}': {} rows".format(table_name, list(cnt)[0][0]))
        print("      " + "-" * 43 + " ")
        print("    | {:10s} {:10s} {:10s} {:10s}|".format(
            "Column", "Name", "Type", "Primary"))
        print("    | " + "-" * 43 + "|")
        for r in res:
            print("    | {:10s} {:10s} {:10s} {:10s}|".format(
                str(r[0]), str(r[1]), str(r[2]), str(r[5])))
        print("      " + "-" * 43 + " ")
        print()

    def _db_create_tables_if_not_exists(self):
        self.cs.execute(
            "CREATE TABLE IF NOT EXISTS player ('name' text PRIMARY KEY, 'level' text, 'pt' text, 'lv' INTEGER)")
        self.cs.execute(
            "CREATE TABLE IF NOT EXISTS refids ('ref' text PRIMARY KEY, 'p1' text, 'p2' text, 'p3' text, 'p4' text)")
        self.cs.execute(
            "CREATE TABLE IF NOT EXISTS logs ('refid' text PRIMARY KEY, 'log' text)")
        self.conn.commit()

    def db_prt_players(self, rows=100):
        row_cnt_cs_obj = self.cs.execute("SELECT count(*) FROM player")
        print("There are {} rows in table player!".format(
            row_cnt_cs_obj.fetchone()[0]))
        for row in self.cs.execute("SELECT * FROM player ORDER BY lv DESC"):
            print("  {}".format(row))
            rows -= 1
            if rows <= 0:
                break

    def db_prt_refs(self, rows=100):
        row_cnt_cs_obj = self.cs.execute("SELECT count(*) FROM refids")
        print("There are {} rows in table refids!".format(
            row_cnt_cs_obj.fetchone()[0]))
        for row in self.cs.execute("SELECT * FROM refids"):
            print("  {}".format(row))
            rows -= 1
            if rows <= 0:
                break

    def db_prt_logs(self, rows=100):
        row_cnt_cs_obj = self.cs.execute("SELECT count(*) FROM logs")
        print("There are {} rows in table refids!".format(
            row_cnt_cs_obj.fetchone()[0]))
        for row in self.cs.execute("SELECT * FROM logs"):
            print("  {}".format(row))
            rows -= 1
            if rows <= 0:
                break

    def db_show_tables(self):
        """
        Show the structure of tables in the database
        :return:
        """
        self._db_show_table_structures("player")
        self._db_show_table_structures("refids")
        self._db_show_table_structures("logs")

    def _db_exists_game_log(self, refid):
        has_log = self.cs.execute(
            f"SELECT count(*) FROM logs WHERE refid = '{refid}'")
        has_log = has_log.fetchone()
        return has_log[0]

    def _db_exists_name(self, name):
        has_name = self.cs.execute(
            f'SELECT count(*) FROM player WHERE name = "{name}"')
        has_name = has_name.fetchone()
        if not has_name or len(has_name) == 0:
            return False
        return has_name[0] != None and has_name[0] > 0

    def _db_exists_refid(self, refid):
        has_refid = self.cs.execute(
            f'SELECT count(*) FROM refids WHERE ref = "{refid}"')
        has_refid = has_refid.fetchone()
        if not has_refid or len(has_refid) == 0:
            return False
        return has_refid[0] != None and has_refid[0] > 0

    def _db_insert_names(self, players):
        for name in players:
            try:
                if not self._db_exists_name(name):
                    self.cs.execute(
                        f'INSERT INTO player VALUES ("{name}", NULL, NULL, NULL, NULL)')
                    print("    Player {} inserted into table player".format(name))
            except Exception as e:
                print('insert name exception')
                print(e)
        self.conn.commit()

    def _db_insert_refid(self, refid, players):
        try:
            if not self._db_exists_refid(refid) and len(players) > 3:
                self.cs.execute(
                    f"INSERT INTO refids VALUES ('{refid}', '{players[0]}', '{players[1]}', '{players[2]}', '{players[3]}')")
                print(
                    "   Refid {} - {} inserted into table refids".format(refid, players))
            self.conn.commit()
        except Exception as e:
            print(e)

    def _db_insert_log(self, refid, log):
        try:
            if not self._db_exists_game_log(refid):
                log = str(log).replace("'", "\"")
                self.cs.execute(
                    f"INSERT INTO logs VALUES ('{refid}', '{log}')")
                print(
                    "Game log of {} crawled and inserted into TABLE logs.".format(refid))
                self.conn.commit()
        except Exception as e:
            print(e)

    def _db_update_player_level(self, name, level, pt):
        try:
            lv = self.level_dict[level]
            self.cs.execute(
                f"UPDATE player SET level = '{level}', pt = '{pt}', lv = '{lv}' WHERE name = '{name}'")
            self.conn.commit()
            print(
                "    Player {}'s level-{} and pt-{} is updated.".format(name, level, pt))
        except Exception as e:
            print('update player level exception')
            print(e)

    def _db_update_retrieved(self, name):
        try:
            self.cs.execute(
                f"UPDATE player SET retrieved = TRUE WHERE name = '{name}'")
            self.conn.commit()
            print("    Player {}'s playing history was totally retrieved".format(name))
        except Exception as e:
            print(e)

    def _db_update_unretrieved(self, name):
        try:
            self.cs.execute(
                f"UPDATE player SET retrieved = NULL WHERE name = '{name}'")
            self.conn.commit()
        except Exception as e:
            print(e)

    def _db_select_players_lv_gr(self, level):
        if True:
            names = self.cs.execute(
                f"SELECT name FROM player WHERE (retrieved IS NULL AND lv > {level}) ORDER BY lv DESC")
            names = names.fetchall()
            for n in names:
                yield n[0]

    def _db_select_players_no_lv(self):
        need_level_names_cs_obj = self.cs.execute(
            "SELECT name FROM player WHERE level IS NULL")
        names = need_level_names_cs_obj.fetchall()
        for n in names:
            yield n[0]

    def _db_select_refids_no_logs_where_players_lv_gr(self, gr_lv):
        res = self.cs.execute(f"SELECT DISTINCT refids.ref "
                              f"FROM player JOIN refids "
                              f"ON (player.name = refids.p1 OR player.name = refids.p2 "
                              f"OR player.name = refids.p3 OR player.name = refids.p4) "
                              f"WHERE player.lv > {gr_lv} "
                              f"ORDER BY refids.ref DESC")
        for r in res.fetchall():
            if not self._db_exists_game_log(r[0]):
                yield r[0]

    def _db_select_refids_with_logs_where_players_lv_gr(self, gr_lv):
        res = self.cs.execute(f"SELECT DISTINCT refids.ref "
                              f"FROM player JOIN refids "
                              f"ON (player.name = refids.p1 OR player.name = refids.p2 "
                              f"OR player.name = refids.p3 OR player.name = refids.p4) "
                              f"WHERE player.lv > {gr_lv} "
                              f"ORDER BY refids.ref DESC")
        for r in res.fetchall():
            if self._db_exists_game_log(r[0]):
                yield r[0]

    @staticmethod
    def _crawl_get_self_page(name):
        url = "http://arcturus.su/tenhou/ranking/ranking.pl?name=" + name
        agent = "Mozilla/5.0 (Macintosh; Intel ...) Gecko/20100101 Firefox/58.0"
        headers = {'User-Agent': agent}
        r = requests.get(url, headers=headers)
        return r.text

    def _crawl_level_and_pt_by_name(self, name=None, page=None):
        if page:
            text = page
        else:
            if name:
                text = GameLogCrawler._crawl_get_self_page(name)
            else:
                return
        pos1 = str.find(text, 'rank estimation [translateme]')
        pos2 = str.find(text, '[to be generalised] hourly gameplay')
        stats = text[pos1:pos2]
        start = str.find(stats, "4man [translateme]:")
        end = str.find(stats, "<br>")
        fourman = stats[start + 20:end]
        if len(fourman) > 0 and len(fourman.split(" ")) > 1:

            # print(name + ": " + fourman)
            level, pt = fourman.split(" ")
            print
            return level, pt

    def _crawl_refid_and_players_by_name(self, name):
        r = GameLogCrawler._crawl_get_self_page(name)
        print(r)
        level, pt = self._crawl_level_and_pt_by_name(page=str(r))
        if level and pt:
            self._db_update_player_level(name, level, pt)

        soup = bs4.BeautifulSoup(r, 'html.parser')
        rec = soup.find(id="records")
        for l in str(rec).splitlines():
            if "<a href=" in l:
                refid = l[l.find("<a href=") + 34:l.find('">log</a>')]
                names = [n.split('(')[0] for n in l[l.find(
                    "</abbr>") + 10:l.find("<br/>")].split(" ")]
                yield {"ref": refid, "players": names}

    def _crawl_log_by_refid(self, refid):
        if (refid[-1:] == '\n'):
            refid = refid[:-1]
        url = "http://tenhou.net/5/mjlog2json.cgi?" + refid
        referer = "http://tenhou.net/5/?log=" + refid
        agent = "Mozilla/5.0 (Macintosh; Intel ...) Gecko/20100101 Firefox/58.0"
        host = "tenhou.net"
        headers = {'User-Agent': agent, 'Host': host, 'Referer': referer}
        response = requests.get(url, headers=headers).content
        log = json.loads(response)
        return log
        # s = str(fixtures).replace("'", "\"")
        # self.cs.execute(f"INSERT INTO logs VALUES ('{refid}', '{s}')")

    def batch_crawl_refids(self, gr_level, ite=5):
        """
        Crawl multiple game log referal ids and insert them into database.
        It will select players from database that havn't been processed yet,
        and then crawl referal ids of games that the specific player was involed in,
        and finally insert them into database
        :param gr_level: Indicates that crawling will be only processed on players who has a level greater than gr_level
        :param ite: number of iterations
        :return: None
        """
        names_generator = self._db_select_players_lv_gr(gr_level)
        # print(names_generator)
        for i in range(ite):
            try:
                current_name = names_generator.__next__()
                refid_generator = self._crawl_refid_and_players_by_name(
                    current_name)
                for refid_item in refid_generator:
                    refid, names = refid_item["ref"], refid_item["players"]
                    self._db_insert_refid(refid, names)
                self._db_update_retrieved(current_name)
            except StopIteration:
                print("    There are not so many ({}) players that have levels greater than {}".format(
                    ite, gr_level))
                print(
                    "    Please crawl by smaller gr_level next time or firstly call_batch_crawl_levels()")
                break

    def batch_crawl_levels(self, ite=5):
        """
        Crawl level of players and store them into database.
        It will select players in database that have no level information and update their levels
        :param ite: number of iterations.
        :return: None
        """
        names_no_levels_generator = self._db_select_players_no_lv()
        for i in range(ite):
            try:
                current_name = names_no_levels_generator.__next__()
                level, pt = self._crawl_level_and_pt_by_name(current_name)
                if level and pt:
                    self._db_update_player_level(current_name, level, pt)
            except StopIteration:
                print("All names in TABLE player has now levels!")
                break

    def batch_crawl_logs(self, gr_lv, ite=10):
        """
        Crawl game logs and insert them into database.
        It will firstly select a couple of players whose level is higher than gr_lv,
        then select all referal ids of these players,
        finally game logs of these referal ids will be crawled and stored into database.
        :param gr_lv: a level number, 20 highest, 0 lowest
        :param ite: number of iteration
        :return: None
        """
        gene = self._db_select_refids_no_logs_where_players_lv_gr(gr_lv)
        for i in range(ite):
            try:
                refid = gene.__next__()
                log = self._crawl_log_by_refid(refid)
                self._db_insert_log(refid, log)
            except StopIteration:
                print("All refids have been processed!")
                break

    def db_get_logs_where_players_lv_gr(self, gr_lv):
        """
        Select game logs of players whose level is higher than gr_lv.
        :param gr_lv: level, highest 20, lowest 0
        :return: a generator of game logs that satisfy the constraint
        """
        gene = self._db_select_refids_with_logs_where_players_lv_gr(gr_lv)
        i = 0
        while True:
            try:
                refid = gene.__next__()
                res = self.cs.execute(
                    f"SELECT log FROM logs WHERE refid='{refid}'")
                res = res.fetchone()
                log = res[0]
                log = json.loads(log)
                i += 1
                yield log
            except StopIteration:
                print("All {} logs with players greater than level {} are processed.".format(
                    i, gr_lv))
                break

    @staticmethod
    def prt_log_format(log):
        """
        Print a game log in user friendly format
        :param log: the log dict
        :return: None
        """
        for k, v in log.items():
            if k == 'log':
                print("log:")
                for vv in v:
                    print("    Round {}".format(v.index(vv)))
                    for vvv in vv:
                        print("        {}".format(vvv))
            else:
                print("{}: {}".format(k, v))
