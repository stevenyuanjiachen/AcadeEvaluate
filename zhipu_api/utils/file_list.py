from zhipuai import ZhipuAI
from client import client
import os
def file_list(client, purpose="file-extract"):
    """
    获取文件列表

    参数:
    client: 客户端实例
    purpose: 文件用途，支持 "batch"、"file-extract"、"fine-tune"

    返回:
    文件列表结果
    """
    # 请求文件列表
    result = client.files.list(
        purpose=purpose,    # 支持 batch、file-extract、fine-tune
    )
    return result

