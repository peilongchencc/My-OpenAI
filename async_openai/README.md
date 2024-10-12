# async openai

以异步方式访问openai的服务，详情可参考GitHub的 [openai-python](https://github.com/openai/openai-python) 项目。

- [async openai](#async-openai)
  - [文件简介:](#文件简介)

## 文件简介:

| 文件名                       | 作用                                   | 备注    |
|-----------------------------|---------------------------------------|---------|
| gradio_stream_openai.py     | 以Gradio启动的UI界面                    | 异步形式 |
| fastapi_sse_example.py      | 以FastAPI启动的后端服务                  | 异步形式 |
| sanic_sse_example.py        | 以Sanic启动的后端服务                    | 异步形式 |

注意: 笔者是为了模拟前端UI界面与后端交互，所以既使用了 Gradio 又使用了 FastAPI。如果你只想要通过界面与OpenAI交互，只使用Gradio即可。