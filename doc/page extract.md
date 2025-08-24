 # page.extract() 功能说明

  page.extract()是Stagehand框架中的一个重要方法，用于从网页中提取结构化数据。它使用AI来理解页面内容并按照指定的指令提取信息。

  主要参数

  1. instruction (必需): 一个自然语言指令，描述要提取什么内容

  2. schema (可选): 定义期望返回数据结构的模式（在TypeScript版本中更常用）

  使用示例

  ## 1. 基本文本提取

  ### 提取页面的所有文本内容
  content = await page.extract(instruction="提取页面的文本内容")

  ### 提取特定元素的文本
  title = await page.extract(instruction="提取页面标题")

  ## 2. 提取特定信息

  ### 提取包含特定关键词的内容
  articles = await page.extract(instruction="找到页面中所有标题包含'巨能智能'的文章")

  ### 提取表格数据
  table_data = await page.extract(instruction="提取表格中的所有数据，包括公司名称和股票代码")

  ## 3. 结构化数据提取（TypeScript示例）

  // 提取结构化对象

```angular2html
  const item = await page.extract({
    instruction: "提取商品的价格",
    schema: z.object({
      price: z.number(),
    }),
  });

```


  // 提取对象列表

```angular2html
  
const apartments = await page.extract({
    instruction: "提取所有公寓列表信息，包括地址、价格和面积",
    schema: z.object({
      list_of_apartments: z.array(
        z.object({
          address: z.string(),
          price: z.string(),
          square_feet: z.string(),
        }),
      ),
    })
  })

```


  ## 4. 复杂数据提取

  ### 提取新闻文章信息
  news = await page.extract(
      instruction="提取所有新闻文章的标题、发布日期和链接地址"
  )

  ### 提取产品信息
  products = await page.extract(
      instruction="提取页面上所有产品的名称、价格和描述信息"
  )



 ## 返回值

  page.extract()的返回值取决于页面内容和指令：
  - 可能返回字符串（简单文本提取）
  - 可能返回字典对象（结构化数据）
  - 可能返回None（如果没有找到匹配内容）

 ## 错误处理

  在实际使用中，应该对extract方法进行适当的错误处理，因为：
  1. 网络问题可能导致提取失败
  2. 页面内容可能与指令不匹配
  3. AI可能无法正确解析页面结构
