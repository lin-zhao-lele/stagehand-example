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
        model_api_key=api_key,  # 去除可能的空格
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

        await page.goto("https://www.cninfo.com.cn/new/disclosure/stock?orgId=gssz0002031&stockCode=002031#latestAnnouncement")

        # 使用observe()获取所有博客文章链接
        blog_links = await page.observe("获取页面上最新公告区域内的所有的以'巨能智能：'开头的公告的标题、公告时间和指向的链接")
        print(f"✅ 发现 {len(blog_links)} 篇博客文章: {blog_links}")

        # 使用 for 循环处理所有博客链接
        for i, blog_link in enumerate(blog_links[:]):  #
            print(f"\n🚀 正在处理第 {i + 1} 篇公告..." )


    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        # 确保关闭Stagehand
        await stagehand.close()


if __name__ == "__main__":
    asyncio.run(main())