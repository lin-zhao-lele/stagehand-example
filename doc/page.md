
# page 概览
  除了observe()、act()和extract()之外，Stagehand的page对象还有许多其他常用方法。 

  这些方法与observe()、act()和extract()一起构成了完整的Stagehand页面操作API，可以帮助您实现各种复杂的浏览器自动化任务。

## 页面导航方法

  1. 页面加载和导航

  ### 导航到指定URL
```angular2html
  await page.goto("https://www.example.com")
```


  ### 后退到上一页
```angular2html
  await page.go_back()
```


  ### 前进到下一页
```angular2html
  await page.go_forward()
```


  ### 刷新当前页面
```angular2html
  await page.reload()
```


  ### 等待指定时间（毫秒）
```angular2html
  await page.wait_for_timeout(3000)
```


  2. 页面状态等待

  ### 等待页面加载完成
```angular2html
  await page.wait_for_load_state()
```


  ### 等待网络空闲
```angular2html
  await page.wait_for_load_state("networkidle")
```


  ### 等待DOM内容加载完成
```angular2html
  await page.wait_for_load_state("domcontentloaded")
```


## 页面信息获取方法

  1. 页面元信息

  ### 获取当前页面URL
```angular2html
  current_url = page.url
```


  ### 获取页面标题
```angular2html
  title = await page.title()
```


  ### 获取页面内容（HTML）
```angular2html
  content = await page.content()
```


  ### 获取页面截图
```angular2html
  screenshot = await page.screenshot()
```


  2. 页面尺寸和视口

  ### 设置视口大小
```angular2html
  await page.set_viewport_size({"width": 1920, "height": 1080})
```


  ### 获取页面尺寸
```angular2html
  size = await page.viewport_size()
```


## 元素交互方法

  1. 元素定位和操作

  ### 通过选择器查找元素
  ```
  element = page.locator("#button-id")
  ```


  ### 点击元素
```angular2html
  await element.click()
```

  ### 填充输入框
```angular2html
  await element.fill("输入文本")
```


  ### 获取元素文本
```angular2html
  text = await element.text_content()
```


  ### 获取元素属性
```angular2html
  value = await element.get_attribute("value")
```


  2. 等待元素

  ### 等待元素出现
```angular2html
  await page.wait_for_selector("#element-id")
```


  ### 等待元素消失
```angular2html
  await page.wait_for_selector("#element-id", state="hidden")
```


## 高级功能方法

  1. 文件下载和上传

  ### 设置下载路径
```angular2html
  page.set_download_path("./downloads")
```


  ### 上传文件
```angular2html
  await page.set_input_files("#file-input", "path/to/file.txt")
```


  2. 键盘和鼠标操作

  ### 按键操作
```angular2html
  await page.keyboard.press("Enter")
  await page.keyboard.type("Hello World")
```

  ### 鼠标操作
```angular2html
  await page.mouse.click(100, 200)
  await page.mouse.move(100, 200)
```


  3. JavaScript执行

  ### 在页面中执行JavaScript
```angular2html
  result = await page.evaluate("() => document.title")
```

  ### 在页面中执行带参数的JavaScript
```angular2html
  result = await page.evaluate("""(data) => {
      return document.querySelector(data.selector).textContent;
  }""", {"selector": "#my-element"})
```


## 浏览器上下文方法

## 页面管理

  ### 创建新页面

```angular2html
  new_page = await context.new_page()
```
  ### 获取所有页面

```angular2html
  pages = context.pages()
```
  ### 关闭页面

```angular2html
  await page.close()
```


## Cookie和存储
  ### 获取Cookies
```angular2html
  cookies = await context.cookies()
```

  ### 设置Cookies
```angular2html
  await context.add_cookies([{
      "name": "session_id",
      "value": "12345",
      "domain": "example.com",
      "path": "/"
  }])
```


  ### 清除存储
```angular2html
  await context.clear_cookies()
```


## 调试和监控方法

  1. 控制台监听

  ### 监听控制台消息
```angular2html
  page.on("console", lambda msg: print(f"控制台消息: {msg.text}"))
```


  2. 网络请求监听

  ### 监听网络请求
```angular2html
  page.on("request", lambda request: print(f"请求: {request.url}"))
```


  ### 监听响应
```angular2html
  page.on("response", lambda response: print(f"响应: {response.status} {response.url}"))
```


## 在Stagehand中的特殊方法     AI增强功能

  ### 使用AI代理执行复杂任务
```angular2html
  agent = stagehand.agent()
  result = await agent.execute("完成注册流程")
```

  ### 获取AI建议的操作
```angular2html
  suggestions = await page.observe("找到可以登录的元素")
```



