const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const session = require('express-session');
require('dotenv').config();

// 存储登录尝试记录的对象（在生产环境中应使用数据库或Redis）
const loginAttempts = {};
const MAX_ATTEMPTS = 5;
const LOCKOUT_DURATION = 30 * 60 * 1000; // 30分钟

const app = express();
const PORT = 1501;

// 中间件
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Session配置
app.use(session({
  secret: 'stagehand-secret-key',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false } // 在生产环境中，如果使用HTTPS，应设置为true
}));

// 登录认证中间件
const requireAuth = (req, res, next) => {
  // 如果是登录页面、登录API、登出API或静态文件，不需要认证
  if (req.path === '/login.html' || req.path === '/api/login' || req.path === '/api/logout' || req.path === '/api/auth-status') {
    return next();
  }
  
  // 对于静态文件（CSS, JS, 图片等），不需要认证
  if (req.path.endsWith('.css') || req.path.endsWith('.js') || req.path.endsWith('.png') || req.path.endsWith('.jpg') || req.path.endsWith('.jpeg') || req.path.endsWith('.gif') || req.path.endsWith('.ico')) {
    return next();
  }
  
  // 检查用户是否已登录
  if (req.session && req.session.authenticated) {
    return next();
  } else {
    // 未登录，返回401状态码
    return res.status(401).json({ error: '未授权访问，请先登录' });
  }
};

// 应用认证中间件到所有路由
app.use(requireAuth);

// 确保必要的目录存在
const ensureDirectories = () => {
  const dirs = ['data', 'downloads'];
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir);
    }
  });
};

