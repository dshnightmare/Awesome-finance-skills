# 美股每日行情总结任务

> 执行时间：北京时间每日凌晨 5:30（美股已收盘）

## 第零步：更新代码仓库

```bash
git pull origin main || echo "git pull failed, continuing..."
```

## 第一步：获取美股最新交易日行情

使用仓库中可用的工具和技能获取美股最新一个交易日的行情数据，包括：
- 道琼斯指数（Dow Jones）、标普500（S&P 500）、纳斯达克（Nasdaq）、罗素2000的涨跌幅及收盘价
- 全天涨幅、跌幅最大的个股（前5名）
- 主要板块（科技、金融、能源、医疗等）表现
- 当日重要财经新闻及市场驱动因素
- VIX恐慌指数变化（如可获取）
- 美债收益率、美元指数动向（如可获取）

## 第二步：生成行情总结报告

将报告保存到 data/us_market_review/ 目录，文件名格式：YYYY-MM-DD_us_market.md（使用北京时间当天日期，即执行任务时的 `date +%Y-%m-%d`，勿使用美东时间）。

报告结构：
1. 市场概览（三大指数涨跌幅、成交量）
2. 板块表现（热门板块与落后板块）
3. 个股亮点（涨跌幅前5、重要财报或新闻驱动）
4. 宏观因素（美债、美元、VIX、重要经济数据）
5. 市场情绪与展望（多空信号、下一交易日关注点）

完成后输出报告内容摘要。

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
