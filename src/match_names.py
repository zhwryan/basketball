# -*- coding: utf-8 -*-
from __init__ import *
import re
import json
import hashlib
from pymongo import MongoClient
from src.utils.open_api import OpenApi


class MatchNames:

    def __init__(self, api_name="火山方舟"):
        mongo_uri = 'mongodb://basketball:basketball@localhost:37017/',
        self._mongo = MongoClient(mongo_uri)
        self._cache_col = self._mongo["缓存"]["MatchNames"]
        self._api = OpenApi(api_name)

    def checkout(self, src):
        src_hash = self._get_src_hash(src)
        cache = self._read_cache(src_hash)
        if cache:
            team_white, team_purple = cache["team_white"], cache["team_purple"]
        else:
            all_names = self._get_all_names()
            prompt = self._build_prompt(src, all_names)
            llm_result = self._call_llm(prompt)
            team_white, team_purple = self._parse_llm_result(llm_result)
            self._write_cache(src_hash, src, team_white, team_purple)

        log(f"team_white = {team_white}\nteam_purple = {team_purple}")
        return team_white, team_purple

    def _get_src_hash(self, src):
        return hashlib.sha256(src.encode("utf-8")).hexdigest()

    def _read_cache(self, src_hash):
        return self._cache_col.find_one({"_id": src_hash})

    def _write_cache(self, src_hash, src, team_white, team_purple):
        cache = {
            "_id": src_hash,
            "src": src,
            "team_white": team_white,
            "team_purple": team_purple
        }
        updater = {"_id": src_hash}
        self._cache_col.replace_one(updater, cache, upsert=True)

    def _get_all_names(self):
        user_db = self._mongo["球员"]
        players = list(user_db["名单"].find())
        return [p["姓名"] for p in players]

    def _build_prompt(self, src, all_names):
        return f"""
你是篮球分队助手。请根据下面的原始分队文本和球员数据库名单，输出最终的白队和紫队名单。
要求：
- 名单中的球员名字必须严格以数据库全名为准。
- src文本中的球员名可能是简称、昵称或简写,请结合数据库名单智能匹配。
- 输出格式为JSON: {{\n  '白队': [全名1, 全名2, ...],\n  '紫队': [全名1, 全名2, ...]\n}}

【数据库球员名单】:
{all_names}

【原始分队文本】:
{src}
"""

    def _call_llm(self, prompt):
        self._api.system = "你是篮球分队助手，善于将简称映射为数据库全名。"
        return self._api.generate(prompt, temperature=0.0)

    def _parse_llm_result(self, llm_result):
        team_white, team_purple = [], []
        try:
            match = re.search(r'\{[\s\S]*\}', llm_result)
            if match:
                data = json.loads(match.group(0).replace("'", '"'))
                team_white = data.get('白队', [])
                team_purple = data.get('紫队', [])
        except Exception as e:
            log(f"解析错误: {e}")
        return team_white, team_purple


# 示例用法
if __name__ == '__main__':
    src = """
白队：林鸿、宏伟、志超、泓达、晓均、陈超、郑超、吴维
紫队：刘竞、国宇、阿鑫、施𬱖、连淼、志坚、益民、宋延
"""
    MatchNames().checkout(src)
