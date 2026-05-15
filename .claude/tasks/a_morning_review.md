# A股早盘行情复盘任务

> 执行时间：北京时间每日中午 12:00（早盘 9:30-11:30 已收盘）

## 第零步：更新代码仓库

```bash
git pull origin main || echo "git pull failed, continuing..."
```

---

## 第一步：技能数据采集

### 1.1 早盘热点新闻（alphaear-news）

```bash
(cd .claude/skills/alphaear-news && /opt/miniconda3/bin/python3 -c "
from scripts.database_manager import DatabaseManager
from scripts.news_tools import NewsNowTools
db = DatabaseManager(db_path='/tmp/alphaear_news.db')
tool = NewsNowTools(db)
# 早盘复盘：财联社 + 雪球 + 微博（捕捉市场舆情）
print(tool.get_unified_trends(['cls', 'xueqiu', 'weibo']))
") 2>/dev/null || echo "[跳过] 新闻获取失败"
```

### 1.2 最新传导链信号（alphaear-deepear-lite）

```bash
/opt/miniconda3/bin/python3 .claude/skills/alphaear-deepear-lite/scripts/deepear_lite.py 2>/dev/null || echo "[跳过] DeepEar信号获取失败"
```

### 1.3 今日早盘指数价格（alphaear-stock）

```bash
(cd .claude/skills/alphaear-stock && /opt/miniconda3/bin/python3 -c "
from scripts.database_manager import DatabaseManager
from scripts.stock_tools import StockTools
from datetime import date
db = DatabaseManager(db_path='/tmp/alphaear_stock.db')tool = StockTools(db)
today = date.today().strftime('%Y-%m-%d')
for code, name in [('sh000001','上证指数'),('sz399006','创业板指'),('sz399001','深证成指'),('sh000300','沪深300')]:
    try:
        df = tool.get_stock_price(code, today, today)
        if not df.empty:
            last = df.iloc[-1]
            print(f'{name}: 开盘 {last.get(\"open\",\"N/A\")}  最新/收盘 {last[\"close\"]}  最高 {last.get(\"high\",\"N/A\")}  最低 {last.get(\"low\",\"N/A\")}')
    except:
        print(f'{name}: 数据获取失败')
") 2>/dev/null || echo "[跳过] 早盘价格数据获取失败"
```

---

## 第二步：读取今日预测记录

读取 `data/predictions/` 中最新的 `*_prediction.md`，提取今日预测的：
- 市场方向和置信度
- 预期幅度区间
- 重点关注板块
- 检验标准

---

## 第三步：早盘行情对比分析

将早盘实际行情与今日预测逐条对比：
- 市场方向：✓ 正确 / ✗ 偏差（分析原因）
- 幅度：✓ 在区间内 / ✗ 偏大 / ✗ 偏小
- 板块：命中数 / 总预测板块数

**情绪判断**（参考 alphaear-sentiment 框架）：
对早盘最具市场影响的1-2条新闻标题评分（score: -1.0~1.0），判断市场情绪偏向。

---

## 第四步：生成早盘复盘报告

**将报告保存到：** `data/daily_review/YYYY-MM-DD_morning_review.md`（使用今天实际日期）

报告结构：
1. **早盘行情概览**：主要指数开盘/早盘表现、成交量、热点板块
2. **今日预测回顾**：预测要点列表
3. **预测 vs 实际对比**：方向/幅度/板块三维评估表
4. **早盘驱动因素分析**：结合 deepear-lite 信号和 news 热点
5. **对下午盘的参考**：基于早盘走势的午后判断（强/弱延续 or 反转风险）

---

## 最后步骤：提交并推送至GitHub

```bash
git add data/
git commit -m "auto: A股早盘复盘 $(date +%Y-%m-%d)" || echo "nothing to commit"
for i in 1 2 3; do git push origin main && break || { echo "retry $i"; sleep 10; }; done
git log --oneline -1
git status
```

- 成功：「✅ 分析结果已成功推送至GitHub」
- 失败：「❌ 推送失败（已重试3次），错误：[详细错误信息]」
