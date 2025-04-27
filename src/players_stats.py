import pandas as pd
from pymongo import MongoClient

client = MongoClient('mongodb://basketball:basketball@localhost:37017/')
user_db = client["球员"]


def calc_ability(record):
    name = record["姓名"]
    stats = client["赛季"]["场均数据"].find_one({"_id": name})
    if stats is None: return 0

    weights = {
        '得分': 0.5,
        '前场板': 0.67,
        '后场板': 0.33,
        '助攻': 1.0,
        '抢断': 1.1,
        '盖帽': 1.1,
        '失误': -1.2,
        '真实命中率': 0.1,
        '有效命中率': 0.1,
    }

    ability = sum(stats[stat] * weights.get(stat, 0) for stat in weights)
    return round(ability + 55, 2)


def generate_players(path):
    file = pd.ExcelFile(path)
    sheet = pd.DataFrame(file.parse("Sheet1"))
    records = sheet.to_dict(orient='records')

    for record in records:
        record["_id"] = record["姓名"]
    user_db["名单"].delete_many({})
    user_db["名单"].insert_many(records)

    for record in records:
        record["数据分"] = calc_ability(record)
    user_db["能力"].delete_many({})
    user_db["能力"].insert_many(records)


def generate_excel(path):
    with pd.ExcelWriter(path) as writer:
        data = user_db["能力"].find()
        df = pd.DataFrame(data)
        df = df.drop(columns=['_id'])
        df.to_excel(writer, index=False)


if __name__ == '__main__':
    generate_players('assets/球员名单.xlsx')
    generate_excel('output/球员能力.xlsx')
