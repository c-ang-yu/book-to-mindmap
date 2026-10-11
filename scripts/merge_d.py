# -*- coding: utf-8 -*-
"""把 {"path": "新d全文", ...} 合并回思维导图 HTML 的 const T=[...] 数据行。

用法：
    python merge_d.py <html_path> <updates.json>

updates.json 示例：
    {"1.1.2.0": "12世纪的经院学者……\\n\\n——摘自《西方哲学史（下册）》"}

安全机制：
    1. 出现未知 path 立即中止，不写盘
    2. 回写后重新 json.loads 校验节点总数，变化即报错退出
"""
import io
import json
import sys


def parse_span(s):
    """稳健定位 const T 数据行区间：逐个候选尝试解析，成功才返回 (a,b)。"""
    pos = 0
    while True:
        i = s.find("const T=[", pos)
        if i < 0:
            raise ValueError("const T data line not found")
        a = i + len("const T=")
        b = s.index("];", a) + 1
        try:
            json.loads(s[a:b])
            return a, b
        except Exception:
            pos = i + 1


def count_nodes(T):
    n = 0

    def rec(o):
        nonlocal n
        if isinstance(o, dict):
            n += 1
            for c in (o.get("ch") or []):
                rec(c)
        elif isinstance(o, list):
            for c in o:
                rec(c)

    rec(T)
    return n


def index_by_path(T):
    by_path = {}

    def walk_list(lst, prefix):
        for i, c in enumerate(lst):
            walk_node(c, prefix + str(i))

    def walk_node(o, path):
        by_path[path] = o
        ch = o.get("ch") or []
        for i, c in enumerate(ch):
            walk_node(c, path + "." + str(i))

    walk_list(T, "")
    return by_path


def main(html_path, updates_path):
    ups = json.load(io.open(updates_path, encoding="utf-8-sig"))
    s = io.open(html_path, encoding="utf-8").read()
    a, b = parse_span(s)
    T = json.loads(s[a:b])
    total0 = count_nodes(T)

    by_path = index_by_path(T)
    missing = [p for p in ups if p not in by_path]
    if missing:
        print("ABORT unknown paths:", missing)
        sys.exit(1)

    for p, d in ups.items():
        by_path[p]["d"] = d

    new_line = json.dumps(T, ensure_ascii=False, separators=(",", ":"))
    io.open(html_path, "w", encoding="utf-8", newline="").write(s[:a] + new_line + s[b:])

    # 回读复检
    s2 = io.open(html_path, encoding="utf-8").read()
    a2, b2 = parse_span(s2)
    T2 = json.loads(s2[a2:b2])
    total1 = count_nodes(T2)
    if total1 != total0:
        print("ABORT node count changed:", total0, "->", total1)
        sys.exit(2)
    print("merged", len(ups), "updates | nodes", total1, "(unchanged) | size",
          len(s2.encode("utf-8")))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
