import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# 加载 .env 中的 GEMINI_API_KEY
load_dotenv()

# 配置 API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini_analyze_pdf_test(pdf_path):
    print("正在上传和处理 PDF 文件...")
    print(f"'{pdf_path}' 处理完毕！")

def call_gemini_analyze_pdf(pdf_path):
    """
    调用 Gemini-2.0-flash 分析 PDF 文档
    """
    try:
        # 确保pdf_path是Path对象
        if isinstance(pdf_path, str):
            pdf_path = Path(pdf_path)
            
        # 检查 PDF 文件是否存在
        if not pdf_path.exists():
            print(f"❌ 错误: 找不到 PDF 文件 {pdf_path}")
            return
        
        # 读取 config.json 获取请求内容
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                # 默认请求内容
                request_content = config_data.get("require", "请分析此文档并提取关键内容。")
        else:
            # 如果没有 config.json，则使用默认请求内容
            request_content = "请分析此文档并提取关键内容。"
        
        # 读取 PDF 文件
        pdf_data = pdf_path.read_bytes()
        
        # 创建 Gemini 模型实例
        model = genai.GenerativeModel('gemini-2.0-flash')
        
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
        prompt = f"{request_content}\n\n请分析附件中的 PDF 文档并按以下格式返回结果：\n\n## 文档摘要\n[文档的核心内容摘要]\n\n## 关键信息\n- [要点1]\n- [要点2]\n- [要点3]\n\n## 详细内容\n[文档的详细分析]"
        
        # 调用 Gemini 生成内容
        print("正在调用 Gemini-2.0-flash 分析文档...")
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

def process_pdf_files(directory_path):
    """
    处理指定目录下的所有PDF文件，调用call_gemini_analyze_pdf函数。

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
            call_gemini_analyze_pdf(pdf_file)
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
        # pdf_path = Path(pdf_file_path)
        # call_gemini_analyze_pdf(pdf_path)
        call_gemini_analyze_pdf_test(pdf_file_path)

    else:
        # 如果没有提供文件路径，则处理data目录下的所有PDF文件
        process_pdf_files("./data/")

if __name__ == "__main__":
    # 获取命令行参数
    if len(sys.argv) > 1:
        # 使用第一个参数作为PDF文件路径
        main(sys.argv[1])
    else:
        # 如果没有参数，则处理data目录下的所有PDF文件
        main()