"""
Description: 单个wav作为输入的realtime，同时输出文本片段和wav文件。(单轮对话)
Notes: 
"""
import os
import json
import asyncio
import aiohttp
from loguru import logger
from dotenv import load_dotenv
from deltabase64_to_wav import base64_to_wav
from wav_to_base64 import audio_to_item_create_event

# 加载环境变量
load_dotenv("env_config/.env.local")

# 设置日志
logger.remove()
logger.add("send_user_audio.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

# 设置 SOCKS5 代理 URL 和 OpenAI API URL
proxy_url = "socks5://127.0.0.1:7890"
api_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
headers = {
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    "OpenAI-Beta": "realtime=v1",
}

# 信息返回时的标准，instructions 可用于定义自定义知识或角色。
response_standard = {
    "type": "response.create","response": {"instructions": "陈文龙的哥哥叫陈培龙"}
}

# 发送用户音频信息的函数
async def send_user_audio(ws):
    with open("output_test.wav", "rb") as f:
        audio_bytes = f.read()

    # 将wav文件以base64编码
    event = audio_to_item_create_event(audio_bytes)

    # 发送事件
    await ws.send_json(event)

    # 发送 response.create 消息
    await ws.send_json(response_standard)

# 连接到 OpenAI 实时 WebSocket 服务的函数
async def connect_to_server():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(api_url, headers=headers, proxy=proxy_url) as ws:
            print("Connected to server.")

            # 调用发送用户文本的函数
            await send_user_audio(ws)

            # 初始化字符串，用于存储拼接后的音频 Base64 字符串
            audio_data = ''  
            
            # 接收并处理消息
            async for message in ws:
                try:
                    # message的类型为: <class 'aiohttp.http_websocket.WSMessage'>
                    response = message.json()
                    # logger.info(message.json())
                    # 流式输出打印文本
                    if response['type'] == 'response.audio_transcript.delta':
                        print(f"stream text: {response['delta']}")
                    
                    # 拼接 Base64 编码的音频数据
                    if response['type'] == 'response.audio.delta':
                        audio_data += response['delta']  # 将Base64字符串拼接起来
                        logger.info(f"\n拼接后的 Base64 编码的音频数据:\n{audio_data}\n")

                    # 在合适的时候将拼接后的Base64字符串写入音频文件
                    # 标准的openai服务的音频文件格式为 16位，采样率24kHz，单声道
                    base64_to_wav(audio_data, output_filename='assistant_response.wav')
                    
                except json.JSONDecodeError:
                    print("Received invalid JSON message.")

# 运行异步任务
if __name__ == "__main__":
    asyncio.run(connect_to_server())
