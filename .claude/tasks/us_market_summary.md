# 美股每日行情总结任务

> 执行时间：北京时间每日凌晨 5:30（美股已收盘）

## 第零步：更新代码仓库

```bash
git pull origin main || echo "git pull failed, continuing..."
```

---

## 第一步：技能数据采集

按顺序运行以下技能，收集原始数据供后续分析使用。所有命令失败时打印提示并继续，不中断任务。

### 1.1 最新财经信号（alphaear-deepear-lite）

```bash
/opt/miniconda3/bin/python3 .claude/skills/alphaear-deepear-lite/scripts/deepear_lite.py 2>/dev/null || echo "[跳过] DeepEar信号获取失败"
```

输出：最新A股/美股传导链信号，含置信度和摘要。

### 1.2 实时财经新闻热点（alphaear-news）

```bash
(cd .claude/skills/alphaear-news && /opt/miniconda3/bin/python3 -c "
from scripts.database_manager import DatabaseManager
from scripts.news_tools import NewsNowTools
db = DatabaseManager(db_path='/tmp/alphaear_news.db')
tool = NewsNowTools(db)
# 美股相关：财联社 + 华尔街见闻 + 雪球
print(tool.get_unified_trends(['cls', 'wallstreetcn', 'xueqiu']))
") 2>/dev/null || echo "[跳过] 新闻热点获取失败"
```

### 1.3 美股个股价格数据（alphaear-stock）

> 注：alphaear-stock 通过 yfinance 获取美股数据，若遭遇 Rate Limit 则跳过，用新闻来源补充。

```bash
(cd .claude/skills/alphaear-stock && /opt/miniconda3/bin/python3 -c "
from scripts.database_manager import DatabaseManager
from scripts.stock_tools import StockTools
from datetime import date, timedelta
db = DatabaseManager(db_path='/tmp/alphaear_stock.db')
tool = StockTools(db)
end = date.today().strftime('%Y-%m-%d')
start = (date.today() - timedelta(days=5)).strftime('%Y-%m-%d')
for ticker, name in [('SPY','S&P500'), ('QQQ','纳斯达克'), ('NVDA','英伟达'), ('AAPL','苹果')]:
    try:
        df = tool.get_stock_price(ticker, start, end)
        if not df.empty:
            last = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else last
            pct = (last['close']/prev['close']-1)*100
            print(f'{name}({ticker}): {last[\"close\"]:.2f}  {pct:+.2f}%')
        else:
            print(f'{name}: 无数据')
    except Exception as e:
        print(f'{name}: 获取失败')
") 2>/dev/null || echo "[跳过] 美股价格数据获取失败"
```

---

## 第二步：生成行情总结报告

综合第一步收集的数据，加上公开财经信息，生成今日美股行情总结报告。

**分析要点（依次覆盖）：**
- 三大指数 + 罗素2000 收盘价、涨跌幅、成交量
- 主要板块表现（科技、金融、能源、医疗、可选消费等 ETF 涨跌）
- 个股亮点：涨跌幅前5、重要财报/新闻驱动
- 宏观因素：美债收益率、美元指数、VIX、当日重要经济数据
- 市场情绪评估：结合 alphaear-deepear-lite 信号和 alphaear-news 热点，判断多空情绪
- 今日核心驱动事件（3条以内，精准归因）
- 对A股次日的传导预判（参考 deepear-lite 传导链信号）

**情绪评分**（使用 alphaear-sentiment 框架）：

根据以下 prompt 对今日最重要的3条新闻标题逐一打分：
```
请分析以下金融文本的情绪极性。
返回: {"score": <-1.0到1.0>, "label": "<positive/negative/neutral>", "reason": "<理由>"}
文本: {标题}
```

**将报告保存到：** `data/us_market_review/YYYY-MM-DD_us_market.md`（使用北京时间当天 `date +%Y-%m-%d`）

报告结构：
1. 市场概览（三大指数 + 罗素2000，表格形式）
2. 板块表现（领涨/落后板块）
3. 个股亮点（涨跌幅前5）
4. 宏观因素（美债、美元、VIX）
5. 市场情绪与展望（含 DeepEar 信号摘要 + 对A股传导预判）

---

## 最后步骤：提交并推送至GitHub

```bash
git add data/
git commit -m "auto: 美股行情总结 $(date +%Y-%m-%d)" || echo "nothing to commit"
for i in 1 2 3; do git push origin main && break || { echo "retry $i"; sleep 10; }; done
git log --oneline -1
git status
```

- 成功：「✅ 分析结果已成功推送至GitHub」
- 失败：「❌ 推送失败（已重试3次），错误：[详细错误信息]」
