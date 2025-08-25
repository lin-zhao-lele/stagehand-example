# 上市公司公告分析助手

本项目是一个Web应用程序，用于自动化分析上市公司公告PDF文件。它支持多种大语言模型（LLM）进行文档分析，并提供友好的Web界面进行配置和任务管理。

## 项目功能

- 自动从指定网站下载上市公司公告PDF文件
- 使用大语言模型（Gemini或DeepSeek）分析PDF内容
- 提供Web界面进行任务配置和状态监控
- 支持打包下载分析结果
- 支持清理已处理的文件

## 系统要求

- Node.js (v14或更高版本)
- Python (v3.8或更高版本)
- uv (Python包管理器，推荐使用)

## 使用uv进行包管理

本项目推荐使用[uv](https://github.com/astral-sh/uv)进行Python包管理，它比pip更快更高效。

### 安装uv

在Linux/macOS上：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

在Windows上（PowerShell）：
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

更多安装选项请参考：https://docs.astral.sh/uv/getting-started/installation/

## 安装和设置

### 1. 克隆项目

```bash
git clone git@github.com:lin-zhao-lele/stagehand-example.git
cd Stagehand
```

### 2. 设置Python环境

使用uv创建虚拟环境并安装依赖：

```bash
# 创建虚拟环境
uv venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 安装Python依赖
uv pip install stagehand python-dotenv google-generativeai PyPDF2 openai

# 安装Playwright浏览器依赖
python -m playwright install
```

### 3. 设置Node.js环境

```bash
# 安装Node.js依赖
npm install
```

### 4. 配置环境变量

在项目根目录下创建或编辑`.env`文件：

```env
# 选择LLM提供商 (gemini 或 deepseek)
LLM_PROVIDER=gemini

# Gemini配置
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-1.5-flash

# DeepSeek配置 (如果使用DeepSeek)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL_NAME=deepseek-chat
```

## 启动应用程序

### 1. 启动Web服务器

```bash
npm start
```

服务器将运行在 http://localhost:1501

### 2. 访问Web界面

打开浏览器访问 http://localhost:1501

## 使用说明

1. 访问Web界面后，需要先登录才能使用系统功能

2. 在"创建配置文件"区域输入目标URL和日期范围
   - 注意：本项目仅支持处理针对 https://www.cninfo.com.cn 网站的请求，输入其他网站URL将无法创建配置文件
3. 在"用户Prompt"区域输入分析要求（可选）
4. 选择底层LLM提供商（Gemini或DeepSeek）
5. 点击"创建配置文件"按钮
6. 点击"运行所有任务"按钮开始执行任务
7. 任务完成后，可以使用"打包下载分析结果"下载分析结果

## 安全功能

### 登录保护
- 系统要求用户登录后才能访问主要功能


### 登录失败限制
- 系统会跟踪登录失败次数
- 连续5次登录失败后，账户将被锁定30分钟
- 锁定期间无法再次尝试登录，提高安全性

## 大语言模型(LLM)支持

### Gemini (默认)
- 在 `.env` 文件中设置: `LLM_PROVIDER=gemini`
- 配置Gemini API密钥: `GEMINI_API_KEY=your_api_key_here`
- 可选配置模型名称: `GEMINI_MODEL_NAME=gemini-1.5-flash`

### DeepSeek
- 在 `.env` 文件中设置: `LLM_PROVIDER=deepseek`
- 配置DeepSeek API密钥: `DEEPSEEK_API_KEY=your_api_key_here`
- 可选配置模型名称: `DEEPSEEK_MODEL_NAME=deepseek-chat`

## URL验证机制

本项目具有URL验证机制，仅支持处理针对 https://www.cninfo.com.cn 网站的请求：

1. 在创建配置文件时，系统会验证所有输入的URL是否以 https://www.cninfo.com.cn 开头
2. 如果输入的URL不符合要求，系统将拒绝创建配置文件并提示错误信息
3. 在执行任务阶段，系统会再次验证配置文件中的target_url是否符合要求
4. 如果发现配置文件中的target_url不是以 https://www.cninfo.com.cn 开头，程序将停止执行并报错

此机制确保了系统的安全性和专一性，防止处理非目标网站的请求。

## 文件操作功能

- **打包下载分析结果**：将data目录下的.md文件（和可选的.pdf文件）打包成ZIP文件下载
- **删除已分析文件**：清理data目录下已处理的文件以节省存储空间

## 项目结构

```
Stagehand/
├── .env                  # 环境变量配置文件
├── server.js             # Node.js服务器主文件
├── package.json          # Node.js依赖配置
├── callLLM.py            # LLM调用脚本
├── inputJson.py          # 预处理脚本
├── getPdfFiles.py        # PDF文件下载脚本
├── getHerfWithoutAI.py   # URL获取脚本
├── public/               # Web前端文件
├── data/                 # 分析结果存储目录
├── downloads/            # 下载文件临时存储目录
└── README.md             # 项目说明文档
```

## 故障排除

### 常见问题

1. **端口被占用**：如果1501端口被占用，可以修改server.js中的PORT变量
2. **API密钥错误**：确保.env文件中的API密钥正确配置
3. **依赖安装失败**：尝试使用`npm install --force`或`uv pip install --force-reinstall`
4. **忘记登录密码**：可以在.env文件中修改USERNAME和PASSWORD值，然后重启服务器

### 查看日志

应用程序日志会在Web界面的"执行日志"区域显示，也可以在终端中查看服务器输出。

## 版本信息

- version 0.1.X 不带web UI
- version 0.2.X 带js webUI 初始版本

## 许可证

[待添加许可证信息]