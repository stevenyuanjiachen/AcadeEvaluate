import os
import requests
from typing import Generator, Union, List
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

S2_API_KEY = os.environ.get("S2_API_KEY", "")


def print_papers(papers):
    for idx, paper in enumerate(papers):
        print(
            f"{idx}  {paper['title']} || {','.join(author['name'] for author in paper['authors'])} || {paper['paperId']}"
        )


def find_paper_by_title(query=None, select=False):
    papers = None
    result_limit=10
    while not papers:
        if not query:
            query = input("Find papers about what: ")
        if not query:
            continue

        rsp = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            headers={"X-API-KEY": S2_API_KEY},
            params={
                "query": query,
                "limit": result_limit,
                "fields": "authors,title,url",
            },
        )
        rsp.raise_for_status()
        results = rsp.json()
        total = results["total"]
        if not total:
            print("No matches found. Please try another query.")
            continue

        print(f"Found {total} results. Showing up to {result_limit}.")
        papers = results["data"]
        # print_papers(papers)
        if not select:
            return papers
    
    selection = ""
    while not re.fullmatch("\\d+", selection):
        selection = input("Select a paper # to base recommendations on: ")
    return results["data"][int(selection)]



def get_citation_edges(**req_kwargs):
    """This helps with API endpoints that involve paging."""
    page_size = 1000
    offset = 0
    total_results = 0
    max_results = 1000

    while True:
        req_kwargs.setdefault("params", dict())
        req_kwargs["params"]["limit"] = page_size
        req_kwargs["params"]["offset"] = offset
        rsp = requests.get(**req_kwargs)
        rsp.raise_for_status()

        page = rsp.json()["data"]
        for element in page:
            yield element
            total_results += 1
            if total_results >= max_results:
                return

        if len(page) < page_size:
            break  # no more pages
        offset += page_size


def get_paper(paper_id):
    rsp = requests.get(
        f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}",
        headers={"X-API-KEY": S2_API_KEY},
        params={"fields": "title,authors"},
    )
    rsp.raise_for_status()
    return rsp.json()


def get_citations(paper_id):
    edges = get_citation_edges(
        url=f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations",
        headers={"X-API-KEY": S2_API_KEY},
        params={"fields": "title,authors,isOpenAccess,openAccessPdf"},
    )

    return list(edge["citingPaper"] for edge in edges)


# 下载 PDF 的函数
def download_papers_from_urls_singlecore(
    urls: list[str],
    directory: str,
    user_agent: str = "requests/2.0.0",
    timeout: int = 5,
    max_downloads: int = 10,
) -> Generator[tuple[str, Union[str, None, Exception]], None, None]:
    # 使用 Session 复用 TCP 连接
    pdf_num = 0

    with requests.Session() as session:
        session.headers.update({"user-agent": user_agent})  # 设置 User-Agent
        for idx, url in enumerate(urls):
            if pdf_num >= max_downloads:
                print(f"Downloaded {pdf_num} papers. Stopping...")
                break

            # download pdf
            try:
                # 自动生成文件名
                filename = os.path.join(directory, f"paper_{idx}.pdf")
                print(f"Downloading {url} to {filename}...")
                download_pdf(session, url, filename, timeout=timeout)
                pdf_num += 1
                yield (idx, url, filename, None)  # 返回成功信息
            except requests.exceptions.Timeout:
                print(f"Timeout occurred while downloading {url}. Skipping...")
                yield (idx, url, None, "Timeout")  # 返回超时信息
            except Exception as e:
                print(f"Failed to download {url}: {e}")
                yield (idx, url, None, e)  # 返回其他错误信息


# 下载 PDF 的函数
def download_papers_from_urls(
    urls: List[str],
    directory: str,
    user_agent: str = "requests/2.0.0",
    timeout: int = 5,
    max_downloads: int = 10,
    max_threads: int = 8  # 限制最大线程数
) -> Generator[tuple[int, str, Union[str, None, Exception]], None, None]:
    # 使用 Session 复用 TCP 连接
    pdf_num = 0
    with requests.Session() as session:
        session.headers.update({"user-agent": user_agent})  # 设置 User-Agent

        if len(urls) > max_downloads:
            urls = urls[:max_downloads]  # 限制下载数量
        
        # 使用 ThreadPoolExecutor 并行下载
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for idx, url in enumerate(urls):
                # 为每个下载任务提交一个线程
                futures.append(executor.submit(download_pdf_task, session, url, directory, idx, timeout))

            # 等待所有任务完成并处理结果
            for future in as_completed(futures):
                idx, url, filename, error = future.result()
                if error:
                    yield (idx, url, None, error)  # 返回错误信息
                else:
                    pdf_num += 1
                    yield (idx, url, filename, None)  # 返回成功信息

# 下载任务函数
def download_pdf_task(session: requests.Session, url: str, directory: str, idx: int, timeout: int) -> tuple[int, str, Union[str, None, Exception]]:
    try:
        # 自动生成文件名
        filename = os.path.join(directory, f"paper_{idx}.pdf")
        print(f"Downloading {url} to {filename}...")
        download_pdf(session, url, filename, timeout=timeout)
        return (idx, url, filename, None)  # 返回成功信息
    except requests.exceptions.Timeout:
        print(f"Timeout occurred while downloading {url}. Skipping...")
        return (idx, url, None, "Timeout")  # 返回超时信息
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return (idx, url, None, e)  # 返回其他错误信息


# 下载单个 PDF 的函数
def download_pdf(session: requests.Session, url: str, filepath: str, timeout: int):
    # 使用流式响应避免将整个文件加载到内存中
    with session.get(url, stream=True, verify=True, timeout=timeout) as response:
        response.raise_for_status()  # 检查请求是否成功
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):  # 分块写入文件
                f.write(chunk)


def main():

    # get the paper by title
    paper = find_paper_by_title(query=None, select=True)
    title = paper["title"]
    dir = os.path.dirname(os.path.abspath(__file__)) + f"/{title}_citationPDFs/"
    if not os.path.exists(dir):
        os.makedirs(dir)

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


if __name__ == "__main__":
    main()
