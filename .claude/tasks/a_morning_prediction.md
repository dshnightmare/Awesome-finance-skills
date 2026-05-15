# A股早盘走势预测任务

> 执行时间：北京时间每日早上 9:00（A股尚未开盘，9:30开盘）

## 第零步：更新代码仓库

```bash
git pull origin main || echo "git pull failed, continuing..."
```

---

## 第一步：读取预测方法论（最重要）

读取 `data/methodology/prediction_methodology.md`，完整理解其中的：
- 信号优先级体系（高/中/低权重信号）
- 市场环境识别规则
- 美股传导规则
- 板块轮动规律
- 常见陷阱

如果文件不存在，说明方法论尚未建立，用通用分析逻辑继续。

---

## 第二步：技能数据采集

按顺序运行以下技能，获取预测所需的实时数据。

### 2.1 最新财经信号（alphaear-deepear-lite）

```bash
/opt/miniconda3/bin/python3 .claude/skills/alphaear-deepear-lite/scripts/deepear_lite.py 2>/dev/null || echo "[跳过] DeepEar信号获取失败"
```

重点关注：信号置信度、传导链、对A股的影响判断。

### 2.2 早盘前财经新闻（alphaear-news）

```bash
(cd .claude/skills/alphaear-news && /opt/miniconda3/bin/python3 -c "
from scripts.database_manager import DatabaseManager
from scripts.news_tools import NewsNowTools
db = DatabaseManager(db_path='/tmp/alphaear_news.db')
tool = NewsNowTools(db)
# A股预测关键源：财联社 + 华尔街见闻 + 雪球
print(tool.get_unified_trends(['cls', 'wallstreetcn', 'xueqiu']))
") 2>/dev/null || echo "[跳过] 新闻获取失败"
```

### 2.3 A股主要指数近期价格（alphaear-stock）

```bash
(cd .claude/skills/alphaear-stock && /opt/miniconda3/bin/python3 -c "
from scripts.database_manager import DatabaseManager
from scripts.stock_tools import StockTools
from datetime import date, timedelta
db = DatabaseManager(db_path='/tmp/alphaear_stock.db')tool = StockTools(db)
end = date.today().strftime('%Y-%m-%d')
start = (date.today() - timedelta(days=10)).strftime('%Y-%m-%d')
for code, name in [('sh000001','上证指数'),('sz399006','创业板指'),('sh000300','沪深300'),('sh000905','中证500')]:
    try:
        df = tool.get_stock_price(code, start, end)
        if not df.empty and len(df) >= 2:
            last = df.iloc[-1]
            prev = df.iloc[-2]
            pct = (last['close']/prev['close']-1)*100
            print(f'{name}: {last[\"close\"]:.2f}  昨日涨跌 {pct:+.2f}%  成交量 {last.get(\"volume\",0):.0f}')
    except Exception as e:
        print(f'{name}: 获取失败')
") 2>/dev/null || echo "[跳过] A股价格数据获取失败"
```

---

## 第三步：读取昨日复盘与美股数据

- 读取 `data/daily_review/` 中最新的 `*_full_review.md`（昨日A股全天复盘）
- 读取 `data/us_market_review/` 中最新的 `*_us_market.md`（最新美股收盘数据）

提取关键信息：市场方向、强弱板块、资金流向、美股传导信号。

---

## 第四步：生成今日预测报告

**严格按照第一步方法论的信号优先级进行分析**，结合第二步技能数据和第三步历史数据做出预测。

**预测框架：**
1. 逐一列出当前高权重信号（来自 deepear-lite + news + 价格数据）并判断多空
2. 评估市场环境（趋势市/震荡市/转折点）
3. 美股传导分析（按方法论规则判断传导有效性）
4. 综合得出方向预测 + 置信度

**将预测报告保存到：** `data/predictions/YYYY-MM-DD_prediction.md`（使用今天实际日期）

报告结构：

### 一、信息输入汇总
- 方法论版本：[v?.?]
- DeepEar信号摘要：[最高置信度信号 1-3 条]
- 昨日A股情况：[主要指标小结]
- 昨日美股情况：[主要指标小结]
- 今日关键新闻信号：[按方法论权重排序，3-5条]

### 二、今日A股预测
- **市场方向**：偏多 / 偏空 / 震荡，置信度（高/中/低）
- **预期幅度**：上证指数波动区间预估
- **重点关注板块**：2-3个，附方法论依据
- **驱动逻辑**：主要依据的方法论规则
- **风险因素**：可能导致预测失误的事项

### 三、预测检验标准（收盘后对照）
1. 市场方向是否正确（涨/跌/震荡）
2. 指数涨跌幅是否在预估区间内
3. 重点板块是否表现

完成后输出预测摘要。

---

## 最后步骤：提交并推送至GitHub

```bash
git add data/
git commit -m "auto: A股走势预测 $(date +%Y-%m-%d)" || echo "nothing to commit"
for i in 1 2 3; do git push origin main && break || { echo "retry $i"; sleep 10; }; done
git log --oneline -1
git status
```

- 成功：「✅ 分析结果已成功推送至GitHub」
- 失败：「❌ 推送失败（已重试3次），错误：[详细错误信息]」
