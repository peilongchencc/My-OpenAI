"""
Description: 文本作为输入的realtime。(单轮对话)
Notes: 
"""
import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("env_config/.env.local")

# 设置 SOCKS5 代理 URL 和 OpenAI API URL
proxy_url = "socks5://127.0.0.1:7890"
api_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
headers = {
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    "OpenAI-Beta": "realtime=v1",
}

# 发送用户文本信息的函数
async def send_user_text(ws):
    event = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "你是谁？"
                }
            ]
        }
    }
    # 发送事件
    await ws.send_json(event)

    # 发送 response.create 消息
    await ws.send_json({"type": "response.create"})

# 连接到 OpenAI 实时 WebSocket 服务的函数
async def connect_to_server():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(api_url, headers=headers, proxy=proxy_url) as ws:
            print("Connected to server.")

            # 调用发送用户文本的函数
            await send_user_text(ws)

            # 接收并处理消息
            async for message in ws:
                try:
                    # message的类型为: <class 'aiohttp.http_websocket.WSMessage'>
                    response = message.json()
                    # 流式输出打印文本
                    if response['type'] == 'response.audio_transcript.delta':
                        print(f"stream text: {response['delta']}")
                except json.JSONDecodeError:
                    print("Received invalid JSON message.")

# 运行异步任务
if __name__ == "__main__":
    asyncio.run(connect_to_server())
"""
Output Example:
Connected to server.
stream text: 你好
stream text: ！
stream text: 我是
stream text: 一个
stream text: 人工
stream text: 智能
stream text: 助手
stream text: ，
stream text: 可以
stream text: 回答
stream text: 你的
stream text: 问题
stream text: 、
stream text: 提供
stream text: 信息
stream text: 和
stream text: 帮助
stream text: 你
stream text: 解决
stream text: 问题
stream text: 。
stream text: 你
stream text: 有什么
stream text: 想
stream text: 了解
stream text: 的吗
stream text: ？
"""