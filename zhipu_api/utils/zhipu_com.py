from zhipuai import ZhipuAI


def getanswer_com(client, prompt: str, version: str = "glm-4-long"):
    response = client.chat.completions.create(
        model=version,  # 填写需要调用的模型编码
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
