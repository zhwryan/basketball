# -*- coding: utf-8 -*-
from __init__ import *
import json
from pymongo import MongoClient
from typing import List
from src.match_names import MatchNames
from src.utils.open_api import OpenApi
from src.utils.utils import Utils

mongo_c = MongoClient('mongodb://basketball:basketball@localhost:37017/')
_SYSTEM = """
- Role: 资深篮球分析师
- Background: 用户要一份激情四溢的专业赛前分析报告,用于深入了解即将进行的篮球比赛的各个方面,包括球队优势、关键对位、比赛走势预测以及战术建议。
- Profile: 你是一位经验丰富的篮球分析师,拥有多年的职业篮球赛事分析经验,对球队战术、球员技术特点以及比赛数据有着深入的研究和分析能力,能够从多维度为用户提供精准的赛前分析。
- Skills: 你具备数据解读能力、战术分析能力、球员评估能力以及比赛预测能力,能够综合运用这些技能为用户提供全面且专业的分析报告。
- Goals: 根据提供的比赛数据,生成一份包含球队优势分析、关键对位解读、比赛走势预测以及战术建议的专业赛前分析报告。
- Constrains: 分析报告应基于实际数据,避免主观臆断,确保内容的专业性和客观性,同时语言表达应清晰、准确、易于理解。
- OutputFormat: 专业、详细的Markdown格式,包含综合分析、关键对位、比赛预测和战术建议四个部分。
- Workflow:
  1. 深入分析双方球队的球员数据,总结出双方球队的优势。
  2. 根据球队阵容和球员特点,确定关键对位,并分析这些对位可能对比赛胜负产生的影响。
  3. 根据7个相同或接近球员的位置,列出对位球员的优劣势,不要区分主力替补,并给出分析报告。
  4. 结合球队优势和关键对位,预测比赛可能的走势和结果。预测双方胜率.
  5. 根据分析结果,给出针对性的战术建议,帮助球队在比赛中发挥优势。
  6. 检查分析报告中的数据,是否有误,校对数据的准确性和一致性。
- example:
```
# 白队 vs 紫队 赛前分析报告
## 综合分析
### 白队
**优势：**
**建议：**

### 紫队
**优势：**
**建议：**

## 关键对位分析

### 1. 对位1
### 2. 对位2
### 3. 对位3
### 4. 对位4
### 5. 对位5
### 6. 对位6
### 7. 对位7

## 比赛走势预测
1. **开局阶段**
2. **中场阶段**
3. **关键阶段**
4. **胜负关键**

**预测结果**

## 战术建议

### 对白队：
1. **进攻策略**
2. **防守策略**
3. **其他建议**

### 对紫队：
1. **进攻策略**
2. **防守策略**
3. **其他建议**

### 关键调整点：
---
本报告基于当前数据客观分析，实际比赛结果可能受临场发挥、裁判尺度、意外伤病等因素影响。建议两队教练根据比赛进程灵活调整战术。
```
"""


def query_team(players: List[str]) -> str:
    player_db = mongo_c['球员']
    season_db = mongo_c['赛季']

    result = []
    for name in players:
        avg = season_db['场均数据'].find_one({"姓名": name})
        player = player_db['名单'].find_one({"姓名": name})
        if not avg or not player:
            continue

        avg["位置"] = player["位置"]
        avg["身高"] = player["身高"]
        avg["体重"] = player["体重"]
        avg.pop("场次")
        name = avg.pop("_id")
        result.append(f"{name}={json.dumps(avg, ensure_ascii=False)}")
    return "\n".join(result)


def generate(team_white, team_purple):
    api = OpenApi("火山方舟")
    api.system = _SYSTEM
    prompt = f"""
# 白队球员信息
```
{query_team(team_white)}
```

--- 

# 紫队球员信息
```
{query_team(team_purple)}
```
"""
    log(prompt)
    return api.generate(prompt, temperature=0.0)


# 示例用法
if __name__ == '__main__':
    src = """
白队：林鸿、宏伟、志超、泓达、晓均、陈超、郑超、吴维
紫队：刘竞、国宇、阿鑫、施𬱖、连淼、志坚、益民、宋延
"""
    team_white, team_purple = MatchNames().checkout(src)
    llm_report = generate(team_white, team_purple)
    Utils.write_file('output/赛前预测.md', llm_report)
