import os
import asyncio
import sys
import json
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

BASE = "https://www.cninfo.com.cn"

async def main(configJson):
    async with Stagehand(config) as sh:
        # 读取配置文件
        with open(configJson, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        config_data['titles'] = []
        config_data['hrefs'] = []

        # 验证target_url是否以https://www.cninfo.com.cn开头
        target_url = config_data['target_url']
        if not target_url.startswith('https://www.cninfo.com.cn'):
            print("错误: 本项目能够处理的target_url是受限的，目前仅能处理针对https://www.cninfo.com.cn网站的请求")
            return

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

        titleList = []
        hrefList = []
        page_no = 1
        while True:
            print(f"\n=== 第 {page_no} 页 ===")

            # 等到至少有一条行可见（稳健）
            try:
                await page.wait_for_selector("tr.el-table__row", state="visible", timeout=10000)
            except Exception:
                print("等待 tr.el-table__row 超时，检测到本页无数据。")
                # 仍尝试读取一次
            rows_loc = page.locator("tr.el-table__row")
            row_count = await rows_loc.count()
            if row_count == 0:
                print("本页没有检测到任何公告行（count=0）。")
            else:
                for i in range(row_count):
                    row = rows_loc.nth(i)
                    title_loc = row.locator("td a.ahover").first
                    time_loc = row.locator("span.time").first

                    # 先检查元素是否存在
                    title = ""
                    href = ""
                    when = ""
                    try:
                        if await title_loc.count() > 0:
                            title = (await title_loc.inner_text()).strip()
                            href = await title_loc.get_attribute("href") or ""
                    except Exception as e:
                        # 元素可能在渲染中被替换，打印并继续
                        print(f"读取标题出错（row {i}）：{e}")

                    try:
                        if await time_loc.count() > 0:
                            when = (await time_loc.inner_text()).strip()
                    except Exception:
                        pass

                    titleList.append(title)
                    hrefList.append(urljoin(BASE, href))

                    print(when, title, href)

            # 取当前页第一条标题（用于等待下一页加载时判断是否变化）
            prev_first = ""
            try:
                first_title_loc = page.locator("tr.el-table__row td a.ahover").first
                if await first_title_loc.count() > 0:
                    prev_first = (await first_title_loc.inner_text()).strip()
            except Exception:
                prev_first = ""

            # 找“下一页”按钮
            next_btn = page.locator("button.btn-next")
            if await next_btn.count() == 0:
                print("没有找到下一页按钮，结束。")
                break

            # 如果按钮已经不可用，则退出
            try:
                if await next_btn.is_disabled():
                    print("下一页按钮已禁用，已到最后一页。")
                    break
            except Exception:
                # 某些情况下 is_disabled 可能抛异常，退而检查 class
                cls = (await next_btn.get_attribute("class")) or ""
                if "disabled" in cls:
                    print("下一页按钮 class 显示为 disabled，已到最后一页。")
                    break

            # 点击下一页
            await next_btn.click()

            # 等待页面内容真正变化：优先等待 first title 变化；若超时则等待行出现
            try:
                await page.wait_for_function(
                    "(prev) => { const el = document.querySelector('tr.el-table__row td a.ahover'); return el && el.textContent.trim() !== prev; }",
                    arg=prev_first,
                    timeout=10000
                )
            except Exception:
                # 兜底：等待新行出现（或 loading mask 消失）
                try:
                    await page.wait_for_selector(".el-loading-mask", state="detached", timeout=3000)
                except Exception:
                    pass
                try:
                    await page.wait_for_selector("tr.el-table__row", timeout=8000)
                except Exception:
                    # 如果仍然没有数据，打印提示并退出或继续重试
                    print("等待下一页的 tr.el-table__row 超时，尝试继续（可能是网络/渲染慢）。")
                    # 你可以选择 break，这里我们继续循环再尝试读取
                    # break

            page_no += 1

        config_data['titles'] = titleList
        config_data['hrefs']= hrefList

        with open(configJson, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # 获取命令行参数，如果没有提供则使用默认的config_1.json
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    asyncio.run(main(config_file))