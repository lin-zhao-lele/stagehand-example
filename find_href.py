import asyncio
import os
from dotenv import load_dotenv
from stagehand import Stagehand, StagehandConfig
# 加载环境变量

# 1 打开网站 https://www.cninfo.com.cn/new/disclosure/stock?orgId=gssz0002031&stockCode=002031#latestAnnouncement
# 3 查找所有包含onclick的超链接标签，提取每个超链接标签的onclick和href属性
# 4 将所有onclick和href信息输出到控制台

load_dotenv()

async def main():
    # 配置Stagehand
    config = StagehandConfig(
        env="LOCAL",
        model_name="google/gemini-2.0-flash",
        model_api_key=os.getenv("GEMINI_API_KEY"),
        headless=False,
        verbose=3
    )
    stagehand = Stagehand(config)
    
    try:
        # 初始化Stagehand
        await stagehand.init()
        page = stagehand.page
        
        # 导航到指定网页
        await page.goto("https://www.cninfo.com.cn/new/disclosure/stock?orgId=gssz0002031&stockCode=002031#latestAnnouncement")
        
        # 等待页面加载完成
        await page.wait_for_timeout(5000)
        
        # 使用JavaScript直接获取页面上所有包含onclick属性的超链接
        js_script = """
        const links = Array.from(document.querySelectorAll('a[onclick]'));
        const result = links.map(link => ({
            onclick: link.getAttribute('onclick'),
            href: link.getAttribute('href')
        }));
        result;
        """
        
        # 执行JavaScript并获取结果
        links_data = await page.evaluate(js_script)
        
        # 提取onclick和href属性
        extracted_links = []
        if isinstance(links_data, list):
            for link in links_data:
                if link.get('onclick') or link.get('href'):
                    extracted_links.append({
                        'onclick': link.get('onclick', ''),
                        'href': link.get('href', '')
                    })
        
        # 输出结果到控制台
        print(f"共找到 {len(extracted_links)} 个包含onclick或href属性的超链接:")
        for i, link in enumerate(extracted_links, 1):
            print(f"{i}. onclick: {link['onclick']}")
            print(f"   href: {link['href']}")
            print()
            
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭Stagehand
        await stagehand.close()

if __name__ == "__main__":
    asyncio.run(main())