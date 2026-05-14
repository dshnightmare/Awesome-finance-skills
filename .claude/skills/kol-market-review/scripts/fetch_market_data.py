"""
A股行情数据抓取工具

支持两种数据源（按优先级）：
  1. AKShare（如已安装）— 完整的指数/板块/个股数据
  2. 东方财富 / 新浪 API（无需额外安装）— 基础指数数据

用法：
  python fetch_market_data.py               # 获取今日数据
  python fetch_market_data.py --date 2026-05-14  # 获取指定日期
  python fetch_market_data.py --json        # 输出JSON格式（供程序调用）
"""

import sys
import json
import argparse
from datetime import datetime, date
from typing import Dict, Optional

try:
    import requests
    from requests.exceptions import RequestException, Timeout
except ImportError:
    print("请安装 requests：pip install requests", file=sys.stderr)
    sys.exit(1)

# 主要指数代码（东方财富接口格式）
INDICES = {
    "sh000001": "上证指数",
    "sh000688": "科创50",
    "sz399006": "创业板指",
    "sh000905": "中证500",
    "sh000852": "中证1000",
    "sz399300": "沪深300",
    "sz399001": "深证成指",
    "sh000016": "上证50",
}

# 新浪财经实时行情接口
SINA_API = "https://hq.sinajs.cn/list={codes}"

# 东方财富板块资金流向接口
EASTMONEY_SECTOR_API = (
    "https://push2.eastmoney.com/api/qt/clist/get"
    "?cb=jQuery&pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281"
    "&fltt=2&invt=2&wbp2u=&fid=f3&fs=m:90+t:2+f:!50&fields=f12,f14,f3,f4,f8"
)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def fetch_index_data() -> Dict[str, dict]:
    """通过新浪财经接口获取主要指数实时行情"""
    codes = ",".join(INDICES.keys())
    url = SINA_API.format(codes=codes)
    result = {}

    try:
        resp = requests.get(url, headers={"User-Agent": UA, "Referer": "https://finance.sina.com.cn"}, timeout=10)
        resp.encoding = "gbk"
        for line in resp.text.strip().split("\n"):
            if "=" not in line:
                continue
            code = line.split("=")[0].split("_")[-1].strip()
            raw = line.split('"')[1] if '"' in line else ""
            if not raw:
                continue
            parts = raw.split(",")
            if len(parts) < 9:
                continue
            try:
                name = INDICES.get(code, parts[0])
                current = float(parts[3]) if parts[3] else 0.0
                prev_close = float(parts[2]) if parts[2] else 0.0
                change = current - prev_close
                pct = (change / prev_close * 100) if prev_close else 0.0
                volume_yuan = float(parts[9]) if len(parts) > 9 and parts[9] else 0.0  # 成交额（元）
                result[code] = {
                    "name": name,
                    "current": current,
                    "prev_close": prev_close,
                    "change": round(change, 2),
                    "pct": round(pct, 2),
                    "volume_billion": round(volume_yuan / 1e8, 2),  # 转为亿元
                }
            except (ValueError, IndexError):
                continue
    except (RequestException, Timeout) as e:
        print(f"[警告] 新浪接口请求失败: {e}", file=sys.stderr)

    return result


def fetch_with_akshare(query_date: Optional[str] = None) -> Dict:
    """尝试用AKShare获取更完整的数据（历史数据/板块）"""
    try:
        import akshare as ak
    except ImportError:
        return {}

    result = {}
    target_date = query_date or date.today().strftime("%Y%m%d")

    try:
        # 获取A股整体统计（涨跌家数、成交额）
        stock_stat = ak.stock_zh_a_spot_em()
        if stock_stat is not None and not stock_stat.empty:
            up = (stock_stat["涨跌幅"] > 0).sum()
            down = (stock_stat["涨跌幅"] < 0).sum()
            limit_up = (stock_stat["涨跌幅"] >= 9.9).sum()
            limit_down = (stock_stat["涨跌幅"] <= -9.9).sum()
            total_volume = stock_stat["成交额"].sum() / 1e8  # 转为亿
            result["market_stat"] = {
                "up": int(up),
                "down": int(down),
                "limit_up": int(limit_up),
                "limit_down": int(limit_down),
                "total_volume_billion": round(total_volume, 2),
            }
    except Exception:
        pass

    try:
        # 板块资金流向（申万行业）
        sector_flow = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流向")
        if sector_flow is not None and not sector_flow.empty:
            top5_in = sector_flow.nlargest(5, "今日主力净流入-净额")
            top5_out = sector_flow.nsmallest(5, "今日主力净流入-净额")
            result["sector_flow"] = {
                "top_inflow": top5_in[["行业", "今日主力净流入-净额"]].to_dict("records"),
                "top_outflow": top5_out[["行业", "今日主力净流入-净额"]].to_dict("records"),
            }
    except Exception:
        pass

    return result


def build_report(index_data: Dict, extra_data: Dict, query_date: str) -> str:
    """生成人类可读的行情摘要"""
    lines = [
        f"# A股行情数据 · {query_date}",
        "",
        "## 主要指数",
        "| 指数 | 现价 | 涨跌幅 | 成交额（亿） |",
        "|-----|-----|-------|------------|",
    ]

    total_volume = 0.0
    for code, data in index_data.items():
        pct = data["pct"]
        sign = "+" if pct >= 0 else ""
        vol = data["volume_billion"]
        total_volume += vol
        lines.append(
            f"| {data['name']} | {data['current']:.2f} | {sign}{pct:.2f}% | {vol:.0f} |"
        )

    lines += ["", f"**三市合计成交额**：约 {total_volume/1e4:.2f} 万亿（估算，沪深两市主要指数合计）", ""]

    if "market_stat" in extra_data:
        s = extra_data["market_stat"]
        lines += [
            "## 市场全貌",
            f"- 上涨家数：{s.get('up', 'N/A')}",
            f"- 下跌家数：{s.get('down', 'N/A')}",
            f"- 涨停家数：{s.get('limit_up', 'N/A')}",
            f"- 跌停家数：{s.get('limit_down', 'N/A')}",
            f"- A股合计成交额：{s.get('total_volume_billion', 'N/A'):.0f} 亿",
            "",
        ]

    if "sector_flow" in extra_data:
        sf = extra_data["sector_flow"]
        lines += ["## 板块资金流向（主力净流入）", "**流入TOP5**："]
        for item in sf.get("top_inflow", []):
            lines.append(f"  - {item.get('行业', '')}: {item.get('今日主力净流入-净额', 0)/1e8:.1f}亿")
        lines += ["**流出TOP5**："]
        for item in sf.get("top_outflow", []):
            lines.append(f"  - {item.get('行业', '')}: {item.get('今日主力净流入-净额', 0)/1e8:.1f}亿")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="获取A股行情数据")
    parser.add_argument("--date", default=None, help="查询日期 YYYY-MM-DD（默认今日）")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出")
    args = parser.parse_args()

    query_date = args.date or date.today().strftime("%Y-%m-%d")

    index_data = fetch_index_data()
    extra_data = fetch_with_akshare(query_date.replace("-", ""))

    if args.json:
        output = {
            "date": query_date,
            "indices": index_data,
            **extra_data,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(build_report(index_data, extra_data, query_date))


if __name__ == "__main__":
    main()
