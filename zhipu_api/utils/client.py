from zhipuai import ZhipuAI

def client(apikey: str):
    """
    创建客户端实例

    参数:
    apikey: API 密钥

    返回:
    ZhipuAI 客户端实例
    """
    return ZhipuAI(api_key=apikey)
