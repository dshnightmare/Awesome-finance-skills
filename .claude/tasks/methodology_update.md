# 预测方法论迭代优化任务

> 执行时间：北京时间每日 18:00（A股已收盘，今日预测结果已可核验）

## 第零步：更新代码仓库

```bash
git pull origin main || echo "git pull failed, continuing..."
```

方法论文件固定路径：`data/methodology/prediction_methodology.md`
后续预测agent每天早上会读取该文件，因此方法论必须保持**抽象、普适、结构清晰**。

---

## 第一步：技能数据采集（辅助评估）

### 1.1 今日传导链信号（alphaear-deepear-lite）

```bash
/opt/miniconda3/bin/python3 .claude/skills/alphaear-deepear-lite/scripts/deepear_lite.py 2>/dev/null || echo "[跳过] DeepEar信号获取失败"
```

记录：哪些高置信度信号被市场验证了？哪些被证伪了？

### 1.2 今日晚间财经新闻（alphaear-news）

```bash
(cd .claude/skills/alphaear-news && /opt/miniconda3/bin/python3 -c "
from scripts.news_tools import NewsNowTools
tool = NewsNowTools()
print(tool.get_unified_trends(['cls', 'wallstreetcn', 'xueqiu']))
") 2>/dev/null || echo "[跳过] 新闻获取失败"
```

用于判断当日市场行为的后验归因（何种事件/信号主导了今日走势）。

---

## 第二步：读取今日预测与复盘

- 读取 `data/predictions/` 中最新的 `*_prediction.md`，提取预测观点和检验标准
- 读取 `data/daily_review/` 中最新的 `*_full_review.md`，提取实际走势和KOL分析结论

---

## 第三步：对比评估今日预测得失

逐条对比，明确判断：
- 方向预测：正确/错误（+1/-1分）
- 幅度预测：在区间内/偏大/偏小（+1/0/-1分）
- 板块预测：命中数/总预测数
- 今日预测总评：准确/基本准确/偏差较大
- 失误的具体原因分析（信号忽略？权重偏差？逻辑错误？传导失效？）

**结合 alphaear-signal-tracker 框架评估信号表现：**

对今日预测使用的每个关键信号，按以下框架判断其演化状态：
- **Strengthened（强化）**：信号逻辑被今日市场验证
- **Weakened（弱化）**：信号有效但强度不足预期
- **Falsified（证伪）**：信号在今日环境中失效
- **Unchanged（不变）**：中性，无新信息

---

## 第四步：读取并理解现有方法论

读取 `data/methodology/prediction_methodology.md`（不存在则从零创建）。
理解现有方法论的结构和核心规则。

---

## 第五步：更新方法论

根据今日得失，结合 deepear-lite 信号验证结果，对方法论进行针对性修订。

**修订原则：**
- **抽象性**：规则描述市场普遍规律，不绑定具体日期或个股
- **普适性**：适用于不同市场环境（牛/熊/震荡）
- **可操作性**：每条规则能直接指导预测决策
- **权重意识**：不同信号的重要性有明确优先级排序
- **案例锚定**：每条重要规则附1-2个历史验证案例

**修订方式：**
- 预测准确 → 强化对应规则或提高权重
- 预测失误 → 修正规则或降低失效信号权重，补充反例案例
- DeepEar 信号 Falsified → 将对应传导路径加入"失效条件"
- 发现新规律 → 新增规则条目

---

## 第六步：写回方法论文件

将更新后的完整方法论写回 `data/methodology/prediction_methodology.md`。

文件格式：

```
# A股预测方法论
> 最后更新：YYYY-MM-DD | 版本：vN.N

## 核心理念
[2-3句话概括预测框架的哲学基础]

## 一、信号优先级体系
### 1.1 高权重信号（必须考量）
- [信号名称]：[描述] → [预测意义] [案例]
### 1.2 中权重信号（参考考量）
- ...
### 1.3 低权重/失效信号（谨慎使用）
- ...

## 二、市场环境识别
- 趋势市特征与应对策略
- 震荡市特征与应对策略
- 转折信号识别

## 三、美股→A股传导规则
- [传导规律描述] [有效条件] [失效条件]

## 四、板块轮动规律
- [规律描述] [案例]

## 五、常见陷阱与反例
- [陷阱描述]：[历史反例]

## 六、修订日志
| 日期 | 修订内容 | 触发原因 |
|------|----------|----------|
| YYYY-MM-DD | [修订摘要] | [今日预测得失] |
```

---

## 第七步：输出总结

1. 今日预测得失评分（方向/幅度/板块）
2. 关键信号演化状态（哪些 Strengthened/Falsified）
3. 本次方法论修订的核心变化（1-3条）
4. 方法论当前版本号

---

## 最后步骤：提交并推送至GitHub

```bash
git add data/
git commit -m "auto: 方法论更新 $(date +%Y-%m-%d)" || echo "nothing to commit"
for i in 1 2 3; do git push origin main && break || { echo "retry $i"; sleep 10; }; done
git log --oneline -1
git status
```

- 成功：「✅ 分析结果已成功推送至GitHub」
- 失败：「❌ 推送失败（已重试3次），错误：[详细错误信息]」
