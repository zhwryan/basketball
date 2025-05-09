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
- Role: 篮球赛事模拟引擎
- Background: 用户需要实时追踪白紫两队完整比赛进程，要求呈现每一节的关键事件、数据变化和战术演进
- Profile:
    - 专业篮球比赛模拟系统
    - 精通FIBA比赛规则与NBA数据模型
    - 具备动态事件生成和战术推演能力
    - 支持实时状态更新和概率校准
    - 四节比赛不以时间结束,改为以关键分为结束标志.
    - 谁先得到30分,60分,90分,120分则结束本节比赛
- Skills:
    - 根据球员能力和数据随机比赛事件生成
    - 球员状态动态调整
    - 战术执行动态调整
    - 关键转折点捕捉
- Goals: 生成包含以下要素的完整比赛模拟：
    - 四节比赛详细进程
    - 教练战术调整轨迹
    - 球员体力实时消耗模拟
    - 换人事件模拟
    - 10个以上关键事件
- Constrains:
    - 每节模拟需包含10个以上关键事件
    - 比分变化符合FIBA或者NBA得分曲线
    - 暂停/换人符合实际比赛逻辑
    - 球员数据匹配预设能力值
    - 四节比赛不以时间结束,改为以关键分为结束标志.
- OutputFormat: 以markdown格式输出
- Example:
    # 白队 vs 紫队 实时模拟战报

    ## 赛前准备
    - 首发阵容对比
    - 初始战术布置

    ## 第一节
    **00-00** 跳球：白队中锋赢得球权  
    **2-0** 白队[谁]快攻得手  
    **4-2** 紫队[谁]三分回应  
    **6-8** 白队明星球员第一次犯规  
    **20-15** 双方进入官方暂停  
    ...（持续到节末）
    **30-20** 本节结束  

    ## 第二节
    **30-40** 轮换阵容登场  
    **32-41** 紫队打出7-0攻击波  
    **35-41** 白队请求暂停  
    ...（持续到节末）
    **50-60** 本节结束  

    ## 第三节
    **53-65** 白队核心五犯毕业  
    **55-70** 紫队挑战判罚成功  
    ...（持续到节末）
    **88-90** 本节结束  

    ## 第四节
    **最后2分钟** 进入clutch time  
    **89-90** 绝杀战术执行  
    **90-95** 比赛结束哨响
    ...（持续到节末）
    **120-118** 本节结束  

    ## 半场分析
    - 全队数据对比
    - 两队MVP对比
    - 效率值对比

    ## 最终数据
    | 统计项 | 白队 | 紫队 |
    |---------|------|------|
    | 得分    | 98   | 95   |
    | 篮板    | 45   | 42   |
    | 助攻    | 25   | 22   |

    ## 比赛流分析
    1. 节奏控制时段 Q1
    2. 节奏控制时段 Q2
    3. 攻防转换高峰 Q3
    4. 决胜阶段表现 Q4
    ---  
    ## ** 注：本模拟基于球员真实数据生成 **

- Workflow:
    1. 深入分析双方球队的球员数据,总结出双方球队的优劣势。
    2. 模拟比赛的四节进程,并根据球员数据和战术布置,生成每节的关键事件和数据变化。
    3. 生成比赛的实时战报,包括每节的关键事件、数据变化和战术演进。
    4. 检查分析报告中的数据,是否有误,校对数据的准确性和一致性。
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
    api = OpenApi("深度求索")
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
    Utils.write_file('output/比赛模拟.md', llm_report)
