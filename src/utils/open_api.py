# -*- coding: utf-8 -*-
# https://platform.openai.com/docs/api-reference
from __init__ import *

# | messages | 是 | 包含迄今为止对话的消息列表，每个元素类似{"role": "user", "content": "你好"}，role只支持system, user, assistant其一，content不得为空 | List[Dict] | - | - |
# | model | 是 | Model ID，可以通过List Models获取 | string | moonshot - v1 - 8k, moonshot - v1 - 32k, moonshot - v1 - 128k其一 | - |
# | max_tokens | 否 | 聊天完成时生成的最大token数。若生成到最大token数仍未结束，finish reason会是 "length"，否则会是 "stop"。需注意是指期待返回的token长度，非输入 + 输出总长度，输入消息总长度和此值总和不能超过模型限制，可通过“计算Token”API获取输入精确token数 | int | - | 若未指定，会给一个如1024的整数 |
# | temperature | 否 | 使用的采样温度，介于0和1之间。较高值（如0.7）使输出更随机，较低值（如0.2）使输出更集中和确定 | float | [0, 1] | 0 |
# | top_p | 否 | 另一种采样方法，模型考虑概率质量为top_p的标记的结果。0.1意味着只考虑概率质量最高的10%的标记，一般建议改变此项或temperature，但不同时改变 | float | - | 1.0 |
# | n | 否 | 为每条输入消息生成多少个结果 | int | 不得大于5，temperature接近0时只能返回1个结果 | 1 |
# | presence_penalty | 否 | 存在惩罚，介于 - 2.0到2.0之间的数字。正值会根据新生成词汇是否出现在文本中惩罚，增加模型讨论新话题可能性 | float | [-2.0, 2.0] | 0 |
# | frequency_penalty | 否 | 频率惩罚，介于 - 2.0到2.0之间的数字。正值会根据新生成词汇在文本中现有频率惩罚，减少模型重复同样话语可能性 | float | [-2.0, 2.0] | 0 |
# | response_format | 否 | 设置为{"type": "json_object"}可启用JSON模式，保证模型生成信息为有效JSON。设置时需在prompt中明确引导模型输出JSON格式内容并告知具体格式，否则可能导致不符合预期结果 | object | - | {"type": "text"} |
# | stop | 否 | 停止词，全匹配这个（组）词后停止输出，该词本身不输出。最多不能超过5个字符串，每个字符串不得超过32字节 | String, List[String] | - | null |
# | stream | 否 | 是否流式返回 | bool | - | false |

import time
import json
from openai import OpenAI
from llm_config import *
from src.utils.utils import log


class OpenApi:

    def __init__(self, company, model=None):
        cfg = LLM_CONFIGS[company]
        limit = cfg.get("limit")
        base_url = cfg["base_url"]
        api_key = cfg["api_key"]
        models = cfg["models"]

        self._limit = limit or 81920
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model or models[0]
        self.system = None

    # 文本生成
    def generate(self, content, **kwargs):
        assert content is not None, "请求不能为空"
        message = self.chat([{"role": "user", "content": content}], **kwargs)

        ret = message["content"]
        reason = message.get("reasoning_content")
        if reason:
            return f"<think>\n{reason}</think>{ret}"
        return ret

    # 对话接口
    def chat(self, messages, with_limit=False, **kwargs):
        # https://platform.openai.com/docs/api-reference/chat/create
        if self.system and messages[0]["role"] != "system":
            messages.insert(0, {"role": "system", "content": self.system})

        request = json.dumps(messages)
        if with_limit:
            sz = len(request)
            assert sz < self._limit, f"内容过长>{sz}/{self._limit}"
        ti = time.time()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs,
        )
        log(f"  请求> chat {self.model} 时: {time.time() - ti}")
        return response.choices[0].message.to_dict()

    # 补全接口
    def completions(self, prompt, **kwargs):
        # https://platform.openai.com/docs/api-reference/completions
        assert prompt is not None, "请求不能为空"
        assert len(prompt) < self._limit, f"内容过长>{len(prompt)}/{self._limit}"
        ti = time.time()

        response = self.client.completions.create(
            model=self.model,
            prompt=prompt,
            **kwargs,
        )
        log(f"  请求> completions {self.model} 时: {time.time() - ti}")
        return response.choices[0].text

    # 分词接口
    def embeddings(self, input, **kwargs):
        # https://platform.openai.com/docs/api-reference/embeddings/create
        assert input is not None, "请求不能为空"
        assert len(input) < self._limit, f"内容过长>{len(input)}/{self._limit}"
        ti = time.time()

        response = self.client.embeddings.create(
            model=self.model,
            input=input,
            **kwargs,
        )
        log(f"  请求> embeddings {self.model} 时: {time.time() - ti}")
        return response

    def list(self):
        models = self.client.models.list().to_dict()
        ret = []
        for m in models["data"]:
            ret.append(m["id"])
        return ret


# 使用示例
if __name__ == "__main__":
    api = OpenApi("groq")
    log({"models": api.list()})

    log(api.embeddings("我觉得3.11比3.9大,你觉得呢?"))

    api = OpenApi("ollama")
    api.system = "你擅长数学"
    log(api.generate("我觉得3.11比3.9大,你觉得呢?"))
    log(api.chat("我觉得3.11比3.9大,你觉得呢?"))

    api = OpenApi("ollama")
    log(api.completions("你好"))
