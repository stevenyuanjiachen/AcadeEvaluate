from zhipuai import ZhipuAI
from pathlib import Path
import json

def upload(client, file_path):
    """
    上传文件

    参数:
    client: 客户端实例
    file_path: 文件路径，支持字符串或列表。如果是列表，则逐个上传文件。

    返回:
    上传文件的ID或ID列表
    """
    if isinstance(file_path, str):
        file_object = client.files.create(file=Path(file_path), purpose="file-extract")
        return file_object.id
    elif isinstance(file_path, list):
        file_ids = []
        for path in file_path:
            file_object = client.files.create(file=Path(path), purpose="file-extract")
            file_ids.append(file_object.id)
        return file_ids
    else:
        raise ValueError("file_path 参数必须是字符串或列表")

