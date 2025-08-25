import asyncio
import os
import sys
import json
from dotenv import load_dotenv
from stagehand import Stagehand

# 加载.env文件中的环境变量到系统环境中
load_dotenv()
save_dir = "downloads"
os.makedirs(save_dir, exist_ok=True)

async def save_pdf(stagehand, title, pdf_url):
    page = stagehand.page

    # 等待页面加载完成
    await page.wait_for_timeout(3000)

    # 下载 PDF
    pdf_data = await page.request.get(pdf_url)
    filepath = os.path.join(save_dir, f"{title}.pdf")
    with open(filepath, "wb") as f:
        f.write(await pdf_data.body())
    print(f"✅ 已保存: {filepath}")

async def main(configJson):
    with open(configJson, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    # 验证target_url是否以https://www.cninfo.com.cn开头
    target_url = config_data['target_url']
    if not target_url.startswith('https://www.cninfo.com.cn'):
        print("错误: 本项目能够处理的target_url是受限的，目前仅能处理针对https://www.cninfo.com.cn网站的请求")
        return
        
    titles = config_data['titles']
    hrefs = config_data['hrefs']

    # 初始化 Stagehand（不使用 AI）
    stagehand = Stagehand(
        env="LOCAL",
        model_name=None,
        model_client_options=None,
        local_browser_launch_options={"headless": True},
        verbose=3
    )
    await stagehand.init()
    page = stagehand.page

    # 打开公告列表页面
    await page.goto(target_url)
    await page.wait_for_timeout(5000)

    # 遍历titles和hrefs列表，下载对应的PDF文件
    for title, href in zip(titles, hrefs):
        await save_pdf(stagehand, title, href)

    await stagehand.close()


if __name__ == "__main__":
    # 获取命令行参数，如果没有提供则使用默认的config.json
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    asyncio.run(main(config_file))