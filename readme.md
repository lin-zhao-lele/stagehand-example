# 使用 uv
uv venv .venv
source .venv/bin/activate  # Linux/Mac
uv pip install stagehand python-dotenv google-generativeai

# 或使用 pip
pip install stagehand python-dotenv google-generativeai

# 完整安装playwright
python -m playwright install

# 指定安装特定浏览器
python -m playwright install chromium

# 启动Web应用程序

## 前置条件
确保已安装Node.js和npm

## 安装依赖
```bash
npm install
```

## 启动服务器
```bash
node server.js
```

服务器将运行在 http://localhost:3000

## 使用说明
1. 打开浏览器访问 http://localhost:3000
2. 在"创建配置文件"区域输入目标URL和公司名称
3. 点击"创建配置文件"按钮
4. 点击"运行所有任务"按钮开始执行任务

## 功能说明
- 配置文件创建：支持同时创建多个配置文件，文件名格式为config_1.json, config_2.json等
- 任务执行流程：
  1. 运行预处理阶段处理每个配置文件
  2. 运行从服务器获取pdf文件下载PDF文件
  3. 将下载的PDF文件从downloads目录移动到data目录
  4. 运行大语言模型分析分析data目录中的每个PDF文件
- 实时状态显示：显示各个agent的运行状态
- 日志显示：在Console区域显示任务执行日志

## 大语言模型(LLM)支持
本项目支持多种大语言模型：
- Gemini (默认)
- DeepSeek

### 如何切换不同的LLM

1. **使用Gemini (默认)**
   - 在 .env 文件中设置: `LLM_PROVIDER=gemini`
   - 确保已配置Gemini API密钥: `GEMINI_API_KEY=your_api_key_here`
   - 可选配置模型名称: `GEMINI_MODEL_NAME=gemini-2.0-flash` (默认值)

2. **使用DeepSeek**
   - 在 .env 文件中设置: `LLM_PROVIDER=deepseek`
   - 配置DeepSeek API密钥: `DEEPSEEK_API_KEY=your_api_key_here`
   - 可选配置模型名称: `DEEPSEEK_MODEL_NAME=deepseek-chat` (默认值)

### .env配置示例

```env
# Gemini配置 (默认)
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyDDkyznSm4lWHUpJ1MoteHysANqG797KuQ
GEMINI_MODEL_NAME=gemini-2.0-flash

# DeepSeek配置 (可选)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_MODEL_NAME=deepseek-chat
```

### 切换步骤
1. 打开项目根目录下的 `.env` 文件
2. 修改 `LLM_PROVIDER` 的值为想要使用的LLM提供商
3. 确保相应提供商的API密钥已正确配置
4. 保存文件并重启应用程序
5. 运行任务时将自动使用配置的LLM提供商

## 版本说明
 version 0.1.X 不带web UI
 version 0.2.X 带js webUI 初始版本 有问题 能run 


## 测试
https://www.cninfo.com.cn/new/disclosure/stock?orgId=gssz0002031&stockCode=002031#latestAnnouncement
巨轮智能
