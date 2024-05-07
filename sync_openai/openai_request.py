import requests
import os
from loguru import logger
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = '.env.local'
load_dotenv(dotenv_path=dotenv_path)

# 设置日志
logger.remove()
logger.add("openai_stream.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

# 设置代理环境变量
# os.environ['http_proxy'] = 'http://127.0.0.1:7890'
# os.environ['https_proxy'] = 'http://127.0.0.1:7890'

# Your OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "user",
            "content": "你的知识截止到什么时候？"
        }
    ]
}

response = requests.post(url, json=data, headers=headers)

print(response.text)

# 终端输出:
# {
#   "id": "chatcmpl-8vMSJpOYgAJXxK5dNWdfDJX5adkfW",
#   "object": "chat.completion",
#   "created": 1708681707,
#   "model": "gpt-3.5-turbo-0125",
#   "choices": [
#     {
#       "index": 0,
#       "message": {
#         "role": "assistant",
#         "content": "我是一个人工智能助手，有什么可以帮到你的吗？"
#       },
#       "logprobs": null,
#       "finish_reason": "stop"
#     }
#   ],
#   "usage": {
#     "prompt_tokens": 12,
#     "completion_tokens": 25,
#     "total_tokens": 37
#   },
#   "system_fingerprint": "fp_cbdb91ce3f"
# }