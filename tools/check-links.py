#!/usr/bin/env python3
"""检查站内所有链接的协议、每一页的 canonical，以及版本号有没有对上。

    python3 tools/check-links.py [目录]

## 为什么要有这个

一条 `http://` 的外链，在 https 的页面上会被浏览器**当作混合内容拦掉或降级**，
而它长得和正常链接一模一样——不点开根本看不出来。这类问题不会报错，
只会让某个链接静悄悄地不工作。

## 什么不算问题

**SVG 的命名空间不是链接。** `xmlns="http://www.w3.org/2000/svg"` 是一个
**标识符**，浏览器从不去取它；把它改成 https 反而会让 SVG 渲染不出来。
同理 `http://localhost` 是本机开发服务器，那里没有也不该有证书。

## 顺带检查 canonical

GitHub Pages 同时认 `/how/` 和 `/how/index.html`，带不带尾斜杠也都认，所以同一页
有好几个地址。canonical 把它们指回同一个。

这一项必须自动查，因为**新页面是从模板复制出来的**：模板里少一行，之后每一篇日志
都会静悄悄地少一行，而页面本身照样打得开、看不出任何异样。

「哪些页面该有」不在这里再列一遍——`robots.txt` 里的 `Disallow` 已经是那份清单，
生成 sitemap 的 action 读的也是它。两份清单迟早会分叉，而分叉的方向是漏掉一页。

## 顺带检查版本号

首页上扩展的版本号出现在**三处**：首屏角标、仓库表格、结构化数据里的
`softwareVersion`。发版时漏掉一处不会有任何症状——页面照常渲染，只是机器读到的
版本停在上一版，而这一处恰恰是最不会有人去看的那一处。
"""

import pathlib
import re
import sys

BASE = 'https://doubak.com'
CANONICAL = re.compile(r'<link\s+rel="canonical"\s+href="([^"]*)"')

# 少于这个数就说明上面那个 glob 或正则坏了，而不是站里真的只剩这么几页。
# 一个「扫了 0 个文件」的检查会永远是绿的。
MIN_PAGES = 25

# 首页上扩展版本号的三处写法。少一处就说明页面改过而这里没跟上。
VERSIONS = (
    re.compile(r'扩展 v(\d+\.\d+\.\d+) 已发布'),
    re.compile(r'<td class="ok">v(\d+\.\d+\.\d+)</td>'),
    re.compile(r'"softwareVersion":\s*"(\d+\.\d+\.\d+)"'),
)

LINK = re.compile(r'(?:href|src)\s*=\s*"([^"]*)"')

# 不是链接的 http://，见文件开头。
ALLOWED = (
    'http://www.w3.org/',       # XML / SVG 命名空间
    'http://localhost',         # 本机开发服务器
    'http://127.0.0.1',
)


def not_published(root: pathlib.Path) -> set[str]:
    """robots.txt 里 Disallow 的那些——它们不是页面，不该有 canonical。"""
    f = root / 'robots.txt'
    if not f.is_file():
        # 不是「那就一个都不跳过」——那样会把 404 和模板一起报成缺 canonical，
        # 真正的原因（指错了目录）反而被埋在一串假问题里。
        raise SystemExit(f'{f} 不在：这个检查要从站点根目录跑，现在指的是 {root}')
    return {m.strip() for m in re.findall(r'^Disallow:\s*(\S+)', f.read_text(encoding='utf-8'), re.M)}


def want(rel: str) -> str:
    """这一页自己的地址。index.html 用目录形式，其余保留文件名。"""
    if rel == 'index.html':
        return BASE + '/'
    if rel.endswith('/index.html'):
        return f'{BASE}/{rel[:-len("index.html")]}'
    return f'{BASE}/{rel}'


def check_canonical(root: pathlib.Path) -> int:
    skip = not_published(root)
    bad, checked = [], 0

    for p in sorted(root.rglob('*.html')):
        if '.git' in p.parts:
            continue
        rel = p.relative_to(root).as_posix()
        if '/' + rel in skip:
            continue
        checked += 1
        found = CANONICAL.findall(p.read_text(encoding='utf-8', errors='ignore'))
        if not found:
            bad.append((rel, '没有 canonical'))
        elif len(found) > 1:
            bad.append((rel, f'有 {len(found)} 条 canonical，只该有一条'))
        elif found[0] != want(rel):
            bad.append((rel, f'指向 {found[0]}，应当是 {want(rel)}'))

    print(f'canonical：查了 {checked} 页，跳过 {len(skip)} 个 robots.txt 里 Disallow 的')
    if checked < MIN_PAGES:
        print(f'  只查到 {checked} 页，少于 {MIN_PAGES} —— 是扫描本身坏了，不是站变小了')
        return 1
    if bad:
        print(f'\n有问题的 canonical {len(bad)} 条：')
        for rel, why in bad[:20]:
            print(f'  {rel}: {why}')
        return 1
    print('每一页都有 canonical，而且都指回自己。')
    return 0


def check_version(root: pathlib.Path) -> int:
    text = (root / 'index.html').read_text(encoding='utf-8')
    found = [pat.findall(text) for pat in VERSIONS]

    missing = [i for i, hits in enumerate(found) if not hits]
    if missing:
        print(f'版本号：第 {missing} 处找不到了——页面改过，这个检查没跟上')
        return 1

    seen = {h for hits in found for h in hits}
    if len(seen) != 1:
        print(f'版本号：三处对不上 —— {sorted(seen)}')
        for pat, hits in zip(VERSIONS, found):
            print(f'  {pat.pattern} → {hits}')
        return 1

    print(f'版本号：三处都是 v{seen.pop()}。')
    return 0


def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    bad = []
    counts = {'https': 0, 'relative': 0, 'other': 0}
    files = 0

    for p in root.rglob('*'):
        if p.suffix.lower() not in {'.html', '.css', '.svg', '.xml'}:
            continue
        if '.git' in p.parts:
            continue
        files += 1
        text = p.read_text(encoding='utf-8', errors='ignore')
        for url in LINK.findall(text):
            if url.startswith('https://'):
                counts['https'] += 1
            elif url.startswith('http://'):
                if url.startswith(ALLOWED):
                    counts['other'] += 1
                else:
                    bad.append((p, url, '明文 http'))
            elif url.startswith('//'):
                # 协议相对 URL 会跟着当前页面走，看起来没问题——但从本地
                # file:// 打开时它会去找一个不存在的主机。这份档案要能双击打开。
                bad.append((p, url, '协议相对'))
            elif url.startswith(('#', '/', '.')) or re.match(r'^[\w-]+[/.]', url):
                counts['relative'] += 1
            else:
                counts['other'] += 1

    print(f'扫了 {files} 个文件：https {counts["https"]} · 相对 {counts["relative"]} '
          f'· 其他 {counts["other"]}')
    if bad:
        print(f'\n有问题的链接 {len(bad)} 条：')
        for p, url, why in bad[:20]:
            print(f'  [{why}] {p}: {url}')
        check_canonical(root)
        check_version(root)
        return 1
    print('没有明文 http，也没有协议相对链接。')
    return check_canonical(root) | check_version(root)


if __name__ == '__main__':
    sys.exit(main())
