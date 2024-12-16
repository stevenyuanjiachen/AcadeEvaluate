import gradio as gr
import yaml

from zhipu_api.utils.client import client

from title_2_citationPdf import *
from zhipu_api.func_dataset import *
from zhipu_api.utils.zhipu_com import getanswer_com


def sanitize_folder_name(s, max_length=255):
    # 定义不适合做文件夹名字的字符
    invalid_chars = r'[<>:"/\\|?* ]'
    # 使用正则表达式替换这些字符为空字符串
    sanitized_name = re.sub(invalid_chars, "", s)
    # 截断字符串到最大长度
    if len(sanitized_name) > max_length:
        sanitized_name = sanitized_name[:max_length]
    return sanitized_name


class AcadeEvaluateWeb:
    def __init__(self):
        dir = os.path.dirname(os.path.abspath(__file__))

        # load config
        config_file = os.path.join(dir, "config/config.yaml")
        with open(config_file, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        # LLM client
        self.client = client(config["model"]["api_key"])
        self.version = config["model"]["model_version"]
        
        file_list = self.client.files.list()
        for file in file_list.data:
            self.client.files.delete(file.id)

        # download path
        self.download_path = os.path.join(dir, "citationPDFs")

        # init the webset
        self.searched_result = []
        self.web = gr.Blocks()
        with self.web:
            # TextBox
            self.paper_name_input = gr.Textbox(
                label="请输入想要查询的论文", placeholder="在这里输入论文名称..."
            )
            self.find_btn = gr.Button("查询")
            self.paper_recommend_output = gr.Radio(
                label="查询到的论文", interactive=True, choices=[]
            )
            self.evaluate_output = gr.Markdown(label="评价结果", visible=False)

            user_choice_output = gr.Textbox(label="Your Choice", interactive=False)
            self.confirm_btn = gr.Button("确认论文", visible=False)

            # Find button
            self.find_btn.click(
                fn=self.find_clicked_event,
                inputs=self.paper_name_input,
                outputs=[
                    self.paper_recommend_output,
                    # self.find_btn,
                    # self.paper_id_input,
                    self.confirm_btn,
                ],
            )
            self.paper_recommend_output.change(
                fn=self.display_choice,
                inputs=self.paper_recommend_output,
                outputs=user_choice_output,
            )
            # Confirm button
            self.confirm_btn.click(
                fn=self.confirm_clicked_event, inputs=None, outputs=self.evaluate_output
            )
            self.confirm_btn.click(
                fn=self.show_TextBox,
                inputs=None,
                outputs=self.evaluate_output,
            )

        self.web.launch(share=True)

    def find_clicked_event(self, query):
        self.papers = find_paper_by_title(query)
        papers_list = []
        for idx, paper in enumerate(self.papers):
            papers_list.append(
                f"{idx}. {paper['title']}\n\tAuthors: {', '.join(author['name'] for author in paper['authors'])}"
            )
        article_title = []
        for i in range(len(self.papers)):
            article_title.append(f"{self.papers[i]['title']}")
        # show the id input and confirm button
        return (
            gr.update(choices=article_title),
            # gr.update(visible=False),   # find_btn
            # gr.update(visible=True),    # paper_id_input
            gr.update(visible=True),  # confirm_btn
        )

    def display_choice(self, selected_article):
        print(selected_article)
        self.article_title = selected_article
        self.id = -1
        for id, article in enumerate(self.papers):
            if selected_article == article["title"]:
                self.id = id
        return f"You selected: {selected_article},id:{self.id}"

    def confirm_clicked_event(self):
        paper = self.papers[int(self.id)]
        self.download_citations(paper)
        return self.evaluate_paper(paper)

    def show_TextBox(self):
        return gr.update(visible=True)

    def download_citations(self, paper):
        # get the paper's citation
        citations = get_citations(paper["paperId"])
        print(f"Found {len(citations)} citations.")

        # create a directory for the paper
        dir = self.download_path
        if not os.path.exists(dir):
            os.makedirs(dir)
        # 清空该论文的文件夹
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

        citationsDf = pd.DataFrame(citations)
        citationsDf.to_csv(
            os.path.join(dir, "citations.csv")
        )  # 所有引用该文献的论文的信息
        pdfURLs = citationsDf.dropna(subset=["openAccessPdf"])["openAccessPdf"].tolist()
        urlDf = pd.DataFrame(pdfURLs)
        urlDf.to_csv(os.path.join(dir, "pdfURLs.csv"))  # 有公开链接的文献的pdf链接
        citationURLs = urlDf["url"].tolist()

        for result in download_papers_from_urls(
            citationURLs, directory=dir, timeout=5, max_downloads=5
        ):  # 设置超时时间为 10 秒
            idx, url, filepath, error = result
            if error:
                print(f"{idx+1}/{len(citationURLs)} Error downloading {url}: {error}")
            else:
                print(f"{idx+1}/{len(citationURLs)} Downloaded {url} to {filepath}")

    def evaluate_paper(self, paper):
        if self.article_title is None:
            return "请先选择一篇论文！"

        create_dataset_folder(
            client= self.client,
            paper_name= self.article_title,
            pdf_dir= "./citationPDFs",
        )
        content = get_dataset_content(
            client= self.client,
            pdf_dir= self.download_path
        )
        answer = getanswer_com(self.client, content,  self.version)
        delete_dataset_folder(self.client, self.download_path)
        return answer


AcadeEvaluateWeb()
