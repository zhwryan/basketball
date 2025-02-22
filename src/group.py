import random
from pymongo import MongoClient

# 连接到MongoDB
client = MongoClient('mongodb://basketball:basketball@localhost:37017/')
users_db = client["球员"]


def load_applies(file_path):
    applies = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '请假' in line:
                continue
            line = line.split('.', 1)[1]
            line = line.strip()
            applies.append(line)
    return applies


def group_users(team_count, users):
    teams = {f"队伍{i + 1}": {} for i in range(team_count)}
    team_pos = ["控球后卫", "得分后卫", "小前锋", "大前锋", "中锋"]
    random.shuffle(users)

    for _, team in teams.items():
        for pos in team_pos:
            for name in users:
                user = users_db.find_one({'_id': name})
                if not user or user['位置'] != pos:
                    continue
                # 从users中移除已分配的球员
                team[pos] = name
                users.remove(name)

    # 按位置分配球员
    for name in users:
        name = users_db.find_one({'_id': name})
        if name is None:
            continue

        position = name['位置']
        ability = name['数据分']
        chosen_team = None
        for team, filled in team_pos.items():
            if position not in filled:
                chosen_team = team
                break
        if chosen_team is not None:
            teams[chosen_team].append({
                'name': name,
                'position': position,
                'ability': ability
            })
            team_pos[chosen_team].append(position)

    # 输出分配结果
    for team, members in teams.items():
        print(f"队伍 {team}:")
        for member in members:
            print(
                f" 名字: {member['name']}, 位置: {member['position']}, 能力: {member['ability']}"
            )


if __name__ == '__main__':
    applies = load_applies('报名名单.txt')  # 新增：加载报名名单
    group_users(2, applies)  # 修改：传递用户列表
