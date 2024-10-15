# Realtime API

[OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime/overview) 使用介绍。
- [Realtime API](#realtime-api)
  - [文件简介:](#文件简介)
  - [response:](#response)
    - [1. Session 创建事件：](#1-session-创建事件)
    - [2. 用户消息创建事件：](#2-用户消息创建事件)
    - [3. Assistant 响应事件：](#3-assistant-响应事件)
    - [4. 音频相关事件：](#4-音频相关事件)
    - [5. 音频数据片段：](#5-音频数据片段)
  - [处理中断:](#处理中断)
  - [继续对话](#继续对话)
  - [关于多轮对话的一些思考:](#关于多轮对话的一些思考)
    - [步骤1：修改 `process_audio` 端点](#步骤1修改-process_audio-端点)
    - [步骤2：修改 `connect_to_server` 函数](#步骤2修改-connect_to_server-函数)
    - [步骤3：修改 `send_user_audio` 函数](#步骤3修改-send_user_audio-函数)
    - [步骤4：在接收到响应后更新对话历史](#步骤4在接收到响应后更新对话历史)
    - [步骤5：处理对话清理（可选）](#步骤5处理对话清理可选)
    - [附加考虑](#附加考虑)
    - [更新的代码片段](#更新的代码片段)
    - [测试多轮对话](#测试多轮对话)

## 文件简介:

| 文件名                               | 作用                                         | 备注         |
|-------------------------------------|---------------------------------------------|--------------|
| realtime_connection.py              | openai-realtime-api 连接示例的python实现      | 网页版为js代码 |
| main_realtime.py                    | 交互模式的openai realtime服务                 |              |
| wav_to_base64.py                    | wav文件转base64，截断需要读者自己做             |               |
| deltabase64_to_wav.py               | 工具函数--base64音频帧转wav                   |               |
| send_user_audio_stream.py           | 多个wav作为输入的realtime                     |               |
| send_user_audio.py                  | 单个wav作为输入的realtime                     |               |
| send_user_text_only_return_text.py  | 交互模式的openai realtime服务                 |               |
| send_user_text_return_text_wav.py   | 文本作为输入的realtime，同时输出文本片段和wav文件 |               |

🚨注意: 以上代码的实现都是单轮对话，多轮对话形式笔者还未实现。


## response:

返回的数据包含了一些复杂的事件和内容，关键事件包括：

### 1. Session 创建事件：

`type: session.created` 表示 WebSocket 会话的创建，成功建立了与 OpenAI 实时 WebSocket 服务的连接。
   
### 2. 用户消息创建事件：

`type: conversation.item.created` 显示用户发送的消息 "Hello!" 已被成功创建和处理。

### 3. Assistant 响应事件：

`type: response.created` 和 `response.output_item.added` 表示 Assistant 开始生成响应，并且有一部分响应已经生成。

**响应内容**显示为 `{"type": "response.audio_transcript.delta", "delta": "Hey there! How's it going?"}`，其中 Assistant 的响应是音频内容，并且实时生成了文本 "Hey there! How's it going?"。

### 4. 音频相关事件：

`response.audio_transcript.delta` 中包含的 `delta` 是逐步生成的音频文本，最初是逐步输出“Hey there! How's it going?”。

### 5. 音频数据片段：

`'response.audio.delta'` 是 Assistant 在生成音频响应时的实时音频数据片段。这意味着每个 `delta` 都是一部分音频数据块，而不是一次性发送整个音频文件。它分段传输，逐步将生成的音频数据发送到客户端。

由于音频文件的体积较大，尤其是在实时应用场景中，它们往往被分割成多个 `delta` 片段，分别发送给客户端。这些片段会组成完整的音频内容，这就是为什么你会看到大量的 `response.audio.delta` 输出，每一块都是音频的一部分。

`response.audio.delta`中`delta`的类型为:

```log
Base64-encoded audio data delta.
```

示例:

```json
{
   "type": "response.audio.delta", 
   "event_id": "event_AI53pgarv1YBkPBezyZt8", 
   "response_id": "resp_AI53ppDU4wGbJ60x4p2kc", 
   "item_id": "item_AI53pHf9eHDjmWJ0snIjS", 
   "output_index": 0, 
   "content_index": 0, 
   "delta": "eQpjC5kLTA09DsUPnBEmEH4PNA/VD10SVxMNFE8UDhUkFT0V7xR7E6IU"
}
```

具体来说：

1. **`response.audio.delta` 的作用**：
   - 它代表一段音频数据。
   - `delta` 的每一部分是连续的音频数据，用于逐步传输完整的 Assistant 语音响应。

2. **占用的内容比较多**：
   - 因为音频比纯文本数据大得多，所以每个 `delta` 可能包含很多的音频数据块。当 Assistant 生成一个较长的响应时，音频数据会被分割成许多片段依次发送，导致输出中的 `response.audio.delta` 占据了较大比例。

3. **如何处理它**：
   - 如果你只关心文本内容，可以忽略这些 `audio.delta` 片段，专注于 `response.audio_transcript.delta`，后者是生成的文本。
   - 如果你需要处理音频数据，可以收集所有的 `audio.delta` 片段，然后在客户端拼接成一个完整的音频文件。


## 处理中断:

当服务器正在用音频进行响应时，可以对其进行中断，停止模型推理，但在对话历史中保留截断的响应。在 `server_vad` 模式下，当服务器端的 VAD 再次检测到输入语音时，就会发生这种情况。在任一模式下，客户端都可以发送 `response.cancel` 消息来显式中断模型。

服务器将以比实时更快的速度生成音频，因此服务器的中断点将与客户端音频播放的中断点不同。换句话说，服务器可能已经生成了比客户端为用户播放的更长的响应。客户端可以使用 `conversation.item.truncate` 来截断模型的响应，使其与客户端在中断前播放的内容一致。


## 继续对话

实时 API 是短暂的——在连接结束后，服务器不会存储会话和对话。如果客户端由于网络状况不佳或其他原因断开连接，您可以创建一个新会话，并通过向对话中注入条目来模拟之前的对话。

🚨目前，无法在新会话中提供之前会话的音频输出。我们的建议是，将之前的音频消息转换为新的文本消息，通过将转录文本传递回模型。

```json
// 会话 1

// [服务器] session.created
// [服务器] conversation.created
// ... 各种来回交互
//
// [连接因客户端断开而结束]

// 会话 2
// [服务器] session.created
// [服务器] conversation.created

// 从内存填充对话：
{
  type: "conversation.item.create",
  item: {
    type: "message",
    role: "user",
    content: [{
      type: "audio",
      audio: AudioBase64Bytes
    }]
  }
}

{
  type: "conversation.item.create",
  item: {
    type: "message",
    role: "assistant",
    content: [
      // 无法在新会话中填充之前会话的音频响应。
      // 我们建议将之前消息的转录转换为新的 "text" 消息，
      // 以便将类似的内容传递给模型。
      {
        type: "text",
        text: "好的，我能帮您什么？"
      }
    ]
  }
}

// 继续对话：
//
// [客户端] input_audio_buffer.append
// ... 各种来回交互
```


## 关于多轮对话的一些思考:

基于 `main_realtime.py` 要实现多轮对话，需要维护用户和助手之间的对话历史。这涉及到存储之前的消息，并在每次新请求中包含它们，以提供上下文。以下是实现多轮对话所需的步骤和代码修改：

1. **存储对话历史**：使用数据结构（如列表）来跟踪对话历史。在生产环境中，您可能需要使用数据库或会话管理。

2. **在请求中包含历史记录**：修改您的请求，包含对话历史，以便助手可以基于先前的上下文生成响应。

3. **修改WebSocket通信**：调整您的WebSocket消息，在适当的字段中发送对话历史。

具体来说，包含历史记录可以有两种方式:

1. 将历史对话作为指令(instructions)发送 `response.create` 事件。（实现简单）
2. 多次发送 `conversation.item.create` 事件，构建历史信息。

下面以第一种为例，讲解下代码修改方式:

---

### 步骤1：修改 `process_audio` 端点

首先，调整 `process_audio` 端点，以接受会话ID或使用某种形式的用户标识来跟踪对话历史。

```python
from fastapi import FastAPI, File, UploadFile, Depends
from typing import Optional

# 内存中存储对话历史
conversation_histories = {}

@app.post("/process_audio")
async def process_audio(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = None
):
    try:
        # 如果未提供会话ID，则生成一个
        if not conversation_id:
            import uuid
            conversation_id = str(uuid.uuid4())
        
        # 如果是新会话，则初始化对话历史
        if conversation_id not in conversation_histories:
            conversation_histories[conversation_id] = []

        # 读取上传的音频文件
        audio_bytes = await file.read()

        # 获取对话历史
        conversation_history = conversation_histories[conversation_id]

        # 调用函数并传入对话历史
        generator = connect_to_server(audio_bytes, conversation_history)

        # 返回会话ID，以便客户端在后续请求中使用
        headers = {"Conversation-ID": conversation_id}

        return StreamingResponse(generator, media_type="text/event-stream", headers=headers)
    except Exception as e:
        logger.error(f"处理音频时出错：{str(e)}")
        return JSONResponse(
            content={"code": 1, "msg": "处理失败", "error": str(e)},
            status_code=500
        )
```

### 步骤2：修改 `connect_to_server` 函数

将对话历史传递给 `send_user_audio` 函数，并根据助手的响应更新对话历史。

```python
async def connect_to_server(audio_bytes, conversation_history):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(api_url, headers=headers, proxy=proxy_url) as ws:
            logger.info("已连接到服务器。")
            # 发送用户音频和对话历史
            await send_user_audio(ws, audio_bytes, conversation_history)
            # 接收并处理消息
            async for message in ws:
                try:
                    response = message.json()
                    # 如果是流式文本，按照SSE格式返回
                    if response['type'] == 'response.audio_transcript.delta':
                        sse_message = f"data: {response['delta']}\n\n"
                        yield sse_message
                        # 将助手的响应添加到对话历史
                        conversation_history.append({"role": "assistant", "content": response['delta']})
                    elif response['type'] == 'response.audio_transcript.done':
                        logger.info("流式文本接收完毕。")
                        yield "event: end\n\n"
                        break
                except json.JSONDecodeError:
                    logger.error("收到无效的JSON消息。")
                except Exception as e:
                    logger.error(f"处理消息时出错：{str(e)}")
                    break
```

### 步骤3：修改 `send_user_audio` 函数

在 `response.create` 消息的 `instructions` 字段中包含对话历史。

```python
async def send_user_audio(ws, audio_bytes, conversation_history):
    # 将WAV文件进行base64编码
    event = audio_to_item_create_event(audio_bytes)
    # 发送音频事件
    await ws.send_json(event)
    # 将对话历史准备为字符串
    history_text = ""
    for message in conversation_history:
        role = message["role"]
        content = message["content"]
        history_text += f"{role}: {content}\n"

    # 准备带有指令的 response.create 消息
    response_create_message = {
        "type": "response.create",
        "response": {
            "instructions": history_text.strip()
        }
    }
    # 发送 response.create 消息
    await ws.send_json(response_create_message)
    # 将用户的消息添加到对话历史（这里可能是一个占位符，因为还未转录）
    conversation_history.append({"role": "user", "content": "[用户的音频输入]"})
```

**注意**：由于用户的当前输入是音频形式，你可能无法立即获得文本内容，直到助手将其转录。你可以根据应用程序的需要决定如何处理。

### 步骤4：在接收到响应后更新对话历史

在 `connect_to_server` 函数中，将助手的响应追加到对话历史中，以便在未来的请求中包含它们。

```python
# 在 connect_to_server 函数的异步循环内
if response['type'] == 'response.audio_transcript.delta':
    sse_message = f"data: {response['delta']}\n\n"
    yield sse_message
    # 将助手的响应添加到对话历史
    conversation_history.append({"role": "assistant", "content": response['delta']})
```

### 步骤5：处理对话清理（可选）

你可能希望清理旧的对话，或实现超时机制以删除不活跃的对话历史。

```python
import time

# 对话历史添加时间戳
conversation_histories[conversation_id] = {
    "history": [],
    "last_updated": time.time()
}

# 定期清理旧对话
def cleanup_conversations():
    while True:
        current_time = time.time()
        for conv_id in list(conversation_histories.keys()):
            if current_time - conversation_histories[conv_id]["last_updated"] > 3600:  # 1小时
                del conversation_histories[conv_id]
        time.sleep(600)  # 每10分钟运行一次

# 在后台线程中运行清理
import threading
threading.Thread(target=cleanup_conversations, daemon=True).start()
```

### 附加考虑

- **用户标识**：在实际应用中，您需要一种可靠的方法来识别用户并安全地管理他们的会话。
- **数据隐私**：确保存储对话历史符合数据隐私法律和法规。
- **错误处理**：实施全面的错误处理，以管理WebSocket通信过程中可能发生的异常。
- **可扩展性**：在生产环境中，考虑使用数据库或分布式缓存（如Redis）来存储对话历史。

### 更新的代码片段

以下是包含修改的更新代码：

```python
# ... [之前的导入和设置代码] ...

# 内存中存储对话历史
conversation_histories = {}

@app.post("/process_audio")
async def process_audio(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = None
):
    try:
        if not conversation_id:
            import uuid
            conversation_id = str(uuid.uuid4())
        
        if conversation_id not in conversation_histories:
            conversation_histories[conversation_id] = []

        audio_bytes = await file.read()
        conversation_history = conversation_histories[conversation_id]
        generator = connect_to_server(audio_bytes, conversation_history)
        headers = {"Conversation-ID": conversation_id}
        return StreamingResponse(generator, media_type="text/event-stream", headers=headers)
    except Exception as e:
        logger.error(f"处理音频时出错：{str(e)}")
        return JSONResponse(
            content={"code": 1, "msg": "处理失败", "error": str(e)},
            status_code=500
        )

async def connect_to_server(audio_bytes, conversation_history):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(api_url, headers=headers, proxy=proxy_url) as ws:
            logger.info("已连接到服务器。")
            await send_user_audio(ws, audio_bytes, conversation_history)
            async for message in ws:
                try:
                    response = message.json()
                    if response['type'] == 'response.audio_transcript.delta':
                        sse_message = f"data: {response['delta']}\n\n"
                        yield sse_message
                        # 将助手的响应添加到对话历史
                        conversation_history.append({"role": "assistant", "content": response['delta']})
                    elif response['type'] == 'response.audio_transcript.done':
                        logger.info("流式文本接收完毕。")
                        yield "event: end\n\n"
                        break
                except json.JSONDecodeError:
                    logger.error("收到无效的JSON消息。")
                except Exception as e:
                    logger.error(f"处理消息时出错：{str(e)}")
                    break

async def send_user_audio(ws, audio_bytes, conversation_history):
    event = audio_to_item_create_event(audio_bytes)
    await ws.send_json(event)
    history_text = ""
    for message in conversation_history:
        role = message["role"]
        content = message["content"]
        history_text += f"{role}: {content}\n"

    response_create_message = {
        "type": "response.create",
        "response": {
            "instructions": history_text.strip()
        }
    }
    await ws.send_json(response_create_message)
    # 添加用户的消息占位符
    conversation_history.append({"role": "user", "content": "[用户的音频输入]"})

# ... [剩余的代码] ...
```

### 测试多轮对话

在实现上述更改后，通过以下步骤测试应用程序：

1. 启动服务器。
2. 发送一个音频文件，并提供一个 `conversation_id`。
3. 接收助手的响应。
4. 使用相同的 `conversation_id` 发送另一个音频文件。
5. 确保助手的响应考虑到了之前的交互。
