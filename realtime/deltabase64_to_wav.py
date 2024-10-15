"""
Description: 工具函数--base64音频帧转wav。
Notes: 
"""
import base64
import wave

def base64_to_wav(base64_string, output_filename):
    # 解码Base64字符串
    audio_data = base64.b64decode(base64_string)
    
    # 打开一个WAV文件用于写入
    with wave.open(output_filename, 'wb') as wav_file:
        # 设置参数，这里假设是单声道，采样率为44100
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16位深度
        wav_file.setframerate(24000)
        # wav_file.setframerate(44100)
        # wav_file.setframerate(16000)
        
        # 写入解码后的音频数据
        wav_file.writeframes(audio_data)


if __name__ == '__main__':
    # Base64编码的音频数据字符串
    base64_string = '你的Base64编码数据'
    # 输出文件名
    output_filename = 'output.wav'

    # 调用函数
    base64_to_wav(base64_string, output_filename)