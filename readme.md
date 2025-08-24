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

## 版本说明
 version 0.1.X 不带web UI
 version 0.2.X 带js webUI 初始版本 有问题 能run 


## 测试
https://www.cninfo.com.cn/new/disclosure/stock?orgId=gssz0002031&stockCode=002031#latestAnnouncement
巨轮智能
