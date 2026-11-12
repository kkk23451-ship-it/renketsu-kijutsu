"""記述問題練習アプリの公開版（index.html）を作る。

使い方: python build.py <アプリの HTML> <出力先のフォルダー>

公開版は、元の HTML から問題の初期データ（SEED_QUESTIONS）を抜き、
スマホのホーム画面に置くための設定を <head> に足したもの。
問題と記録は、アプリが非公開の DB から読む。
"""
import re
import sys
from pathlib import Path

HEAD_TAGS = """<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#f5f4f0" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#15171a" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="連結記述">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-180.png">"""

VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1">'
SEED = re.compile(r"const SEED_QUESTIONS = \[\n.*?\n\];\n", re.S)


def build(src: Path) -> str:
    html = src.read_text(encoding="utf-8")
    if html.count(VIEWPORT) != 1:
        raise SystemExit("viewport の行が見つからないか、複数ある")
    seed = SEED.findall(html)
    if len(seed) != 1:
        raise SystemExit("SEED_QUESTIONS が見つからないか、複数ある")
    answers = re.findall(r'^  a:"(.{12})', seed[0], re.M)
    if not answers:
        raise SystemExit("SEED_QUESTIONS の中に解答例が見つからない")
    html = SEED.sub("const SEED_QUESTIONS = [];   // 公開版には問題を入れない（DB から読む）\n", html)
    html = html.replace(VIEWPORT, HEAD_TAGS)
    leaked = [a for a in answers if a in html]
    if leaked:
        raise SystemExit(f"問題の中身が残っている: {leaked[:3]}")
    return html


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    out = Path(sys.argv[2]) / "index.html"
    out.write_text(build(Path(sys.argv[1])), encoding="utf-8", newline="\n")
    print(f"wrote {out}")
