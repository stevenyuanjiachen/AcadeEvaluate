# AcadeEvaluate

> 建议科学上网

## Run

### 1. 打开网页

使用 conda 来创建环境 evaluate
```shell
conda env create -f ./requirements.yml
conda activate evaluate
```

如果创建过 evaluate 环境，可以
```shell
conda env update -f requirements.yml
conda activate evaluate
```

然后运行
```shell
python web.py
```

在浏览器中打开 [http://127.0.0.1:7860/](http://127.0.0.1:7860/)

### 2. 搜索并选择论文

1. 在第一个输入框中输入关键词，点击“搜索”。
2. 在找到的论文列表中选择一个，在第二个输入框中输入选择的论文前的 Id, 点击“确定论文”，
3. 等待一段时间后输出评价结果


## 说明

### title_2_citationPdf.py

运行后输入关键词，选择返回的候选列表中的一篇文献，即开始下载cite它的所有可下载pdf，将会创建一个文件夹。

文件夹包括：

* citations.csv：所有引用该文献的论文的信息表
* pdfURLs.csv：有公开链接的文献的pdf链接表


## TODO
- [x] 根据论文标题搜索论文
- [x] 选择需要的论文(记为A)
- [x] 下载所有引用了A的论文的 pdf, 并保存在 citationPDFs 文件夹中
- [ ] 将 citationPDFs 文件夹中的pdf输入给大模型，让大模型去找出这些文献分别在哪里引用了A，把这些信息保存下来
- [ ] 让大模型去评价