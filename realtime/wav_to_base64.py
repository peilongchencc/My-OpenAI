"""
Description: wav文件转base64，截断需要读者自己做。
Notes: 
Requirements:
pip install pydub
sudo apt update
sudo apt install ffmpeg
"""
import io
import json
import base64
from pydub import AudioSegment

def audio_to_item_create_event(audio_bytes: bytes) -> str:
    # Load the audio file from the byte stream
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    
    # Resample to 24kHz mono pcm16
    pcm_audio = audio.set_frame_rate(24000).set_channels(1).set_sample_width(2).raw_data
    
    # Encode to base64 string
    pcm_base64 = base64.b64encode(pcm_audio).decode()
    
    event = {
        "type": "conversation.item.create", 
        "item": {
            "type": "message",
            "role": "user",
            "content": [{
                "type": "input_audio", 
                "audio": pcm_base64
            }]
        }
    }
    # return json.dumps(event)
    return event

if __name__ == '__main__':
    with open("input_example.wav", "rb") as f:
        audio_bytes = f.read()
    # 调用函数
    event = audio_to_item_create_event(audio_bytes)
    print(event)
    print(type(event))