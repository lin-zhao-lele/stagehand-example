import os
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
    local_browser_launch_options={"headless": False},
    verbose=3,
    debug_dom=True
)

BASE = "https://www.cninfo.com.cn"
URL  = "https://www.cninfo.com.cn/new/disclosure/stock?orgId=gssz0002031&stockCode=002031#latestAnnouncement"

async def main():
    async with Stagehand(config) as sh:
        page = sh.page

        # 1. 打开公告页面
        await page.goto(URL)

        # 2. 输入日期并点击查询
        await page.fill('input[placeholder="开始日期"]', '2025-08-01')
        await page.fill('input[placeholder="结束日期"]', '2025-08-21')
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

        # 打印结果
        for t, h, tm in zip(titles, hrefs, times):
            print(f"{tm} | {t} -> {h}")

        return titles, hrefs, times

if __name__ == "__main__":
    titles, hrefs, times = asyncio.run(main())