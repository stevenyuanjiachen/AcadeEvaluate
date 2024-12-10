from zhipuai import ZhipuAI
from pathlib import Path
import json

def get_file_content(client,path):
    """
    获取文件上下文
    从给定的path中获取id列表

    参数:
    client: 客户端实例
    path: 存放文件id的文件路径

    返回:
    文件列表结果
    """
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    id_list=[line.strip() for line in lines]
    # 请求文件列表
    prompt_context="以下是文件库中的文件：\n"
    i=0
    for id in id_list:
        i+=1
        content = json.loads(client.files.content(id).content)["content"]
        prompt_context+=f"第{i}个文件的内容为：\n{content}\n"

    return prompt_context
