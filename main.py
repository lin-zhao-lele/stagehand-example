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

        await page.goto("https://www.aivi.fyi/")

        # 使用observe()获取所有博客文章链接
        blog_links = await page.observe("获取页面上所有可点击的博客文章和文章链接")
        print(f"✅ 发现 {len(blog_links)} 篇博客文章: {blog_links}")

        # 使用 for 循环处理所有博客链接
        for i, blog_link in enumerate(blog_links[:3]):  # 只处理前3篇博客
            print(f"\n🚀 正在处理第 {i + 1} 篇博客...")
            
            await page.act(blog_link)

            blog_data = await page.extract("提取博客的标题并总结博客内容")

            print(f"✅ 第 {i + 1} 篇博客: {blog_data}")

            # 如果不是最后一篇，返回主页
            if i < len(blog_links[:3]) - 1:
                await page.go_back()
                # 等待页面加载完成
                await page.wait_for_timeout(2000)
                
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        # 确保关闭Stagehand
        await stagehand.close()

if __name__ == "__main__":
    asyncio.run(main())