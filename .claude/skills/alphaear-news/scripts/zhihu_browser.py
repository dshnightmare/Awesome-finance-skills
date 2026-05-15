"""
知乎无头浏览器工具

两步使用流程：
  1. 首次运行 `python zhihu_browser.py setup` —— 打开可见 Chrome，手动登录后自动保存 Session
  2. 后续调用 ZhihuBrowserTools().fetch_user_activities(slug) —— 无头模式复用 Session
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

# Session 文件默认保存在 ~/.zhihu_session.json，可通过环境变量覆盖
SESSION_FILE = Path(os.getenv("ZHIHU_SESSION_FILE", Path.home() / ".zhihu_session.json"))

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

VERB_MAP = {
    "ANSWER_CREATE":           "回答了问题",
    "ARTICLE_CREATE":          "发布了文章",
    "QUESTION_CREATE":         "提了问题",
    "ANSWER_VOTE_UP":          "赞同了回答",
    "ARTICLE_VOTE_UP":         "赞同了文章",
    "MEMBER_VOTEUP_ANSWER":    "赞同了回答",
    "MEMBER_VOTEUP_ARTICLE":   "赞同了文章",
    "PIN_CREATE":              "发了想法",
    "MEMBER_COLLECT_ANSWER":   "收藏了回答",
    "MEMBER_FOLLOW_QUESTION":  "关注了问题",
    "QUESTION_FOLLOW":         "关注了问题",
    "MEMBER_FOLLOW_COLUMN":    "关注了专栏",
    "MEMBER_FOLLOW_COLLECTION": "关注了收藏夹",
    "MEMBER_COLLECT_ARTICLE":   "收藏了文章",
    "MEMBER_COLLECT_ANSWER":    "收藏了回答",
    "MEMBER_FOLLOW_ROUNDTABLE": "关注了圆桌",
}


def _get_playwright():
    """延迟导入，自动查找 playwright 安装位置"""
    _SEARCH_PATHS = [
        "/Users/bytedance/.local/lib/python3.12/site-packages",  # user site-packages
        os.path.join(os.environ.get("TMPDIR", "/tmp"), "pylibs"),  # Claude Code sandbox
    ]
    for p in _SEARCH_PATHS:
        if p not in sys.path:
            sys.path.insert(0, p)
    try:
        from playwright.async_api import async_playwright
        return async_playwright
    except ImportError:
        raise RuntimeError(
            "未安装 playwright。请运行：\n"
            "  /opt/miniconda3/bin/pip install playwright "
            "--target=/Users/bytedance/.local/lib/python3.12/site-packages\n"
            "  PLAYWRIGHT_BROWSERS_PATH=$TMPDIR/pw-browsers "
            "PYTHONPATH=/Users/bytedance/.local/lib/python3.12/site-packages "
            "/opt/miniconda3/bin/python -m playwright install chromium"
        )


async def _setup_session_async():
    """打开可见 Chrome，等待用户手动登录，完成后保存 Session。"""
    async_playwright = _get_playwright()
    print("=" * 55)
    print("知乎 Session 初始化")
    print("=" * 55)
    print("即将打开 Chrome 浏览器，请在浏览器中完成知乎登录。")
    print("登录成功后，回到此终端按 Enter 保存 Session。")
    print("=" * 55)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path=CHROME_PATH,
            args=["--no-sandbox"],
        )
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.zhihu.com/signin")
        print("\n浏览器已打开，请登录知乎...")

        # 等待用户在终端按 Enter
        await asyncio.get_event_loop().run_in_executor(
            None, input, "\n登录完成后按 Enter 保存 Session > "
        )

        cookies = await context.cookies()
        storage = await context.storage_state()

        SESSION_FILE.write_text(json.dumps(storage, ensure_ascii=False, indent=2))
        print(f"\n✅ Session 已保存到 {SESSION_FILE}")
        print(f"   共保存 {len(cookies)} 个 Cookie")

        await browser.close()


async def _fetch_async(user_slug: str, limit: int) -> List[Dict]:
    """无头模式，加载已保存 Session，拦截知乎动态 API 响应。"""
    if not SESSION_FILE.exists():
        raise FileNotFoundError(
            f"未找到 Session 文件：{SESSION_FILE}\n"
            "请先运行：python zhihu_browser.py setup"
        )

    async_playwright = _get_playwright()
    storage_state = json.loads(SESSION_FILE.read_text())
    activities: List[Dict] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            storage_state=storage_state,
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        async def on_response(resp):
            if f"moments/{user_slug}/activities" in resp.url:
                try:
                    body = await resp.json()
                    activities.extend(body.get("data", []))
                    logger.info(f"捕获 {len(body.get('data', []))} 条动态 from {resp.url[:80]}")
                except Exception as e:
                    logger.warning(f"解析动态响应失败: {e}")

        page.on("response", on_response)

        url = f"https://www.zhihu.com/people/{user_slug}"
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)

        # 如果需要更多条目，可向下滚动触发分页
        if len(activities) < limit:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)

        await browser.close()

    return activities[:limit]


def _parse_activity(item: Dict) -> Dict:
    verb = item.get("verb", "")
    target = item.get("target", {})
    ts = item.get("created_time", 0)

    title = (
        target.get("title")
        or target.get("question", {}).get("title", "")
        or target.get("content", "")[:80]
        or ""
    )
    url = target.get("url") or target.get("question", {}).get("url", "")
    excerpt = target.get("excerpt") or target.get("content", "")
    if excerpt:
        excerpt = excerpt[:150].replace("\n", " ")

    return {
        "id": item.get("id", ""),
        "verb": verb,
        "verb_text": VERB_MAP.get(verb, verb),
        "created_time": ts,
        "created_time_str": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "",
        "title": title,
        "url": url,
        "excerpt": excerpt,
    }


class ZhihuBrowserTools:
    """使用无头 Chrome 获取知乎大V动态（需先运行 setup 保存登录态）"""

    def fetch_user_activities(self, user_slug: str, limit: int = 20) -> List[Dict]:
        """
        获取指定知乎用户的最新动态。

        Args:
            user_slug: 用户 URL 中的唯一标识，如 "zhang-xue-feng-51"
            limit:     最多返回条数

        Returns:
            动态列表，字段：id, verb, verb_text, created_time_str, title, url, excerpt
        """
        raw = asyncio.run(_fetch_async(user_slug, limit))
        return [_parse_activity(item) for item in raw]

    def format_activities(self, activities: List[Dict], user_slug: str) -> str:
        """格式化动态列表为 Markdown 报告"""
        if not activities:
            return (
                f"❌ 未获取到 @{user_slug} 的动态。\n"
                f"请先运行：python scripts/zhihu_browser.py setup"
            )

        lines = [
            f"## 知乎动态：@{user_slug}",
            f"共 {len(activities)} 条 · {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        ]
        for i, a in enumerate(activities, 1):
            time_str = a["created_time_str"] or "未知时间"
            verb_text = a["verb_text"]
            title = a["title"] or "（无标题）"
            url = a["url"]
            excerpt = a["excerpt"]

            if url:
                lines.append(f"**{i}.** `{time_str}` {verb_text}")
                lines.append(f"   [{title}]({url})")
            else:
                lines.append(f"**{i}.** `{time_str}` {verb_text}：{title}")

            if excerpt:
                lines.append(f"   > {excerpt}…")
            lines.append("")

        return "\n".join(lines)


# ── CLI 入口 ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python zhihu_browser.py setup              # 首次登录，保存 Session")
        print("  python zhihu_browser.py fetch <user_slug>  # 获取用户动态")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "setup":
        asyncio.run(_setup_session_async())

    elif cmd == "fetch":
        if len(sys.argv) < 3:
            print("缺少 user_slug，例如：python zhihu_browser.py fetch zhang-xue-feng-51")
            sys.exit(1)
        slug = sys.argv[2]
        tool = ZhihuBrowserTools()
        acts = tool.fetch_user_activities(slug, limit=20)
        print(tool.format_activities(acts, slug))
