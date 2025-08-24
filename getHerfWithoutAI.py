import asyncio
import os
from stagehand import Stagehand

save_dir = "downloads"
os.makedirs(save_dir, exist_ok=True)

async def save_pdf(stagehand, title):
    page = stagehand.page

    # 等待页面加载完成
    await page.wait_for_timeout(3000)

    # 如果 pdf_url 是相对路径，需要拼接域名 例如 /new/disclosure/detail?plate=szse&orgId=gssz0002031&stockCode=002031&announcementId=1222180577&announcementTime=2024-12-30%2011:00
    # if pdf_url.startswith("/"):
    #     pdf_url = "https://www.cninfo.com.cn" + pdf_url
    herf_url = "https://www.cninfo.com.cn/new/disclosure/detail?plate=szse&orgId=gssz0002031&stockCode=002031&announcementId=1222180577&announcementTime=2024-12-30%2011:00"

    # 下载 PDF
    pdf_data = await page.request.get(herf_url)
    filepath = os.path.join(save_dir, f"{title}.pdf")
    with open(filepath, "wb") as f:
        f.write(await pdf_data.body())
    print(f"✅ 已保存: {filepath}")


async def main():
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
    target_url = "https://www.cninfo.com.cn/new/disclosure/stock?orgId=gssz0002031&stockCode=002031#latestAnnouncement"
    await page.goto(target_url)
    await page.wait_for_timeout(5000)

    # 示例标题列表
    titles = [
        "巨轮智能：2024年第二次临时股东大会法律意见书"
    ]

    for t in titles:
        await save_pdf(stagehand, t)

    await stagehand.close()

asyncio.run(main())