// 登录API
app.post('/api/login', (req, res) => {
  try {
    const { username, password } = req.body;
    const clientIP = req.ip || req.connection.remoteAddress;
    const attemptKey = `${username}-${clientIP}`;
    
    // 检查是否被锁定
    if (loginAttempts[attemptKey] && loginAttempts[attemptKey].lockedUntil) {
      const lockoutTime = new Date(loginAttempts[attemptKey].lockedUntil);
      const now = new Date();
      
      if (now < lockoutTime) {
        const minutesLeft = Math.ceil((lockoutTime - now) / (60 * 1000));
        return res.status(429).json({ 
          success: false, 
          error: `账户已被锁定，请在${minutesLeft}分钟后重试` 
        });
      } else {
        // 锁定期已过，重置尝试次数
        loginAttempts[attemptKey] = { attempts: 0, lockedUntil: null };
      }
    }
    
    // 从.env文件读取用户名和密码
    const envUsername = process.env.USERNAME || 'lan';
    const envPassword = process.env.PASSWORD; // 不使用默认值，如果环境变量未设置则为undefined
    
    // 验证用户名和密码
    if (username === envUsername && password === envPassword) {
      // 登录成功，重置尝试次数并设置session
      loginAttempts[attemptKey] = { attempts: 0, lockedUntil: null };
      req.session.authenticated = true;
      req.session.username = username;
      
      res.json({ 
        success: true, 
        message: '登录成功',
        username: username
      });
    } else {
      // 登录失败，增加尝试次数
      if (!loginAttempts[attemptKey]) {
        loginAttempts[attemptKey] = { attempts: 0, lockedUntil: null };
      }
      
      loginAttempts[attemptKey].attempts += 1;
      
      // 检查是否达到最大尝试次数
      if (loginAttempts[attemptKey].attempts >= MAX_ATTEMPTS) {
        // 锁定账户30分钟
        const lockoutTime = new Date(Date.now() + LOCKOUT_DURATION);
        loginAttempts[attemptKey].lockedUntil = lockoutTime;
        
        return res.status(429).json({ 
          success: false, 
          error: '登录失败次数过多，账户已被锁定30分钟' 
        });
      } else {
        // 返回剩余尝试次数
        const remainingAttempts = MAX_ATTEMPTS - loginAttempts[attemptKey].attempts;
        res.status(401).json({ 
          success: false, 
          error: `用户名或密码错误，您还有${remainingAttempts}次尝试机会` 
        });
      }
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 登出API
app.post('/api/logout', (req, res) => {
  try {
    // 销毁session
    req.session.destroy((err) => {
      if (err) {
        return res.status(500).json({ error: '登出失败' });
      }
      
      res.json({ 
        success: true, 
        message: '登出成功' 
      });
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 检查登录状态API
app.get('/api/auth-status', (req, res) => {
  if (req.session && req.session.authenticated) {
    res.json({ 
      authenticated: true, 
      username: req.session.username 
    });
  } else {
    res.json({ authenticated: false });
  }
});

// 创建配置文件
app.post('/api/config', (req, res) => {
  try {
    const { targetUrl, startDate, endDate, require } = req.body;
    
    if (!targetUrl || !startDate || !endDate) {
      return res.status(400).json({ error: 'Missing required fields: targetUrl, startDate, or endDate' });
    }
    
    // 如果config.json文件已存在，先删除它
    const configFileName = 'config.json';
    if (fs.existsSync(configFileName)) {
      fs.unlinkSync(configFileName);
    }
    
    // 创建新的配置数据（不包含companyName字段）
    const configData = {
      target_url: targetUrl.trim(),
      startDate: startDate,
      endDate: endDate,
      require: require || "请分析此文档，提取关键内容并进行总结。",
      titles: []
    };
    
    // 写入新的config.json文件
    fs.writeFileSync(configFileName, JSON.stringify(configData, null, 2));
    
    res.json({ 
      success: true, 
      message: '成功创建配置文件',
      file: configFileName
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 获取所有配置文件
app.get('/api/configs', (req, res) => {
  try {
    const configFiles = fs.readdirSync('.')
      .filter(file => file.startsWith('config_') && file.endsWith('.json'));
    
    const configs = configFiles.map(file => {
      const content = fs.readFileSync(file, 'utf8');
      return { filename: file, ...JSON.parse(content) };
    });
    
    res.json(configs);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 获取当前配置文件内容
app.get('/api/config-content', (req, res) => {
  try {
    const configFile = 'config.json';
    if (!fs.existsSync(configFile)) {
      return res.status(404).json({ error: 'Configuration file not found' });
    }
    
    const content = fs.readFileSync(configFile, 'utf8');
    const configData = JSON.parse(content);
    res.json(configData);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 获取当前.env文件中的LLM_PROVIDER值
app.get('/api/current-llm', (req, res) => {
  try {
    // 检查.env文件是否存在
    const envFile = '.env';
    if (!fs.existsSync(envFile)) {
      return res.status(404).json({ error: '.env file not found' });
    }
    
    // 读取.env文件内容
    const envContent = fs.readFileSync(envFile, 'utf8');
    
    // 查找LLM_PROVIDER行
    const llmProviderMatch = envContent.match(/LLM_PROVIDER=(.*)/);
    const llmProvider = llmProviderMatch ? llmProviderMatch[1].trim() : 'gemini';
    
    res.json({ success: true, llmProvider });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 更新.env文件中的LLM_PROVIDER值
app.post('/api/update-env', (req, res) => {
  try {
    const { llmProvider } = req.body;
    
    // 检查.env文件是否存在
    const envFile = '.env';
    if (!fs.existsSync(envFile)) {
      return res.status(404).json({ error: '.env file not found' });
    }
    
    // 读取.env文件内容
    let envContent = fs.readFileSync(envFile, 'utf8');
    
    // 更新LLM_PROVIDER行，如果不存在则添加
    const llmProviderLine = `LLM_PROVIDER=${llmProvider}`;
    if (envContent.includes('LLM_PROVIDER=')) {
      // 替换现有的LLM_PROVIDER行
      envContent = envContent.replace(/LLM_PROVIDER=.*/, llmProviderLine);
    } else {
      // 添加新的LLM_PROVIDER行
      envContent += `\n${llmProviderLine}`;
    }
    
    // 写入更新后的内容到.env文件
    fs.writeFileSync(envFile, envContent);
    
    res.json({ success: true, message: 'LLM provider updated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 更新配置文件
app.post('/api/update-config', (req, res) => {
  try {
    const { require } = req.body;
    
    // 检查config.json文件是否存在
    const configFile = 'config.json';
    if (!fs.existsSync(configFile)) {
      return res.status(404).json({ error: 'Configuration file not found' });
    }
    
    // 读取现有的配置文件
    const configData = JSON.parse(fs.readFileSync(configFile, 'utf8'));
    
    // 更新require字段
    configData.require = require;
    
    // 写入更新后的配置文件
    fs.writeFileSync(configFile, JSON.stringify(configData, null, 2));
    
    res.json({ success: true, message: 'Configuration updated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 清空目录的辅助函数
const clearDirectory = (dirPath) => {
  try {
    if (fs.existsSync(dirPath)) {
      const files = fs.readdirSync(dirPath);
      for (const file of files) {
        const filePath = path.join(dirPath, file);
        fs.unlinkSync(filePath);
      }
      console.log(`已清空目录: ${dirPath}`);
    }
  } catch (error) {
    console.error(`清空目录 ${dirPath} 失败:`, error);
    throw error;
  }
};

// 运行所有任务
app.post('/api/run-tasks', async (req, res) => {
  // 设置SSE响应头
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*'
  });
  
  // 存储响应对象用于发送实时日志
  currentResponse = res;
  
  try {
    // 发送开始消息
    res.write(`data: ${JSON.stringify({ type: 'start', message: '开始执行所有任务...' })}\n\n`);
    
    // 清空downloads和data目录
    res.write(`data: ${JSON.stringify({ type: 'info', message: '清空downloads目录...' })}\n\n`);
    clearDirectory('./downloads');
    res.write(`data: ${JSON.stringify({ type: 'info', message: '清空data目录...' })}\n\n`);
    clearDirectory('./data');
    
    // 检查config.json文件是否存在
    const configFile = 'config.json';
    if (!fs.existsSync(configFile)) {
      res.write(`data: ${JSON.stringify({ type: 'error', message: '没有找到配置文件 config.json' })}\n\n`);
      res.end();
      return;
    }
    
    res.write(`data: ${JSON.stringify({ type: 'info', message: `处理配置文件: ${configFile}` })}\n\n`);
    
    // 1. 运行 inputJson.py (预处理阶段)
    res.write(`data: ${JSON.stringify({ type: 'info', message: '执行 预处理阶段 任务...' })}\n\n`);
    await runPythonScript('inputJson.py', [configFile]);
    res.write(`data: ${JSON.stringify({ type: 'info', message: '预处理阶段 任务完成' })}\n\n`);
    
    // 2. 运行 getPdfFiles.py (从服务器获取pdf文件)
    res.write(`data: ${JSON.stringify({ type: 'info', message: '执行 从服务器获取pdf文件 任务...' })}\n\n`);
    await runPythonScript('getPdfFiles.py', [configFile]);
    res.write(`data: ${JSON.stringify({ type: 'info', message: '从服务器获取pdf文件 任务完成' })}\n\n`);
    
    // 3. 移动PDF文件从downloads到data目录
    res.write(`data: ${JSON.stringify({ type: 'info', message: '移动PDF文件从downloads到data目录...' })}\n\n`);
    movePdfFiles();
    res.write(`data: ${JSON.stringify({ type: 'info', message: 'PDF文件移动完成' })}\n\n`);
    
    // 4. 处理data目录下的PDF文件 (大语言模型分析)
    res.write(`data: ${JSON.stringify({ type: 'info', message: '处理data目录下的PDF文件 (大语言模型分析)...' })}\n\n`);
    const pdfFiles = fs.readdirSync('./data')
      .filter(file => file.endsWith('.pdf') || file.endsWith('.PDF'));
    
    res.write(`data: ${JSON.stringify({ type: 'info', message: `找到 ${pdfFiles.length} 个PDF文件` })}\n\n`);
    
    for (const pdfFile of pdfFiles) {
      const fullPath = path.join('./data', pdfFile);
      res.write(`data: ${JSON.stringify({ type: 'info', message: `处理PDF文件: ${pdfFile}` })}\n\n`);
      await runPythonScript('callLLM.py', [fullPath]);
      res.write(`data: ${JSON.stringify({ type: 'info', message: `PDF文件处理完成: ${pdfFile}` })}\n\n`);
    }
    
    res.write(`data: ${JSON.stringify({ type: 'end', message: '所有任务执行完成' })}\n\n`);
    res.end();
  } catch (error) {
    console.error('任务执行失败:', error);
    if (currentResponse) {
      currentResponse.write(`data: ${JSON.stringify({ type: 'error', message: `任务执行失败: ${error.message}` })}\n\n`);
      currentResponse.end();
    }
  } finally {
    // 清除当前响应对象
    currentResponse = null;
  }
});

// 存储客户端响应对象以发送实时日志
let currentResponse = null;

// 运行Python脚本的辅助函数
const runPythonScript = (scriptName, args = []) => {
  return new Promise((resolve, reject) => {
    console.log(`启动Python脚本: ${scriptName} ${args.join(' ')}`);
    
    const child = spawn('python', [scriptName, ...args]);
    
    child.stdout.on('data', (data) => {
      const output = data.toString().trim();
      console.log(`[stdout] ${output}`);
      // 发送实时日志到前端
      if (currentResponse) {
        currentResponse.write(`data: ${JSON.stringify({ type: 'stdout', message: output })}\n\n`);
      }
    });
    
    child.stderr.on('data', (data) => {
      const error = data.toString().trim();
      console.error(`[stderr] ${error}`);
      // 发送错误日志到前端
      if (currentResponse) {
        currentResponse.write(`data: ${JSON.stringify({ type: 'stderr', message: error })}\n\n`);
      }
    });
    
    child.on('close', (code) => {
      console.log(`${scriptName} 执行完成，退出码: ${code}`);
      if (currentResponse) {
        currentResponse.write(`data: ${JSON.stringify({ type: 'close', code: code, script: scriptName })}\n\n`);
      }
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`${scriptName} 执行失败，退出码: ${code}`));
      }
    });
    
    child.on('error', (error) => {
      console.error(`${scriptName} 启动失败:`, error);
      if (currentResponse) {
        currentResponse.write(`data: ${JSON.stringify({ type: 'error', message: `${scriptName} 启动失败: ${error.message}` })}\n\n`);
      }
      reject(new Error(`${scriptName} 启动失败: ${error.message}`));
    });
  });
};

// 移动PDF文件的辅助函数
const movePdfFiles = () => {
  try {
    // 确保目录存在
    if (!fs.existsSync('./downloads')) {
      console.log('downloads目录不存在');
      return;
    }
    
    if (!fs.existsSync('./data')) {
      fs.mkdirSync('./data');
    }
    
    const files = fs.readdirSync('./downloads');
    const pdfFiles = files.filter(file => 
      file.endsWith('.pdf') || file.endsWith('.PDF')
    );
    
    console.log(`在downloads目录中找到 ${pdfFiles.length} 个PDF文件`);
    
    let movedCount = 0;
    pdfFiles.forEach(file => {
      try {
        const sourcePath = path.join('./downloads', file);
        const destPath = path.join('./data', file);
        
        // 检查目标文件是否已存在
        if (fs.existsSync(destPath)) {
          console.log(`文件已存在，跳过: ${file}`);
          return;
        }
        
        fs.renameSync(sourcePath, destPath);
        console.log(`移动文件: ${file}`);
        movedCount++;
      } catch (moveError) {
        console.error(`移动文件 ${file} 失败:`, moveError.message);
      }
    });
    
    console.log(`成功移动 ${movedCount} 个PDF文件到data目录`);
  } catch (error) {
    console.error('移动PDF文件时出错:', error);
    throw error;
  }
};

// 打包并下载data目录下的文件
app.post('/api/download-files', (req, res) => {
  try {
    const { includePdf } = req.body; // 是否包含PDF文件
    
    // 检查data目录是否存在
    const dataDir = './data';
    if (!fs.existsSync(dataDir)) {
      return res.status(404).json({ error: 'Data directory not found' });
    }
    
    // 获取data目录下的所有文件
    const files = fs.readdirSync(dataDir);
    
    // 根据参数过滤文件
    let filteredFiles = files.filter(file => file.endsWith('.md')); // 默认只包含md文件
    if (includePdf) {
      // 如果includePdf为true，则也包含PDF文件
      filteredFiles = files.filter(file => file.endsWith('.md') || file.endsWith('.pdf') || file.endsWith('.PDF'));
    }
    
    if (filteredFiles.length === 0) {
      return res.status(404).json({ error: 'No files found to download' });
    }
    
    // 创建临时zip文件
    const zip = new (require('adm-zip'))();
    
    // 添加文件到zip
    filteredFiles.forEach(file => {
      const filePath = path.join(dataDir, file);
      if (fs.existsSync(filePath)) {
        zip.addLocalFile(filePath);
      }
    });
    
    // 生成zip文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const zipFileName = `analysis_results_${timestamp}.zip`;
    
    // 设置响应头
    res.writeHead(200, {
      'Content-Type': 'application/zip',
      'Content-Disposition': `attachment; filename="${zipFileName}"`
    });
    
    // 发送zip文件内容
    const zipBuffer = zip.toBuffer();
    res.end(zipBuffer);
    
  } catch (error) {
    console.error('打包下载文件时出错:', error);
    // 检查响应头是否已经发送
    if (!res.headersSent) {
      res.status(500).json({ error: error.message });
    }
  }
});

// 下载PDF文件
app.post('/api/download-pdf-files', async (req, res) => {
  // 设置SSE响应头
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*'
  });

  try {
    // 发送开始消息
    res.write(`data: ${JSON.stringify({ type: 'start', message: '开始下载PDF文件...' })}\n\n`);
    
    // 检查config.json文件是否存在
    const configFile = 'config.json';
    if (!fs.existsSync(configFile)) {
      res.write(`data: ${JSON.stringify({ type: 'error', message: '没有找到配置文件 config.json' })}\n\n`);
      res.end();
      return;
    }
    
    res.write(`data: ${JSON.stringify({ type: 'info', message: '执行预处理任务...' })}\n\n`);
    
    // 先运行 inputJson.py 脚本
    await runPythonScript('inputJson.py', [configFile]);
    
    res.write(`data: ${JSON.stringify({ type: 'info', message: '预处理任务完成，开始下载PDF文件...' })}\n\n`);
    
    // 再运行 getPdfFiles.py 脚本
    await runPythonScript('getPdfFiles.py', [configFile]);
    
    res.write(`data: ${JSON.stringify({ type: 'end', message: 'PDF文件下载完成' })}\n\n`);
    res.end();
  } catch (error) {
    console.error('下载PDF文件失败:', error);
    if (res && !res.headersSent) {
      res.write(`data: ${JSON.stringify({ type: 'error', message: `下载PDF文件失败: ${error.message}` })}\n\n`);
      res.end();
    }
  }
});

// 打包并下载PDF文件
app.post('/api/download-pdf-zip', (req, res) => {
  try {
    // 检查downloads目录是否存在
    const downloadsDir = './downloads';
    if (!fs.existsSync(downloadsDir)) {
      return res.status(404).json({ error: 'Downloads directory not found' });
    }
    
    // 获取downloads目录下的所有PDF文件
    const files = fs.readdirSync(downloadsDir);
    const pdfFiles = files.filter(file => file.endsWith('.pdf') || file.endsWith('.PDF'));
    
    if (pdfFiles.length === 0) {
      return res.status(404).json({ error: 'No PDF files found to download' });
    }
    
    // 创建临时zip文件
    const zip = new (require('adm-zip'))();
    
    // 添加PDF文件到zip
    pdfFiles.forEach(file => {
      const filePath = path.join(downloadsDir, file);
      if (fs.existsSync(filePath)) {
        zip.addLocalFile(filePath);
      }
    });
    
    // 生成zip文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const zipFileName = `pdf_files_${timestamp}.zip`;
    
    // 设置响应头
    res.writeHead(200, {
      'Content-Type': 'application/zip',
      'Content-Disposition': `attachment; filename="${zipFileName}"`
    });
    
    // 发送zip文件内容
    const zipBuffer = zip.toBuffer();
    res.end(zipBuffer);
    
  } catch (error) {
    console.error('打包下载PDF文件时出错:', error);
    // 检查响应头是否已经发送
    if (!res.headersSent) {
      res.status(500).json({ error: error.message });
    }
  }
});

// 删除data目录下的文件
app.post('/api/clear-data-files', (req, res) => {
  try {
    const { includePdf } = req.body; // 是否包含PDF文件
    
    // 检查data目录是否存在
    const dataDir = './data';
    if (!fs.existsSync(dataDir)) {
      return res.status(404).json({ error: 'Data directory not found' });
    }
    
    // 获取data目录下的所有文件
    const files = fs.readdirSync(dataDir);
    
    // 根据参数过滤文件
    let filesToDelete = files.filter(file => file.endsWith('.md')); // 默认只删除md文件
    if (includePdf) {
      // 如果includePdf为true，则也删除PDF文件
      filesToDelete = files.filter(file => file.endsWith('.md') || file.endsWith('.pdf') || file.endsWith('.PDF'));
    }
    
    // 删除文件
    let deletedCount = 0;
    filesToDelete.forEach(file => {
      const filePath = path.join(dataDir, file);
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        deletedCount++;
      }
    });
    
    res.json({ 
      success: true, 
      message: `成功删除 ${deletedCount} 个文件`,
      deletedCount: deletedCount
    });
  } catch (error) {
    console.error('删除文件时出错:', error);
    res.status(500).json({ error: error.message });
  }
});

// 启动服务器
ensureDirectories();
app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
});