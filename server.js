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
    const { targetUrls, companyName, startDate, endDate } = req.body;
    
    if (!targetUrls || !companyName || !startDate || !endDate) {
      return res.status(400).json({ error: 'Missing required fields: targetUrls, companyName, startDate, or endDate' });
    }
    
    const urls = targetUrls.split('\n').filter(url => url.trim());
    const createdFiles = [];
    
    urls.forEach((url, index) => {
      const trimmedUrl = url.trim();
      if (trimmedUrl) {
        const configData = {
          target_url: trimmedUrl,
          companyName: companyName.trim(),
          startDate: startDate,
          endDate: endDate,
          titles: []
        };
        
        const filename = `config_${index + 1}.json`;
        fs.writeFileSync(filename, JSON.stringify(configData, null, 2));
        createdFiles.push(filename);
      }
    });
    
    res.json({ 
      success: true, 
      message: `成功创建 ${createdFiles.length} 个配置文件`,
      files: createdFiles
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

// 运行所有任务
app.post('/api/run-tasks', async (req, res) => {
  try {
    // 获取所有配置文件
    const configFiles = fs.readdirSync('.')
      .filter(file => file.startsWith('config_') && file.endsWith('.json'));
    
    if (configFiles.length === 0) {
      return res.status(400).json({ error: '没有找到配置文件' });
    }
    
    console.log('开始执行所有任务...');
    
    // 为每个配置文件执行任务
    for (const configFile of configFiles) {
      console.log(`处理配置文件: ${configFile}`);
      
      // 1. 运行 inputJson.py
      console.log('执行 inputJson.py 任务...');
      await runPythonScript('inputJson.py', [configFile]);
      console.log('inputJson.py 任务完成');
      
      // 2. 运行 getPdfFiles.py
      console.log('执行 getPdfFiles.py 任务...');
      await runPythonScript('getPdfFiles.py', [configFile]);
      console.log('getPdfFiles.py 任务完成');
    }
    
    // 3. 移动PDF文件从downloads到data目录
    console.log('移动PDF文件从downloads到data目录...');
    movePdfFiles();
    console.log('PDF文件移动完成');
    
    // 4. 处理data目录下的PDF文件
    console.log('处理data目录下的PDF文件...');
    const pdfFiles = fs.readdirSync('./data')
      .filter(file => file.endsWith('.pdf') || file.endsWith('.PDF'));
    
    console.log(`找到 ${pdfFiles.length} 个PDF文件`);
    
    for (const pdfFile of pdfFiles) {
      const fullPath = path.join('./data', pdfFile);
      console.log(`处理PDF文件: ${pdfFile}`);
      await runPythonScript('callGemini.py', [fullPath]);
      console.log(`PDF文件处理完成: ${pdfFile}`);
    }
    
    console.log('所有任务执行完成');
    res.json({ success: true, message: '所有任务执行完成' });
  } catch (error) {
    console.error('任务执行失败:', error);
    res.status(500).json({ error: error.message });
  }
});

// 运行Python脚本的辅助函数
const runPythonScript = (scriptName, args = []) => {
  return new Promise((resolve, reject) => {
    console.log(`启动Python脚本: ${scriptName} ${args.join(' ')}`);
    
    const child = spawn('python', [scriptName, ...args]);
    
    child.stdout.on('data', (data) => {
      const output = data.toString().trim();
      console.log(`[stdout] ${output}`);
      // 如果前端需要实时日志，可以在这里通过WebSocket或其他方式发送
    });
    
    child.stderr.on('data', (data) => {
      const error = data.toString().trim();
      console.error(`[stderr] ${error}`);
    });
    
    child.on('close', (code) => {
      console.log(`${scriptName} 执行完成，退出码: ${code}`);
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`${scriptName} 执行失败，退出码: ${code}`));
      }
    });
    
    child.on('error', (error) => {
      console.error(`${scriptName} 启动失败:`, error);
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