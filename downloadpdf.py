import asyncio
import os
from dotenv import load_dotenv
from stagehand import Stagehand, StagehandConfig

# 加载.env文件中的环境变量到系统环境中
load_dotenv()

async def main():
    # 检查API密钥是否设置
    api_key = os.getenv("GEMINI_API_KEY")

    # 使用配置创建Stagehand实例
    config = StagehandConfig(
        env="LOCAL",
        model_name="google/gemini-2.0-flash",
        model_api_key=api_key,
        headless=False,
        verbose=3,
        debug_dom=True
    )
    stagehand = Stagehand(config)

    try:
        # 初始化Stagehand（启动浏览器会话）
        await stagehand.init()

        # 获取页面对象，用于后续的页面操作
        page = stagehand.page

        # 打开指定网站
        targetURL='https://www.cninfo.com.cn/new/disclosure/stock?orgId=gssz0002031&stockCode=002031#latestAnnouncement'
        await page.goto(targetURL)

        # 等待页面加载完成
        await page.wait_for_timeout(5000)

        # 找到文章 "巨轮智能：2025年半年度报告" 并保存它
        title = '巨轮智能：2025年半年度报告'

        await savePDF(page, title)

        
        print("✅ PDF下载完成")
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        # 确保关闭Stagehand
        await stagehand.close()

async def savePDF(page, title):
    await page.act(f"找到文章'{title}'的链接并保存链接内容到本地")

if __name__ == "__main__":
    asyncio.run(main())