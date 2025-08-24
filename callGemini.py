import os
import json
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

if __name__ == "__main__":
    call_gemini_analyze_pdf(Path("./data/1224461857.PDF"))