# 使用 uv
uv venv .venv
source .venv/bin/activate  # Linux/Mac
uv pip install stagehand python-dotenv

# 或使用 pip
pip install stagehand python-dotenv

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
