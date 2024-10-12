"""
Description: openai词向量获取、降维示例，验证 "手动降低维度" 和 "通过传参降低维度" 的区别:。
Notes: 
"""
import sys
import os

# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)
# 获取当前脚本的父目录的父目录
parent_directory_of_the_parent_directory = os.path.dirname(os.path.dirname(current_script_path))
# 将这个目录添加到 sys.path
sys.path.append(parent_directory_of_the_parent_directory)

import numpy as np
from loguru import logger
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv('env_config/.env.local')

# 设置日志
logger.remove()
logger.add("openai_stream.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

user_input = "《老人与海》这篇文章被选入了小学语文课本。"   # 用户输入会被转化为 [1 x dimension_n] 的列表

response = client.embeddings.create(
    input=user_input,
    model="text-embedding-3-small",
)

print("标准embedding调用:\n")
print(response.data[0].embedding)
print(type(response.data[0].embedding))
print(len(response.data[0].embedding))
# type(response.data[0].embedding)
# <class 'list'>
# len(response.data[0].embedding)
# 1536
print("\n标准embedding调用后，手动降低维度，并执行标准化操作:\n")
def normalize_l2(x):
    x = np.array(x)
    if x.ndim == 1:
        norm = np.linalg.norm(x)
        if norm == 0:
            return x
        return x / norm
    else:
        norm = np.linalg.norm(x, 2, axis=1, keepdims=True)
        return np.where(norm == 0, x, x / norm)

cut_dim = response.data[0].embedding[:256]
norm_dim = normalize_l2(cut_dim)    # norm_dim的数据类型为<class 'numpy.ndarray'>，可通过 `norm_dim.tolist()` 转为list形式。
print(norm_dim)
print(type(norm_dim))
print(len(norm_dim))

print("\n标准embedding调用，采用传参形式降低维度:\n")
para_response = client.embeddings.create(
    input=user_input,
    model="text-embedding-3-small",
    dimensions=256
)

para_dim = para_response.data[0].embedding  # list类型，长度256，数据为 [0.09904252737760544, -0.02682558260858059, -0.01077528577297926, 0.012549266219139099,...]
# 由于array类型的数据格式为 `[ 9.90425200e-02 -2.68255801e-02 -1.07752855e-02  1.25492662e-02 ...]`，数据含科学计数法(`e`)
# 所以想比较2个变量是否相同最好的方式不是将 array 转为 list，而是将 list 转为 array 。因为将 array 转为 list 会因为 `e` 的原因造成小数点后8位之后的数字精度缺失(9.90425200e-02 对应小数点后8位)。
para_dim_array = np.array(para_dim)
print(para_dim_array)
print(type(para_dim_array))
print(len(para_dim_array))

# 使用np.allclose进行比较，可以指定一个容忍度(9.90425200e-02 对应小数点后8位)
# - atol代表绝对容忍度，是一个非负的浮点数。
# - 1e-8是科学计数法表示的0.00000001，即1后面跟着8个零。
are_close = np.allclose(norm_dim, para_dim_array, atol=1e-8)

print(f"\nnorm_dim和para_dim是否几乎相等: {are_close}")
