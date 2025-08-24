# 代码文件功能和接口说明

## 1. 预处理阶段

### 功能说明
该脚本主要用于从指定URL页面中提取包含特定公司名称的标题信息，并将这些标题保存到配置文件中。它使用Stagehand库来控制浏览器进行页面操作。

### 主要功能
- 加载环境变量中的GEMINI_API_KEY
- 使用Stagehand创建浏览器实例并访问指定URL
- 提取页面中包含特定公司名称的文本内容
- 对提取的标题进行去重处理
- 将过滤后的标题列表保存到config.json配置文件中

### 接口说明
- `main(configJson)`: 主函数，接收配置文件路径作为参数
  - 参数: `configJson` (str) - 配置文件路径
  - 返回值: 无
- 依赖配置文件字段:
  - `target_url`: 目标网站URL
  - `companyName`: 公司名称，用于过滤标题

## 2. 大语言模型分析

### 功能说明
该脚本用于调用Gemini-2.0-flash模型分析PDF文档内容，并将分析结果保存为Markdown格式文件。

### 主要功能
- 读取配置文件获取分析请求内容
- 上传PDF文件到Gemini服务
- 调用Gemini模型分析PDF内容
- 将分析结果格式化为Markdown并保存

### 接口说明
- `call_gemini_analyze_pdf(pdf_path)`: 分析PDF文档的主要函数
  - 参数: `pdf_path` (Path) - PDF文件路径
  - 返回值: 无
- `call_gemini_analyze_pdf_test(pdf_path)`: 测试函数，仅打印处理信息
  - 参数: `pdf_path` (Path) - PDF文件路径
  - 返回值: 无
- 依赖配置文件字段:
  - `require`: 分析请求内容（可选）

## 3. 从服务器获取pdf文件

### 功能说明
该脚本用于根据配置文件中的标题列表，从网站下载对应的PDF文件。它使用Stagehand库控制浏览器进行文件下载操作。

### 主要功能
- 加载配置文件中的标题列表
- 遍历标题列表，依次下载对应的PDF文件
- 使用Stagehand控制浏览器点击下载链接
- 处理下载过程中的异常情况

### 接口说明
- `main(configJson)`: 主函数，控制整个PDF下载流程
  - 参数: `configJson` (str) - 配置文件路径
  - 返回值: 无
- `save_pdf(stagehand, title)`: 下载单个PDF文件的函数
  - 参数: 
    - `stagehand` (Stagehand) - Stagehand实例
    - `title` (str) - PDF文件标题
  - 返回值: 无
- 依赖配置文件字段:
  - `target_url`: 目标网站URL
  - `titles`: 需要下载的PDF文件标题列表