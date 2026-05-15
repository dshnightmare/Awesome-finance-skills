# A股全天行情复盘任务

> 执行时间：北京时间每日 16:00（全天交易 9:30-15:00 已结束）

## 第零步：更新代码仓库

```bash
git pull origin main || echo "git pull failed, continuing..."
```

---

## 第一步：读取前一天的预测记录

读取 `data/predictions/` 中最新的 `*_prediction.md`，记录主要预测观点（方向、幅度、板块）。

---

## 第二步：技能数据采集

### 2.1 今日结构化行情数据（kol-market-review/fetch_market_data.py）

```bash
/opt/miniconda3/bin/python3 .claude/skills/kol-market-review/scripts/fetch_market_data.py 2>/dev/null || echo "[跳过] 行情数据获取失败，将使用其他来源"
```

输出：上证指数、科创50、创业板指、中证500、中证1000、沪深300 的涨跌幅和成交额。

### 2.2 今日最新传导链信号（alphaear-deepear-lite）

```bash
/opt/miniconda3/bin/python3 .claude/skills/alphaear-deepear-lite/scripts/deepear_lite.py 2>/dev/null || echo "[跳过] DeepEar信号获取失败"
```

### 2.3 今日财经新闻热点（alphaear-news）

```bash
(cd .claude/skills/alphaear-news && /opt/miniconda3/bin/python3 -c "
from scripts.database_manager import DatabaseManager
from scripts.news_tools import NewsNowTools
db = DatabaseManager(db_path='/tmp/alphaear_news.db')
tool = NewsNowTools(db)
# 全天复盘：财联社 + 华尔街见闻 + 雪球（全面覆盖）
print(tool.get_unified_trends(['cls', 'wallstreetcn', 'xueqiu']))
") 2>/dev/null || echo "[跳过] 新闻热点获取失败"
```

### 2.4 A股指数全天价格验证（alphaear-stock，备用）

若 2.1 行情数据不完整，用此补充：

```bash
(cd .claude/skills/alphaear-stock && /opt/miniconda3/bin/python3 -c "
from scripts.database_manager import DatabaseManager
from scripts.stock_tools import StockTools
from datetime import date
db = DatabaseManager(db_path='/tmp/alphaear_stock.db')tool = StockTools(db)
today = date.today().strftime('%Y-%m-%d')
for code, name in [('sh000001','上证'),('sz399006','创业板'),('sh000300','沪深300'),('sh000905','中证500')]:
    try:
        df = tool.get_stock_price(code, today, today)
        if not df.empty:
            r = df.iloc[-1]
            pct = (r['close']/r['open']-1)*100 if r.get('open') else 0
            print(f'{name}: 收盘 {r[\"close\"]:.2f}  日涨跌 {pct:+.2f}%')
    except: pass
") 2>/dev/null || echo "[跳过] 备用行情数据获取失败"
```

---

## 第三步：7位KOL多视角复盘

读取 `.claude/skills/kol-market-review/references/kol_frameworks.md`，获取所有7位KOL的分析框架，结合第二步收集的数据，逐一按各KOL方法论分析今日行情：

1. **么瑞与小A**（技术波段）：分析量能、K线形态、蝗虫过境信号，给出仓位建议
2. **MR Dang**（宏观解读）：结合 deepear-lite 传导链信号和 news 核心事件，分析市场定价偏差
3. **寒武纪的鳄鱼**（周期×价值）：评估央企资源板块信号，判断周期位置
4. **派大星皮皮**（趋势配置）：回答三问（牛/震/熊、增量/存量/减量、多空），评估进攻方向
5. **Deep Van**（全球产业链）：结合 deepear-lite 全球链条信号，评估多空布局
6. **白白胖胖0**（估值+右侧）：分析技术形态，检查止损信号，标注关注标的
7. **龙开**（宏观叙事→期货）：更新宏观叙事，分析商品/期货信号

每个KOL分析须：仅使用该KOL自己关注的变量；结论量化（仓位用成数，概率用%）。

最后提炼：共识（≥5/7一致）、主要分歧、明日关键变量。

---

## 第四步：预测 vs 实际对比分析

将实际行情与第一步预测逐条对比：
- 预测准确的部分（✓）
- 预测偏差的部分及原因分析（✗）
- 整体命中率（方向/幅度/板块三维评分）

---

## 第五步：生成完整复盘报告

**将报告保存到：** `data/daily_review/YYYY-MM-DD_full_review.md`（使用今天实际日期）

报告结构：

### 一、全天行情概览
主要指数涨跌幅表（来自 fetch_market_data.py 或 alphaear-stock）、成交量、涨跌家数

### 二、今日核心新闻与信号
来自 alphaear-deepear-lite 的传导链信号 + alphaear-news 热点（各取 Top 3）

### 三、前日预测回顾
预测要点列表

### 四、预测 vs 实际对比
对比表（方向/板块/幅度三维评分）+ 偏差原因分析

### 五、7位KOL多视角复盘
逐一展示每位KOL分析结论

**综合研判**：
- 共识（≥5/7一致）
- 主要分歧及分歧来源
- 明日关键变量（3条）
- 综合仓位建议范围

### 六、经验总结与预测模型优化建议

完成后输出报告摘要（各章节核心结论，不超过500字）。

---

## 最后步骤：提交并推送至GitHub

```bash
git add data/
git commit -m "auto: A股全天复盘 $(date +%Y-%m-%d)" || echo "nothing to commit"
for i in 1 2 3; do git push origin main && break || { echo "retry $i"; sleep 10; }; done
git log --oneline -1
git status
```

- 成功：「✅ 分析结果已成功推送至GitHub」
- 失败：「❌ 推送失败（已重试3次），错误：[详细错误信息]」
