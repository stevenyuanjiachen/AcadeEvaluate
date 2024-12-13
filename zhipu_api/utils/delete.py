from zhipuai import ZhipuAI

def delete(client, id):
    """
    删除文件

    参数:
    client: 客户端实例
    id: 文件ID，支持字符串或列表。如果是列表，则逐个删除文件。

    返回:
    删除结果
    """
    if isinstance(id, str):
        result = client.files.delete(
            file_id=id  # 支持 retrieval、batch、fine-tune、file-extract 文件
        )
    elif isinstance(id, list):
        result = []
        for file_id in id:
            res = client.files.delete(
                file_id=file_id  # 支持 retrieval、batch、fine-tune、file-extract 文件
            )
            result.append(res)
    else:
        raise ValueError("id 参数必须是字符串或列表")
    
    return result
