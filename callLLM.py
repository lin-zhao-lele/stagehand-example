import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
from openai import OpenAI

# 加载 .env 中的 API Keys
load_dotenv()

# 配置 API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 配置模型名称
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")
DEEPSEEK_MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")

# 配置 Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_llm_provider():
    """
    从环境变量获取LLM提供商设置，如果没有设置则默认使用Gemini
    """
    return os.getenv("LLM_PROVIDER", "gemini").lower()

def call_gemini_analyze_pdf(pdf_path):
    """
    调用 Gemini 分析 PDF 文档
    """
    try:
        # 确保pdf_path是Path对象
        if isinstance(pdf_path, str):
            pdf_path = Path(pdf_path)
            
        # 检查 PDF 文件是否存在
        if not pdf_path.exists():
            print(f"❌ 错误: 找不到 PDF 文件 {pdf_path}")
            return
        
        # 读取 config.json 获取请求内容和验证target_url
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                # 验证target_url是否以https://www.cninfo.com.cn开头
                target_url = config_data.get("target_url", "")
                if not target_url.startswith('https://www.cninfo.com.cn'):
                    print("错误: 本项目能够处理的target_url是受限的，目前仅能处理针对https://www.cninfo.com.cn网站的请求")
                    return
                # 默认请求内容
                request_content = config_data.get("require", "请分析此文档并提取关键内容。")
        else:
            # 如果没有 config.json，则使用默认请求内容
            request_content = "请分析此文档并提取关键内容。"
        
        # 读取 PDF 文件
        pdf_data = pdf_path.read_bytes()
        
        # 创建 Gemini 模型实例
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        
        # 创建文件上传对象
        pdf_file = genai.upload_file(path=pdf_path, display_name="Analysis Document")
        
        # 等待文件处理完成
        print("正在上传和处理 PDF 文件...")
        import time
        while pdf_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            pdf_file = genai.get_file(pdf_file.name)
        
        if pdf_file.state.name == "FAILED":
            raise ValueError("PDF 文件处理失败")
        
        print("\n✅ PDF 文件上传完成")
        
        # 构建提示内容
        prompt = f"{request_content}\n\n请分析附件中的 PDF 文档并按以下格式返回结果：\n\n## 公告编号\n[文档内的公告编号] \n\n## 公告日期\n[文档最后的一行的日期]  \n\n## 文档摘要\n[文档的核心内容摘要]\n\n## 关键信息\n- [要点1]\n- [要点2]\n- [要点3]\n\n## 详细内容\n[文档的详细分析]"
        
        # 调用 Gemini 生成内容
        print(f"正在调用 {GEMINI_MODEL_NAME} 分析文档...")
        response = model.generate_content([prompt, pdf_file])
        
        # 格式化为 Markdown 并保存
        if response.text:
            # 生成输出文件路径
            output_filename = pdf_path.stem + ".md"
            output_path = Path("./data") / output_filename
            
            # 确保data目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入 Markdown 文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"✅ 分析完成，结果已保存到: {output_path}")
            print(f"\n{response.text}")
        else:
            print("❌ Gemini 返回空响应")
            
    except Exception as e:
        print(f"❌ 处理过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

def call_deepseek_analyze_pdf(pdf_path):
    """
    调用 DeepSeek 分析 PDF 文档
    """
    try:
        # 确保pdf_path是Path对象
        if isinstance(pdf_path, str):
            pdf_path = Path(pdf_path)
            
        # 检查 PDF 文件是否存在
        if not pdf_path.exists():
            print(f"❌ 错误: 找不到 PDF 文件 {pdf_path}")
            return
        
        # 读取 config.json 获取请求内容和验证target_url
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                # 验证target_url是否以https://www.cninfo.com.cn开头
                target_url = config_data.get("target_url", "")
                if not target_url.startswith('https://www.cninfo.com.cn'):
                    print("错误: 本项目能够处理的target_url是受限的，目前仅能处理针对https://www.cninfo.com.cn网站的请求")
                    return
                # 默认请求内容
                request_content = config_data.get("require", "请分析此文档并提取关键内容。")
        else:
            # 如果没有 config.json，则使用默认请求内容
            request_content = "请分析此文档并提取关键内容。"

        
        # 读取PDF文件内容
        print("正在读取PDF文件内容...")
        reader = PdfReader(pdf_path)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
        
        # 如果PDF内容为空，给出提示
        if not text_content.strip():
            print("⚠️ 注意: PDF文件中未提取到文本内容，可能是扫描版PDF")
            text_content = "[无法从PDF中提取文本内容，可能是扫描版PDF]"
        
        # 构建提示内容
        prompt = f"{request_content}\n\n文档内容如下:\n{text_content}\n\n请分析文档并按以下格式返回结果：\n\n## 公告编号\n[文档内的公告编号] \n\n## 公告日期\n[文档最后的一行的日期]  \n\n## 文档摘要\n[文档的核心内容摘要]\n\n## 关键信息\n- [要点1]\n- [要点2]\n- [要点3]\n\n## 详细内容\n[文档的详细分析]"
        
        # 配置DeepSeek API客户端
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
        )
        
        # 调用DeepSeek API
        print(f"正在调用 {DEEPSEEK_MODEL_NAME} 分析文档...")
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一位专业的文档分析助手，请仔细分析用户提供的文档内容并按要求格式回答。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        
        # 获取API响应结果
        result_text = response.choices[0].message.content
        
        # 生成输出文件路径
        output_filename = pdf_path.stem + ".md"
        output_path = Path("./data") / output_filename
        
        # 确保data目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入 Markdown 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result_text)
        
        print(f"✅ 分析完成，结果已保存到: {output_path}")
        print(f"\n{result_text}")
            
    except Exception as e:
        print(f"❌ 处理过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


def call_llm_analyze_pdf(pdf_path):
    """
    根据环境变量选择的LLM提供商调用相应的分析函数
    """
    llm_provider = get_llm_provider()
    
    if llm_provider == "gemini":
        if not GEMINI_API_KEY:
            print("❌ 未配置 GEMINI_API_KEY")
            return
        return call_gemini_analyze_pdf(pdf_path)
    elif llm_provider == "deepseek":
        if not DEEPSEEK_API_KEY:
            print("❌ 未配置 DEEPSEEK_API_KEY")
            return
        return call_deepseek_analyze_pdf(pdf_path)
    # ModelScope support has been removed
    else:
        print(f"❌ 不支持的 LLM 提供商: {llm_provider}")
        return

def call_gemini_analyze_pdf_test(pdf_path):
    print("正在上传和处理 PDF 文件...")
    print(f"'{pdf_path}' 处理完毕！")

def process_pdf_files(directory_path):
    """
    处理指定目录下的所有PDF文件，调用call_llm_analyze_pdf函数。

    参数:
    directory_path (str): 包含PDF文件的目录路径
    """
    # 将目录路径转换为Path对象
    dir_path = Path(directory_path)

    # 检查目录是否存在
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"错误: 目录 {directory_path} 不存在或不是目录")
        return

    # 获取目录下所有PDF文件（不区分大小写）
    pdf_files = list(dir_path.glob("*.pdf")) + list(dir_path.glob("*.PDF"))

    if not pdf_files:
        print(f"在目录 {directory_path} 中没有找到PDF文件")
        return

    # 遍历每个PDF文件并调用函数
    for pdf_file in pdf_files:
        try:
            # 调用函数处理PDF文件
            call_llm_analyze_pdf(pdf_file)
            print(f"已处理文件: {pdf_file}")
        except Exception as e:
            print(f"处理文件 {pdf_file} 时出错: {e}")

def main(pdf_file_path=None):
    """
    主函数，用于处理单个PDF文件
    
    参数:
    pdf_file_path (str): PDF文件路径
    """
    if pdf_file_path:
        # 处理指定的PDF文件
        pdf_path = Path(pdf_file_path)
        call_llm_analyze_pdf(pdf_path)
        # call_gemini_analyze_pdf_test(pdf_file_path)

    else:
        # 如果没有提供文件路径，则处理data目录下的所有PDF文件
        process_pdf_files("./data/")

if __name__ == "__main__":
        main()