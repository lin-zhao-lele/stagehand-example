# 使用 uv
uv venv .venv
source .venv/bin/activate  # Linux/Mac
uv pip install stagehand python-dotenv google-generativeai

# 或使用 pip
pip install stagehand python-dotenv google-generativeai

# 完整安装playwright
python -m playwright install

# 指定安装特定浏览器
# python -m playwright install chromium


# 提示
example.py 给出了一个示例，如何在Stagehand的框架内使用gemini的api；使用context7参考Stagehand相关文档，修改app.py实现以下的功能
1 打开网站https:/https://www.cninfo.com.cn
2 在网站的搜索框内输入 ”巨能智能“，然后在搜索结果的页面中定位一个页面区域， 标题是： 包含"巨轮智能"关键词的搜索结果
3 在该页面区域，找到所有标题中包含 ”巨能智能：“的文章
4 将所有文章的标题和链接地址输出到控制台

example.py 给出了一个示例，如何在Stagehand的框架内使用gemini的api；使用context7参考Stagehand相关文档，新建test1.py实现以下的功能
1 打开网站https://www.cninfo.com.cn/new/fulltextSearch?notautosubmit=&keyWord=巨轮智能
3 查找所有包含onclick的超链接标签，提取每个超链接标签的onclick和href属性
4 将所有onclick和href信息输出到控制台

example.py 给出了一个示例，如何在Stagehand的框架内使用gemini的api；使用context7参考Stagehand相关文档，新建downloadpdf.py实现以下的功能
1 打开网站 https://www.cninfo.com.cn/new/disclosure/stock?orgId=gssz0002031&stockCode=002031#latestAnnouncement
2 找到文章 ”巨轮智能：2025年半年度报告“
3 下载链接里面的pdf文档，保存到本地./download目录下