import asyncio
import os
import json
from dotenv import load_dotenv
from stagehand import Stagehand, StagehandConfig

# 加载.env文件中的环境变量到系统环境中
load_dotenv()


async def main(configJson):
    # 检查API密钥是否设置
    api_key = os.getenv("GEMINI_API_KEY")

    # 使用配置创建Stagehand实例
    config = StagehandConfig(
        env="LOCAL",
        model_name="google/gemini-2.0-flash",
        model_api_key=api_key,  # 去除可能的空格
        local_browser_launch_options={"headless": True},
        verbose=3,
        debug_dom=True
    )
    stagehand = Stagehand(config)

    # 读取配置文件
    with open(configJson, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    target_url = config_data['target_url']
    companyName = config_data['companyName']

    try:
        # 初始化Stagehand（启动浏览器会话）
        await stagehand.init()

        # 获取页面对象，用于后续的页面操作
        page = stagehand.page

        # 打开指定网站
        try:
            response = await page.goto(target_url)
            # 检查页面是否成功加载
            if response and response.status != 200:
                raise Exception(f"无法打开目标URL，HTTP状态码: {response.status}")
        except Exception as e:
            raise Exception(f"target_url不正确: {target_url}，错误详情: {str(e)}")

        # 等待页面加载完成
        await page.wait_for_timeout(5000)

        try:
            # 先获取页面的文本内容进行调试
            page_content = await page.extract(instruction=f"过滤页面的文本内容,要求包含'{companyName}'字符串")

            # 过滤重复的标题
            # 确保page_content是字符串类型
            if isinstance(page_content, dict):
                # 如果是字典类型，尝试获取文本内容
                content_text = str(page_content.get('text', page_content))
            elif isinstance(page_content, list):
                # 如果是列表，转换为字符串
                content_text = '\n'.join(str(item) for item in page_content)
            else:
                content_text = str(page_content)

            # 按行分割并去重
            titles = content_text.split('\\n')
            unique_titles = list(set(titles))

            # 过滤空字符串和空白字符
            unique_titles = [title.strip() for title in unique_titles if title and title.strip()]
            unique_titles = list(dict.fromkeys(t.strip("'") for t in titles if t.startswith(companyName)))
            print("✅ 过滤后的唯一标题数量:", len(unique_titles))

            # 检查是否找到任何标题
            if len(unique_titles) == 0:
                raise Exception(f"根据'{companyName}'检索不到任何信息，请检查companyName是否正确")

            # 将过滤后的标题存入config.json
            config_data['titles'] = unique_titles
            with open(configJson, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            print("✅ 标题已保存到config.json")


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
    asyncio.run(main('config.json'))