# -*- coding: utf-8 -*-

from __init__ import *
import pandas as pd
from collections import defaultdict


def ev_2p_hit(stats, player):
    stats[player]['投篮出手'] += 1
    stats[player]['投篮命中'] += 1
    stats[player]['得分'] += 2


def ev_2p_miss(stats, player):
    stats[player]['投篮出手'] += 1


def ev_3p_hit(stats, player):
    stats[player]['投篮出手'] += 1
    stats[player]['投篮命中'] += 1
    stats[player]['三分出手'] += 1
    stats[player]['三分命中'] += 1
    stats[player]['得分'] += 3


def ev_3p_miss(stats, player):
    stats[player]['投篮出手'] += 1
    stats[player]['三分出手'] += 1


def ev_1p_hit(stats, player):
    stats[player]['罚球出手'] += 1
    stats[player]['罚球命中'] += 1
    stats[player]['得分'] += 1


def ev_1p_miss(stats, player):
    stats[player]['罚球出手'] += 1


def ev_assist(stats, player):
    stats[player]['助攻'] += 1


def ev_offensive_rebound(stats, player):
    stats[player]['进攻篮板'] += 1
    stats[player]['篮板'] += 1


def ev_defensive_rebound(stats, player):
    stats[player]['防守篮板'] += 1
    stats[player]['篮板'] += 1


def ev_turnover(stats, player):
    stats[player]['失误'] += 1


def ev_steal(stats, player):
    stats[player]['抢断'] += 1


def ev_cap(stats, player):
    stats[player]['盖帽'] += 1


EVENTS = {
    "两分命中": ev_2p_hit,
    "三分命中": ev_3p_hit,
    "罚球命中": ev_1p_hit,
    "两分不中": ev_2p_miss,
    "三分不中": ev_3p_miss,
    "罚球不中": ev_1p_miss,
    "助攻": ev_assist,
    "进攻篮板": ev_offensive_rebound,
    "防守篮板": ev_defensive_rebound,
    "失误": ev_turnover,
    "抢断": ev_steal,
    "盖帽": ev_cap,
}


def parse_match_events(stats, path):
    if not path.lower().endswith(('.md', '.txt')):
        return

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            catched = False
            player, event = None, None
            for event, ev_cb in EVENTS.items():
                if event in line:
                    player = line.split(event)[0]
                    event = line.split(player)[1]
                    ev_cb(stats, player)
                    catched = True
                    break
            if not catched:
                print(f"无法解析事件: {line}")


def save_stats(stats, match_name):
    """生成球员统计数据Excel文件"""
    data_list = []
    for player, data in stats.items():
        stat = {}
        stat['姓名'] = player
        stat['得分'] = data['得分']
        stat['篮板'] = data['篮板']
        stat['前场板'] = data['进攻篮板']
        stat['后场板'] = data['防守篮板']
        stat['助攻'] = data['助攻']
        stat['盖帽'] = data['盖帽']
        stat['抢断'] = data['抢断']
        stat['失误'] = data['失误']
        stat['投篮'] = f"{data['投篮命中']}-{data['投篮出手']}"
        stat['3分'] = f"{data['三分命中']}-{data['三分出手']}"
        stat['罚球'] = f"{data['罚球命中']}-{data['罚球出手']}"
        stat['球队'] = ""
        stat['胜负'] = ""
        data_list.append(stat)

    df = pd.DataFrame(data_list)
    out_path = f"output/数据统计_{match_name}.xlsx"
    df.to_excel(out_path, sheet_name=match_name, index=False)
    print(f"统计数据已保存: {out_path}")


def parse_matchs_events(match_name):
    src_dir = f"userdata/{match_name}"
    stats = defaultdict(
        lambda: {
            '得分': 0,
            '投篮命中': 0,
            '投篮出手': 0,
            '三分命中': 0,
            '三分出手': 0,
            '罚球命中': 0,
            '罚球出手': 0,
            '篮板': 0,
            '进攻篮板': 0,
            '防守篮板': 0,
            '助攻': 0,
            '抢断': 0,
            '盖帽': 0,
            '失误': 0,
            '球队': "",
            '胜负': "",
        })
    for file in os.listdir(src_dir):
        path = op.join(src_dir, file)
        parse_match_events(stats, path)
    save_stats(stats, match_name)


if __name__ == "__main__":
    match_name = "25.4.25白胜"
    parse_matchs_events(match_name)
