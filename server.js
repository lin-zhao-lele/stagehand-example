const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// 中间件
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// 确保必要的目录存在
const ensureDirectories = () => {
  const dirs = ['data', 'downloads'];
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir);
    }
  });
};

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

// 启动服务器
ensureDirectories();
app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
});