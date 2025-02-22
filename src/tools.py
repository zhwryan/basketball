import re
from datetime import datetime


# 解析比赛名称
def parse_match_time(sheet_name):
    match = re.search(r'([\d,\.]+)', sheet_name)
    if not match:
        return None
    match_name = match.group()
    return datetime.strptime(match_name, '%y.%m.%d').strftime('%Y.%m.%d')


# 计算效率值
# 效率值(PER) = 得分 + 前场板 + 0.8*后场板 + 助攻 + 抢断 + 盖帽 - 投篮打铁数 - 罚球打铁数 - 失误
def calc_per(user, times):
    ret = user['得分']
    ret += user['前场板']
    ret += 0.8 * user["后场板"]
    ret += user['助攻']
    ret += user['抢断']
    ret += user['盖帽']
    ret -= (user['投篮出手'] - user['投篮命中'])
    ret -= (user['罚球出手'] - user['罚球命中'])
    ret -= user['失误']
    return round(ret / times, 2)


# 计算真实命中率
def calc_ts(user):
    if user is None: return 0
    denominator = 2 * (user['投篮出手'] + 0.44 * user['罚球出手'])
    percent = user['得分'] / denominator
    return round(percent, 4)


# 计算有效命中率
def calc_efg(user):
    if user is None: return 0
    numerator = user['投篮命中'] + 0.5 * user['3分命中']
    percent = numerator / user['投篮出手']
    return round(percent, 4)


# 计算命中率
def calc_fg(user, title):
    shoot = user[title + '出手']
    if shoot > 0:
        return round(user[title + '命中'] / shoot, 2)


# 计算进攻贡献值
def calc_ows(user):
    return user['得分'] + user['助攻'] + user['前场板'] * 0.5 - user['失误']


# 计算防守贡献值
def calc_dws(user):
    return user['后场板'] + user['抢断'] + user['盖帽'] * 0.8


# 计算总胜利贡献值（WS）
def calc_ws(user, total_ows, total_dws):
    ows = (calc_ows(user)) / total_ows
    dws = calc_dws(user) / total_dws
    return round(ows + dws, 4)
