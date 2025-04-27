# -*- coding: utf-8 -*-
# https://platform.openai.com/docs/api-reference

import base64
import cv2
from __init__ import *
from src.utils.open_api import OpenApi
from src.utils.utils import Utils


class VisionApi:

    def __init__(self, company, model=None):
        self.llm = OpenApi(company, model)

    # 图片理解
    def image(self, path=None, content=None, prompt="用中文描述图片内容", **kwargs):
        ext = "jpeg"
        if path:
            assert op.exists(path), f"图片不存在: {path}"
            with open(path, "rb") as f:
                content = f.read()
            ext = op.splitext(path)[1][1:]  # 使用 [1:] 去掉第一个点号字符

        message = [{
            "role":
            "user",
            "content": [{
                "type": "text",
                "text": prompt
            }, {
                "type": "image_url",
                "image_url": {
                    "url":
                    f"data:image/{ext};base64,{ base64.b64encode(content).decode('utf-8') }"
                }
            }]
        }]

        ret = self.llm.chat(message, **kwargs)
        return ret["content"]

    # 视频理解
    def video(self, path, fps=1, prompt="描述视频的内容", **kwargs):
        try:
            cap = cv2.VideoCapture(path)
            fps_old = int(cap.get(cv2.CAP_PROP_FPS))
            if fps <= 0 or fps > fps_old:
                raise ValueError(f"fps需在1-{fps_old}之间")

            interval = max(1, fps_old // fps)  # 确保至少1帧间隔
            video_array = []
            frame_count = 0  # 新增帧计数器
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % interval == 0:  # 改为if判断
                    _, content = cv2.imencode('.png', frame)
                    image_data = base64.b64encode(content).decode('utf-8')
                    video_array.append(f"data:image/png;base64,{image_data}")
                frame_count += 1  # 每次循环都递增计数器
            cap.release()

            messages = [{
                "role":
                "user",
                "content": [
                    {
                        "type": "video",
                        "video": video_array
                    },
                    {
                        "type": "text",
                        "text": prompt
                    },
                ]
            }]

            ret = self.llm.chat(messages, with_limit=False, **kwargs)
        except Exception as e:
            Utils.print_exc(e)

        return ret["content"]


if __name__ == "__main__":
    v_image = VisionApi("ollama", "gguf/DeepSeek-Janus-Pro-7B")
    v_image.llm.system = "你是一个游戏玩家"
    log(f"图片内容:{v_image.image(
        path="assets/gui/ui.png",
        prompt="""
- 背景:我要把图片内容转成结构化参数
- 期望:给出所有按钮的描述,大小,文字,坐标
- 受众:给程序员看
- 响应:输出markdown格式
""",
    )}")

    v_video = VisionApi("qwen", "qwen-vl-max")
    v_video.llm.system = "你是一个游戏玩家"
    log(f"视频内容:{v_video.video(
        path="assets/videos/test.mp4",
        fps=2,
        prompt=f"""
- 背景:我要视频内容分析报告
- 视角:需要简单易懂,内容简洁
- 期望:期望详细介绍视频内容,将UI相关的信息用markdown画出来
- 受众:要给老板看
- 响应:输出markdown格式
""",
    )}")
