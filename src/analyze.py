import os
from pymongo import MongoClient

OUTPUT_DIR = 'output'
client = MongoClient('mongodb://basketball:basketball@localhost:37017/')
season_db = client['赛季']


# 参数改为球员名字的数组
def analyze_players(player_names):
    for player_name in player_names:
        analyze_player(player_name)


def analyze_player(player_name):
    """分析指定球员的详细数据统计"""
    season_stats = season_db['赛季数据'].find_one({'_id': player_name})
    if not season_stats:
        print(f"未找到球员 {player_name} 的数据")
        return

    avg_stats = season_db['场均数据'].find_one({'_id': player_name}) or {}
    score_stats = season_db['积分榜'].find_one({'_id': player_name}) or {}

    # 准备markdown内容
    markdown_content = f"""# {player_name}球员数据统计

## 基础数据
- 场次: {season_stats['场次']}
- 胜负情况: {score_stats['胜场']}胜{score_stats['败场']}负
- 胜率: {score_stats['胜率']*100:.1f}%

## 场均数据
- 得分: {avg_stats['得分']:.1f}
- 篮板: {avg_stats['篮板']:.1f}
  - 前场: {avg_stats['前场板']:.1f}
  - 后场: {avg_stats['后场板']:.1f}
- 助攻: {avg_stats['助攻']:.1f}
- 盖帽: {avg_stats['盖帽']:.1f}
- 抢断: {avg_stats['抢断']:.1f}
- 失误: {avg_stats['失误']:.1f}
- 效率值: {avg_stats['效率值']:.1f}
"""

    if '投篮命中率' in avg_stats:
        markdown_content += "\n## 投篮数据\n"
        投篮类型 = [('投篮', '投篮命中率', '投篮命中', '投篮出手'),
                ('三分', '3分命中率', '3分命中', '3分出手'),
                ('罚球', '罚球命中率', '罚球命中', '罚球出手')]
        for 名称, 命中率, 命中, 出手 in 投篮类型:
            if season_stats[出手] <= 0:
                continue
            if 命中率 in avg_stats and 命中 in season_stats and 出手 in season_stats:
                markdown_content += f"- {名称}: {avg_stats[命中率]*100:.1f}% ({season_stats[命中]}/{season_stats[出手]})\n"
            else:
                markdown_content += f"- {名称}: 无数据\n"

    # 写入markdown文件
    output_file = f"{OUTPUT_DIR}/{player_name}_数据统计.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"统计结果已保存到 {output_file}")


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    analyze_players(['郑宏伟'])
