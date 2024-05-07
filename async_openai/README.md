# async openai

本章介绍如何以异步方式访问openai的服务。参考网址如下:<br>

```log
https://github.com/openai/openai-python
```

- [async openai](#async-openai)
  - [Async usage:](#async-usage)
  - [Streaming responses:](#streaming-responses)


## Async usage:

Simply import `AsyncOpenAI` instead of `OpenAI` and use `await` with each API call:<br>

简单导入 `AsyncOpenAI` 替代 `OpenAI` 并在每个 API 调用时使用 `await` ：<br>

> 除了这些，其他和同步模式使用一致。

```python
import os
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


async def main() -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo",
    )


asyncio.run(main())
```

Functionality between the synchronous and asynchronous clients is otherwise identical.<br>

同步和异步客户端的功能在其他方面是相同的。<br>


## Streaming responses:

We provide support for streaming responses using Server Side Events (SSE).<br>

我们支持使用服务器端事件（SSE）来进行响应流处理。<br>

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
```

The async client uses the exact same interface.<br>

异步客户端使用完全相同的接口。<br>

> 只是加入了异步特有的 `async` 前缀。

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()


async def main():
    stream = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test"}],
        stream=True,
    )
    async for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")


asyncio.run(main())
```