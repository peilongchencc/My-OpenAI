"""
Description: 交互模式的openai realtime服务。
Notes: 
"""
import os
import json
import aiohttp
from loguru import logger
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
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


# 设定session默认配置
session_default = {
    "event_id": "event_123",
    "type": "session.update",
    "session": {
        "instructions": "Your knowledge cutoff is 2023-10. You are a helpful assistant.",
        # OpenAI暂时还没有把input_audio_transcription调试好，该功能暂时无效。
        "input_audio_transcription": {
            # "enabled": True,  # 使用这个参数会提示 "没有这个参数"
            "model": "whisper-1"
        }
    }
}

# 信息返回时的标准，instructions 可用于定义自定义知识或角色。
response_standard = {
    "type": "response.create",
    "response": {"instructions": ""}
}

app = FastAPI()

# 根目录访问的处理
@app.get("/")
async def read_root():
    return JSONResponse(
        content={"code": 0, "msg": "My-OpenAI", "data": ""},
        status_code=200
    )

async def send_user_audio(ws, audio_bytes):
    
    # 设定事件默认配置
    await ws.send_json(session_default)
    
    # 将 WAV 文件以 base64 编码
    event = audio_to_item_create_event(audio_bytes)
    # 发送主事件
    await ws.send_json(event)
    # 发送 response.create 消息
    await ws.send_json(response_standard)

async def connect_to_server(audio_bytes):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(api_url, headers=headers, proxy=proxy_url) as ws:
            logger.info("已连接到服务器。")
            # 发送用户音频
            await send_user_audio(ws, audio_bytes)
            # 接收并处理消息
            async for message in ws:
                try:
                    response = message.json()
                    # logger.info(response)
                    # 如果是流式文本，按照 SSE 格式返回
                    if response['type'] == 'response.audio_transcript.delta':
                        sse_message = f"data: {response['delta']}\n\n"
                        yield sse_message
                    # 如果流式文本结束，发送结束事件
                    elif response['type'] == 'response.audio_transcript.done':
                        logger.info("流式文本接收完毕。")
                        # SSE 使用一个特殊的事件（如 event: end）来标识结束，而不是发送 data: None。
                        yield "event: end\n\n"
                        break
                except json.JSONDecodeError:
                    logger.error("收到无效的 JSON 消息。")
                except Exception as e:
                    logger.error(f"处理消息时出错：{str(e)}")
                    break

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    try:
        # 读取上传的文件内容为字节流
        audio_bytes = await file.read()
        # 调用异步生成器函数
        generator = connect_to_server(audio_bytes)
        # 使用 StreamingResponse 返回流式响应
        return StreamingResponse(generator, media_type="text/event-stream")
    except Exception as e:
        logger.error(f"处理音频时出错：{str(e)}")
        return JSONResponse(
            content={"code": 1, "msg": "处理失败", "error": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"启动服务器时出错：{e}")
