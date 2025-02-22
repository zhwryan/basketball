# -*- coding: utf-8 -*-

import os
import base64
import json
from math import floor
import cv2
from openai import OpenAI
from time import time

prompt = """
## 角色:
- 你是一位资深篮球视频分析师
## 能力:
- 能够高效识别持球运动员的动作
- 识别持球运动员的球衣信息
## 目标:
- 识别持球运动员的动作
- 识别持球运动员的球衣颜色,号码
## 输出格式:
- 输出JSON格式
```
## 工作流程:
1. 识别出是否有球员正在投篮
2. 识别投篮球员的球衣颜色,号码
3. 检查返回格式是否符合json,且字段齐全
"""


def llm_analysis(events, prompt="这是一个视频连续的帧的json,请你分析一下,是否进球"):
    BASE_URL = "http://localhost:11434/v1/"
    MODEL = "deepseek-r1:32b"
    API_KEY = "ollama"

    estr = json.dumps(events, ensure_ascii=False, indent=2)
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"{estr}\n{prompt}",
        }],
        temperature=0.2,
    )
    return response.choices[0].message.content


def vlm_frame(frame):
    BASE_URL = "http://localhost:11434/v1/"
    MODEL = "llava:7b"
    API_KEY = "ollama"

    _, buffer = cv2.imencode('.jpg', frame)
    image_data = base64.b64encode(buffer).decode('utf-8')

    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    prompt = """
## 角色:
- 你是一位资深篮球视频分析师
## 能力:
- 能够高效识别持球运动员的动作
## 目标:
- 识别持球运动员的动作
## 输出格式:
- 用中文回答
- 输出JSON格式{"正在投篮":"是否"}
## 工作流程:
1. 识别是否有球员正在投篮
2. 检查返回格式是否符合json,且字段齐全
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role":
            "user",
            "content": [{
                "type": "text",
                "text": prompt
            }, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                }
            }]
        }],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    result = response.choices[0].message.content

    # 解析JSON结果
    try:
        result_json = json.loads(result or "")
        hit = result_json.get('hit')
        if hit == True or hit == "是" or hit == "命中":
            os.makedirs('output/hit_frames', exist_ok=True)
            filename = f'output/hit_frames/hit_{int(time())}.jpg'
            cv2.imwrite(filename, frame)
            print(f'保存了命中帧: {filename} saved.')
    except json.JSONDecodeError:
        pass

    return result


def process_video(path, interval=0.5):
    rets = []
    cap = cv2.VideoCapture(path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    count = 0
    interval = floor(fps * interval)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if count % interval == 0:
            ret = vlm_frame(frame)
            rets.append(ret)
            print(f"{count/fps}: {ret}")

        count += 1

    cap.release()
    return rets


if __name__ == "__main__":
    path = 'assets/宏伟-004.mp4'
    # path = "比赛/250124/白队-001.mp4"
    ti = time()
    rets = process_video(path)
    # ret = llm_analysis(rets)
    # print(f"结果: {ret} 时间:{time()-ti:.1f}")
