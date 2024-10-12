"""
Description: openai-realtime-api 的python实现。
Notes: 
当前(2024-10-12)openai-realtime-api只有javascript实现，笔者实现了一下python形式。
注意: 由于网络限制，笔者必须开启 SOCKET5 代理才能访问，故没有使用python原生的websockets库。
python原生的websockets库本身并不直接支持 SOCKS5 代理。
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
initial_message = {
    "type": "response.create",
    "response": {
        "modalities": ["text"],
        "instructions": "Please assist the user."
    }
}

async def connect_to_server():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(api_url, headers=headers, proxy=proxy_url) as ws:
            print("Connected to server.")
            await ws.send_json(initial_message)

            # 接收并处理消息
            async for message in ws:
                try:
                    print(message.json())
                except json.JSONDecodeError:
                    print("Received invalid JSON message.")

# 运行异步任务
asyncio.run(connect_to_server())
