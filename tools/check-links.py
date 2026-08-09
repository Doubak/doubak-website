#!/usr/bin/env python3
"""检查站内所有链接的协议。

    python3 tools/check-links.py [目录]

## 为什么要有这个

一条 `http://` 的外链，在 https 的页面上会被浏览器**当作混合内容拦掉或降级**，
而它长得和正常链接一模一样——不点开根本看不出来。这类问题不会报错，
只会让某个链接静悄悄地不工作。

## 什么不算问题

**SVG 的命名空间不是链接。** `xmlns="http://www.w3.org/2000/svg"` 是一个
**标识符**，浏览器从不去取它；把它改成 https 反而会让 SVG 渲染不出来。
同理 `http://localhost` 是本机开发服务器，那里没有也不该有证书。
"""

import pathlib
import re
import sys

LINK = re.compile(r'(?:href|src)\s*=\s*"([^"]*)"')

# 不是链接的 http://，见文件开头。
ALLOWED = (
    'http://www.w3.org/',       # XML / SVG 命名空间
    'http://localhost',         # 本机开发服务器
    'http://127.0.0.1',
)


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
        return 1
    print('没有明文 http，也没有协议相对链接。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
