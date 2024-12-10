import gradio as gr
import yaml

from zhipu_api.utils.client import client

from title_2_citationPdf import *


class AcadeEvaluateWeb:
    def __init__(self):
        dir = os.path.dirname(os.path.abspath(__file__))

        # load config
        config_file = os.path.join(dir, "config\\config_test.yaml")
        with open(config_file, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        # list_path
        list_path = os.path.join(dir, "dataset\\list.txt")

        # LLM client
        self.client = client(config["model"]["api_key"])
        system = config["prompt"]["system"]
        version = config["model"]["model_version"]

        # init the webset
        self.web = gr.Blocks()
        with self.web:
            # TextBox
            self.paper_name_input = gr.Textbox(
                label="请输入想要查询的论文", placeholder="在这里输入论文名称..."
            )
            self.paper_recommend_output = gr.Textbox(label="查询到的论文")
            self.paper_id_input = gr.Textbox(
                label="请输入论文ID", placeholder="在这里输入Id...", visible=False
            )
            self.evaluate_output = gr.Textbox(label="评价结果", visible=False)

            # Buttons
            with gr.Row():
                self.find_btn = gr.Button("查询")
                self.clear_btn = gr.Button("清除")
                self.confirm_btn = gr.Button("确认论文", visible=False)

            self.find_btn.click(
                fn=self.find_clicked_event,
                inputs=self.paper_name_input,
                outputs=[
                    self.paper_recommend_output,
                    self.find_btn,
                    self.paper_id_input,
                    self.confirm_btn,
                ],
            )
            self.confirm_btn.click(
                fn=self.confirm_clicked_event,
                inputs=self.paper_id_input,
                outputs=[self.evaluate_output, self.evaluate_output],
            )
        self.web.launch(share=True)

    def find_clicked_event(self, query):
        self.papers = find_paper_by_title(query)
        papers_list = []
        for idx, paper in enumerate(self.papers):
            papers_list.append(
                f"{idx}. {paper['title']}\n\tAuthors: {', '.join(author['name'] for author in paper['authors'])}"
            )

        # show the id input and confirm button
        return (
            self.format_list(papers_list),
            gr.update(visible=False),   # find_btn
            gr.update(visible=True),    # paper_id_input
            gr.update(visible=True),    # confirm_btn
        )

    def confirm_clicked_event(self, paper_id: str):
        if not paper_id.isdigit():
            return "输入的ID不是数字，请重新输入", gr.update(visible=True)
        paper = self.papers[int(paper_id)]

        self.download_citations(paper)



    def format_list(self, list):
        formatted_list = "\n".join([f"{line}" for line in list])
        return formatted_list

    def download_citations(self, paper):
        # get the paper's citation
        citations = get_citations(paper["paperId"])
        print(f"Found {len(citations)} citations.")

        citationsDf = pd.DataFrame(citations)
        citationsDf.to_csv(dir + "citations.csv")  # 所有引用该文献的论文的信息
        pdfURLs = citationsDf.dropna(subset=["openAccessPdf"])["openAccessPdf"].tolist()
        urlDf = pd.DataFrame(pdfURLs)
        urlDf.to_csv(dir + "pdfURLs.csv")  # 有公开链接的文献的pdf链接
        citationURLs = urlDf["url"].tolist()
        for result in download_papers_from_urls(
            citationURLs, directory=dir, timeout=10
        ):  # 设置超时时间为 10 秒
            idx, url, filepath, error = result
            if error:
                print(f"{idx+1}/{len(citationURLs)} Error downloading {url}: {error}")
            else:
                print(f"{idx+1}/{len(citationURLs)} Downloaded {url} to {filepath}")
        
        

AcadeEvaluateWeb()
