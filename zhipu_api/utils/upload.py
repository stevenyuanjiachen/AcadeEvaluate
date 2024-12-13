from zhipuai import ZhipuAI
from pathlib import Path
import json
import os
#---------------------------用于上传pdf到智谱，返回文件id-----------------------------------
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

def upload_folder(client, folder_path):
    """
    上传文件夹中的所有文件

    参数:
    client: 客户端实例
    folder_path: 文件夹路径

    返回:
    上传文件的ID列表
    """
    file_ids = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_id = upload(client, file_path)
            file_ids.append(file_id)
    return file_ids
