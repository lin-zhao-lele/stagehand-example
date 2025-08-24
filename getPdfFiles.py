import asyncio
import os
import json
from dotenv import load_dotenv
from stagehand import Stagehand

# 加载.env文件中的环境变量到系统环境中
load_dotenv()


async def main(configJson):
    # 检查API密钥是否设置
    api_key = os.getenv("GEMINI_API_KEY")

    # 读取配置文件
    with open(configJson, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    target_url = config_data['target_url']
    titles = config_data['titles']

    stagehand = None

    try:
        # 使用配置创建Stagehand实例
        stagehand = Stagehand(
            env="LOCAL",
            model_name="google/gemini-2.0-flash",
            model_client_options={"apiKey": api_key},
            local_browser_launch_options={"headless": True},
            verbose=3
        )

        # 初始化Stagehand（启动浏览器会话）
        await stagehand.init()

        # 获取页面对象，用于后续的页面操作
        page = stagehand.page

        # 打开指定网站
        await page.goto(target_url)

        # 等待页面加载完成
        await page.wait_for_timeout(5000)

        # 依次保存每个PDF
        for i, title in enumerate(titles):
            print(f"正在处理第 {i + 1} 个文件: {title}")
            try:
                await save_pdf(stagehand, title)
                # 等待一段时间确保下载完成
                await asyncio.sleep(30)  # 增加等待时间到30秒
            except Exception as e:
                print(f"处理文件 '{title}' 时出错: {e}")
                # 继续处理下一个文件而不是终止整个程序
                if i < len(titles) - 1:
                    await asyncio.sleep(10)

            # 如果不是最后一个文件，重新初始化Stagehand
            if i < len(titles) - 1:
                # 关闭当前Stagehand实例
                if stagehand:
                    await stagehand.close()

                # 重新创建Stagehand实例
                stagehand = Stagehand(
                    env="LOCAL",
                    model_name="google/gemini-2.0-flash",
                    model_client_options={"apiKey": api_key},
                    local_browser_launch_options={"headless": True},
                    verbose=3
                )
                await stagehand.init()
                page = stagehand.page

                # 重新打开指定网站
                await page.goto(target_url)
                await page.wait_for_timeout(5000)

        print("✅ 所有PDF下载完成")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        # 尝试关闭Stagehand实例
        if stagehand:
            try:
                await stagehand.close()
            except Exception as close_error:
                print(f"关闭Stagehand时出现警告: {close_error}")


async def save_pdf(stagehand, title):
    # 使用stagehand.page确保获取当前活动页面
    page = stagehand.page
    # 使用更精确的指令来定位元素
    await page.act(f"在表格中找到完全匹配'{title}'的链接并点击下载")




import sys

if __name__ == "__main__":
    # 获取命令行参数，如果没有提供则使用默认的config.json
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    asyncio.run(main(config_file))