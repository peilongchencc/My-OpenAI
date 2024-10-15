"""
Description: 多个wav作为输入的realtime，同时输出文本片段和wav文件。(单轮对话)
Notes: 
三个音频文件可以被视为一个整体音频文件的不同片段。将它们分开处理，可能是因为文件整体过大，分块处理有助于更高效地传输和处理数据。
"""
import os
import json
import asyncio
import aiohttp
from loguru import logger
from dotenv import load_dotenv
import io
import base64
from pydub import AudioSegment

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
    "type": "response.create","response": {"instructions": ""}
}

# 将音频字节流转换为 Base64 编码的 PCM16 数据
def audio_to_base64(audio_bytes: bytes) -> str:
    # 从字节流加载音频文件
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    
    # 重采样为 24kHz 单声道 PCM16
    pcm_audio = audio.set_frame_rate(24000).set_channels(1).set_sample_width(2).raw_data
    
    # 编码为 Base64 字符串
    pcm_base64 = base64.b64encode(pcm_audio).decode()
    
    return pcm_base64

# 发送用户音频信息的函数
async def send_user_audio(ws, files):
    for filename in files:
        with open(filename, 'rb') as f:
            audio_bytes = f.read()
        base64_audio_data = audio_to_base64(audio_bytes)
        await ws.send_json({
            "type": "input_audio_buffer.append",
            "audio": base64_audio_data
        })
    await ws.send_json({"type": "input_audio_buffer.commit"})
    await ws.send_json(response_standard)

# 连接到 OpenAI 实时 WebSocket 服务的函数
async def connect_to_server():
    files = [
        'audio_stream_1.wav',
        'audio_stream_2.wav',
        'audio_stream_3.wav'
    ]
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(api_url, headers=headers, proxy=proxy_url) as ws:
            print("Connected to server.")

            # 调用发送用户音频的函数
            await send_user_audio(ws, files)

            # 初始化字符串，用于存储拼接后的音频 Base64 字符串
            audio_data = ''  
            
            # 接收并处理消息
            async for message in ws:
                try:
                    response = message.json()
                    logger.info(response)
                    # 流式输出打印文本
                    if response['type'] == 'response.audio_transcript.delta':
                        print(f"stream text: {response['delta']}")
                    
                    # 流式输出结束标识
                    if response['type'] == 'response.audio_transcript.done':
                        print("回复结束")
                        # 模拟给前端发送消息
                        # await send_to_frontend("Audio transcript stream completed.")

                    # 拼接 Base64 编码的音频数据
                    if response['type'] == 'response.audio.delta':
                        audio_data += response['delta']  # 将 Base64 字符串拼接起来
                        # logger.info(f"\n拼接后的 Base64 编码的音频数据:\n{audio_data}\n")

                    # 在合适的时候将拼接后的 Base64 字符串写入音频文件
                    # 标准的 OpenAI 服务的音频文件格式为 16 位，采样率 24kHz，单声道
                    # base64_to_wav(audio_data, output_filename='assistant_response.wav')
                    
                except json.JSONDecodeError:
                    print("Received invalid JSON message.")

# 运行异步任务
if __name__ == "__main__":
    asyncio.run(connect_to_server())
