import os
import sys
import shutil  # 新增导入
from zhipuai import ZhipuAI
from pathlib import Path
import json
from zhipuai import ZhipuAI

# ---------------导入zhipu的api函数---------------------------------------------------
from zhipu_api.utils.delete import delete
from zhipu_api.utils.zhipu_com import getanswer_com
from zhipu_api.utils.upload import upload, upload_folder
from zhipu_api.utils.file_list import file_list


# --------------------等待完成的文件内容提取函数，输入为pdf文件提取的字符内容，输出为你想要输入给LLM的内容，目前采用完全输出（identity)-------------------------------------------------------
def pdf_process(content):
    """
    处理pdf文件内容,返回关键内容"""
    return content


# -------------------主要函数：创建数据库文件夹，删除数据库文件夹，获取数据库文件夹内容-----------------------------------------------------
def create_dataset_folder(
    client,
    paper_name: str,
    pdf_dir: str = "./citationPDFs",
):
    """
    创建数据库文件夹，上传PDF文件和文件夹内容，并生成list.txt文件记录文件ID

    参数:
    client: ZhipuAI客户端实例
    pdf_file_path: 单个PDF文件的路径，默认是第一篇论文（被引论文）
    pdf_folder_path: 包含多个PDF文件的文件夹路径（引用第一篇论文的论文）
    db_folder_absolute_path: 数据库文件夹的绝对路径
    specified_folder_name: 指定创建的文件夹名称
    """
    # 创建list.txt文件
    list_path = os.path.join(pdf_dir, "list.txt")
    with open(list_path, "w") as list_file:
        # 写入要评价的论文名称
        list_file.write(f"{paper_name}\n")

        # 上传pdf_folder_path并写入id列表
        pdf_ids = upload_folder(client, pdf_dir)
        for pdf_id in pdf_ids:
            list_file.write(f"{pdf_id}\n")


def delete_dataset_folder(client, pdf_dir: str = "./citationPDFs"):
    """
    删除数据库文件夹及其内容，先删除文件库中的文件，再删除本地文件夹

    参数:
    client: ZhipuAI客户端实例
    db_folder_absolute_path: 数据库文件夹的绝对路径
    specified_folder_name: 指定删除的文件夹名称
    """
    # 读取list.txt文件
    target_folder_path = pdf_dir
    list_file_path = os.path.join(target_folder_path, "list.txt")
    with open(list_file_path, "r") as list_file:
        lines = list_file.readlines()
    id_list = [line.strip() for line in lines[1:]]
    # 删除文件库中的文件
    for id in id_list:
        delete(client, id=id)
    # 删除指定文件夹
    # target_folder_path = os.path.join(db_folder_absolute_path, specified_folder_name)
    # shutil.rmtree(target_folder_path)  # 修改为shutil.rmtree


def get_dataset_content(client, pdf_dir: str = "./citationPDFs"):
    """
    获取数据库文件夹中的内容，返回所有文件的内容摘要和相互引用关系

    参数:
    client: ZhipuAI客户端实例
    db_folder_absolute_path: 数据库文件夹的绝对路径
    specified_folder_name: 指定获取内容的文件夹名称
    """
    # 读取list.txt文件
    list_path = os.path.join(pdf_dir, "list.txt")
    with open(list_path, "r") as list_file:
        lines = list_file.readlines()
    
    paper_name = lines[0].strip()
    id_list = [line.strip() for line in lines[1:]]
    
    # 请求文件列表
    prompt_context = f'''
    现在我有一篇论文，标题为{paper_name}，下面这些论文引用了{paper_name}，请找出这些论文分别是怎么引用{paper_name}的：并据此给出对{paper_name}的评价。
    以下是这些论文的内容：
    '''
    i = 0
    for id in id_list:
        i += 1
        content = json.loads(client.files.content(id).content)["content"]
        content = pdf_process(content)
        prompt_context += f"第{i}篇论文的内容为：\n{content}\n"
    prompt_context += f"请找出这些论文分别是怎么引用{paper_name}的：并据此给出对{paper_name}的评价"
    return prompt_context


# -------------------云端数据库函数：获取当前api的文件库中的文件列表，获取文件名列表，删除id-----------------------------------------------------


def get_filelist(client):
    """
    获取文件库中的文件数量，上限为100

    参数:
    client: ZhipuAI客户端实例
    """
    filelist = file_list(client)
    return filelist


def get_filenames(filelist):
    """
    获取filelist中的所有文件名

    参数:
    filelist: ListOfFileObject实例

    返回:
    包含所有文件名的列表
    """
    filenames = [file.filename for file in filelist.data]
    return filenames


def get_file_id(filelist):
    """
    获取filelist中的所有文件id

    参数:
    filelist: ListOfFileObject实例

    返回:
    包含所有文件id的列表
    """
    fileids = [file.id for file in filelist.data]
    return fileids


def delete_id(
    client,
    id,
):
    """将传入的id对应的文件在云端删除，可以是一个id或者一个列表"""
    delete(client, id)


# -------------------测试函数-----------------------------------------------------
if __name__ == "__main__":
    # ...existing code...
    client = ZhipuAI(api_key="c78468f91461f654f4e4d882f9bc5481.6TcFNbpFK7KV1DtD")
    pdf_file_path = "C:/Users/kaich/Desktop/二值化论文整理/one_bit_LLM/OneBit.pdf"
    pdf_folder_path = "C:/Users/kaich/Desktop/二值化论文整理/one_bit_LLM"
    db_folder_absolute_path = "C:/Users/kaich/Desktop/new/AcadeEvaluate/dataset"
    specified_folder_name = (
        "0"  #'BiLLMPushingtheLimitofPost-TrainingQuantizationforLLMs'
    )
    # create_dataset_folder(client, pdf_file_path, pdf_folder_path, db_folder_absolute_path, specified_folder_name)
    # delete_dataset_folder(client, db_folder_absolute_path,specified_folder_name)
    # 测试get_file_content功能
    # list_file_path = 'C:/Users/kaich/Desktop/ZhipuLLM/dataset/dataset_0/list.txt'
    filelist = get_filelist(client)
    filenames = get_filenames(filelist)
    print(filelist)
    delete(client, id=get_file_id(filelist))
    # filelist = get_filelist(client)
    # print(get_filenames(filelist))
    # content = get_dataset_content(client,db_folder_absolute_path,specified_folder_name )
    # with open('test.txt', 'w', encoding='utf-8') as output_file:
    #    output_file.write(content)
    # response=getanswer_com(client,content,system="你是一个热心的文件整理员",version="glm-4-long")
    # with open('output.txt', 'w', encoding='utf-8') as output_file:
    #   output_file.write(response)
# ...existing code...
