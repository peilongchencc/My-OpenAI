"""
@author:ChenPeilong(peilongchencc@163.com)
@description:According to the content count token number through GPT3.5 & GPT4 encoding methods, the results are consistent with the official website's token calculation.
@reference link:https://platform.openai.com/docs/guides/embeddings/frequently-asked-questions
"""

import tiktoken

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string.
    (返回一个文本字符串中的 tokens 数量。)
    """
    encoding = tiktoken.get_encoding(encoding_name)
    exact_tokens = encoding.encode(string)
    num_tokens = len(exact_tokens)
    return exact_tokens, num_tokens

content = "请将下列内容翻译为地道的中文"
# content = "tiktoken is great!"

exact_tokens_rtn, num_tokens_rtn = num_tokens_from_string(content, "cl100k_base")
print(f"\n数字编码的结果为:{exact_tokens_rtn}")
print(f"\ncontent所占token数为:{num_tokens_rtn}")

encoding = tiktoken.get_encoding("cl100k_base")
restore_str = encoding.decode(exact_tokens_rtn)
print(f"\ncontent原文为:{restore_str}")

token_byte = [encoding.decode_single_token_bytes(token) for token in exact_tokens_rtn]
print(f"\n编码后的结果为:{token_byte}")
# 英文编码的内容人类可识别, 例如 [b't', b'ik', b'token', b' is', b' great', b'!']
# 中文编码的内容人类不可识别, 例如 [b'\xe8\xaf\xb7', b'\xe5\xb0\x86', b'\xe4\xb8\x8b', b'\xe5\x88\x97', ...],解码后更一睹

# 使用utf-8编码将每个字节序列解码为字符串
decoded_strings = [token.decode('utf-8', errors='replace') for token in token_byte]

print(f"\n解码后的文本为:{decoded_strings}")