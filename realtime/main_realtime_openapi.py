"""
Description: 交互模式的openai realtime服务测试示例。
Notes: 
终端测试示例:
```bash
curl -N -X POST "http://localhost:8000/process_audio" -F "file=@/path/to/your/audio.wav"
```
"""
import asyncio
import aiohttp

async def main():
    url = 'http://localhost:8000/process_audio'  # 根据您的服务器实际地址调整
    # 根据您的文件地址调整
    filename = 'beijing.wav'
    
    async with aiohttp.ClientSession() as session:
        with open(filename, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename=filename, content_type='audio/wav')
            
            async with session.post(url, data=data) as resp:
                if resp.status != 200:
                    print(f"请求失败，状态码：{resp.status}")
                    text = await resp.text()
                    print(f"响应内容：{text}")
                    return
                
                # 因为响应是流式的，需要逐行读取
                # 响应的媒体类型为 'text/event-stream'
                async for line in resp.content:
                    decoded_line = line.decode('utf-8').strip()
                    if decoded_line:
                        print(decoded_line)
                
                print("流式响应结束。")

if __name__ == '__main__':
    asyncio.run(main())
