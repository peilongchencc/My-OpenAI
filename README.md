# My-OpenAI:

OpenAI Code使用示例。

- [My-OpenAI:](#my-openai)
  - [文件简介:](#文件简介)
  - [system、user、assistant角色解析:](#systemuserassistant角色解析)
  - [附录: OpenAI关键界面](#附录-openai关键界面)
    - [API密钥页面:](#api密钥页面)
    - [OpenAI账单界面:](#openai账单界面)

## 文件简介:

| 文件夹名                     | 作用                                  | 备注 |
|-----------------------------|---------------------------------------|------|
| async_openai                | 以Gradio为前端，FastAPI为后端启用服务示例  |      |
| chat                        | openai chat服务代码示例                  |      |
| vision                      | openai 图像服务代码示例                   |      |
| embedding                   | openai embedding服务代码示例             |      |
| realtime                    | openai realtime服务代码示例              |      |
| token_count                 | openai token计算代码示例                 |      |


## system、user、assistant角色解析:

- system: 它设定了 AI 的行为、角色、和背景，或者你可以理解为语境。常常用于开始对话，给出一个对话的大致方向，或者设置对话的语气和风格。

ChatGPT网页端不显示system选项，你需要用`user`角色给予它定义。例如，输入："你是一个助理"或"你是一名历史教师"。这个消息可以帮助设定对话的语境，以便 AI 更好地理解其在对话中的角色。

- assistant: 即系统回复的内容，在使用 API 的过程中，你不需要直接生成 assistant 消息，因为它们是由 API 根据 system 和 user 消息自动生成的。

- user: 即用户输入，例如输入 "请给我一份使用python读取json文件的示例代码"


## 附录: OpenAI关键界面

### API密钥页面:

```log
https://platform.openai.com/api-keys
```

注意不要将你的 **OPENAI KEY** 上传到公共平台(例如GitHub)，一旦上传，OpenAI 会自动禁用该密钥。

### OpenAI账单界面:

```log
https://platform.openai.com/settings/organization/billing/overview
```