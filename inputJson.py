import os
import sys
import json
import asyncio
from urllib.parse import urljoin
from dotenv import load_dotenv
from stagehand import Stagehand, StagehandConfig

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

config = StagehandConfig(
    env="LOCAL",
    model_name="google/gemini-2.0-flash",
    model_api_key=api_key,
    local_browser_launch_options={"headless": True},
    verbose=3,
    debug_dom=True
)

# config = StagehandConfig(
#     env="LOCAL",
#     model_name="deepseek-ai/DeepSeek-V3",
#     model_api_key="",
#     local_browser_launch_options={"headless": True},
#     verbose=3,
#     debug_dom=True
# )

BASE = "https://www.cninfo.com.cn"

async def main(configJson):
    async with Stagehand(config) as sh:
        # 读取配置文件
        with open(configJson, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        target_url = config_data['target_url']
        startDate = config_data['startDate']
        endDate = config_data['endDate']

        page = sh.page

        # 1. 打开公告页面
        await page.goto(target_url)

        # 2. 输入日期并点击查询
        await page.fill('input[placeholder="开始日期"]', startDate)
        await page.fill('input[placeholder="结束日期"]', endDate)
        await page.click('button:has-text("查询")')

        # 3. 等待表格行加载
        await page.wait_for_selector('tr.el-table__row', timeout=20000)

        # 4. 遍历公告行
        rows = await page.query_selector_all('tr.el-table__row')
        titles, hrefs, times = [], [], []

        for row in rows:
            a_tag = await row.query_selector('a[href*="/new/disclosure/detail"]')
            time_span = await row.query_selector('span.time')

            if a_tag:
                title = (await a_tag.inner_text() or "").strip()
                href = await a_tag.get_attribute("href")
                full_url = urljoin(BASE, href) if href else None
                titles.append(title)
                hrefs.append(full_url)

            if time_span:
                times.append((await time_span.inner_text()).strip())
            else:
                times.append("")


        config_data['titles'] = titles
        config_data['hrefs'] = hrefs
        with open(configJson, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)

        print("✅ 标题已保存到config.json")

        # 打印结果
        for t, h, tm in zip(titles, hrefs, times):
            print(f"{tm} | {t} -> {h}")

if __name__ == "__main__":
    # 获取命令行参数，如果没有提供则使用默认的config_1.json
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    asyncio.run(main(config_file))