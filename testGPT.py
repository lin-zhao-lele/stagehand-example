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
        await page.fill('input[placeholder="开始日期"]', '2025-07-01')
        await page.fill('input[placeholder="结束日期"]', '2025-08-26')
        await page.click('button:has-text("查询")')

        # 3. 等待表格行加载
        await page.wait_for_selector('tr.el-table__row', timeout=20000)

        page_no = 1
        while True:
            print(f"=== 第 {page_no} 页 ===")

            # 用 locator + count 的方式遍历本页所有公告行（异步）
            rows = page.locator("tr.el-table__row")
            row_count = await rows.count()
            for i in range(row_count):
                row = rows.nth(i)
                title_loc = row.locator("td a.ahover").first
                time_loc = row.locator("span.time").first

                has_title = await title_loc.count() > 0
                has_time = await time_loc.count() > 0

                title = (await title_loc.inner_text()).strip() if has_title else ""
                href = await title_loc.get_attribute("href") if has_title else ""
                when = (await time_loc.inner_text()).strip() if has_time else ""

                print(when, title, href)

            # 找“下一页”按钮并判断是否不可用
            next_btn = page.locator("button.btn-next")
            disabled_by_attr = await next_btn.is_disabled()  # 有 disabled 属性
            cls = (await next_btn.get_attribute("class")) or ""
            disabled_by_class = "disabled" in cls  # 或 class 含 disabled
            if disabled_by_attr or disabled_by_class:
                print("已经到最后一页，结束。")
                break

            # 记录当前激活页码文本，用于等待翻页完成
            active_loc = page.locator(".el-pager li.active")
            prev_active = ""
            try:
                prev_active = (await active_loc.inner_text()).strip()
            except:
                pass  # 如果没有页码，也不影响后续等待

            # 点击“下一页”
            await next_btn.click()

            # 等待页码变化；若无页码则退化为等待列表可见
            try:
                await page.wait_for_function(
                    "(prev) => {"
                    "  const a = document.querySelector('.el-pager li.active');"
                    "  return a && a.textContent.trim() !== prev;"
                    "}",
                    arg=prev_active,
                    timeout=5000
                )
            except:
                # 有些情况下页面用 loading mask，这里做一次兜底等待
                try:
                    await page.wait_for_selector(".el-loading-mask", state="detached", timeout=2000)
                except:
                    pass
                await page.wait_for_selector("tr.el-table__row", timeout=5000)

            page_no += 1





if __name__ == "__main__":
    asyncio.run(main())