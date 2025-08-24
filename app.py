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

        # 1. 打开网站https://www.cninfo.com.cn
        await page.goto("https://www.cninfo.com.cn")

        # 2. 在网站的搜索框内输入"巨能智能"
        await page.act("在搜索框中输入'巨能智能'")
        
        # 点击搜索按钮
        await page.act("点击搜索按钮")
        
        # 等待页面加载
        await page.wait_for_timeout(5000)
        
        # 3. 在搜索结果的页面中定位一个页面区域，标题是：包含"巨轮智能"关键词的搜索结果
        # 4. 在该页面区域，找到所有标题中包含"巨能智能："的文章
        # 5. 将所有文章的标题和链接地址输出到控制台
        print("🔍 正在提取页面内容...")
        try:
            # 先获取页面的文本内容进行调试
            page_content = await page.extract(instruction="提取页面的文本内容")
            print("📄 页面内容预览:", str(page_content)[:200] + "..." if len(str(page_content)) > 200 else page_content)
            
            # 尝试提取文章
            articles = await page.extract(
                instruction="找到页面中所有标题包含'巨能智能'的文章，提取它们的标题和链接地址"
            )
            
            # 6. 输出所有文章的标题和链接地址到控制台
            if articles:
                print("✅ 找到的文章:")
                # 如果返回的是字符串，尝试解析为对象
                if isinstance(articles, str):
                    print(articles)
                else:
                    # 如果是对象，格式化输出
                    if isinstance(articles, dict):
                        if 'articles' in articles and isinstance(articles['articles'], list):
                            for i, article in enumerate(articles['articles'], 1):
                                title = article.get('title', 'N/A')
                                link = article.get('link', 'N/A')
                                print(f"{i}. 标题: {title}")
                                print(f"   链接: {link}")
                        else:
                            print(articles)
                    else:
                        print(articles)
            else:
                print("❌ 未找到符合条件的文章")
        except Exception as e:
            print(f"❌ 提取过程中发生错误: {e}")
            # 打印页面URL以便调试
            current_url = page.url
            print(f"📍 当前页面URL: {current_url}")
        

    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        # 确保关闭Stagehand
        await stagehand.close()


if __name__ == "__main__":
    asyncio.run(main())