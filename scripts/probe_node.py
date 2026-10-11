# -*- coding: utf-8 -*-
"""思维导图数据完整性体检。

用法：
    python probe_node.py <html_path> [关键词]

输出：
    1. 节点总数 / 末端节点数 / 末端含 d 数
    2. 末端无 d 的节点清单（era/school/person 无 d 属正常；detail/idea/note/lineage 无 d = 漏做）
    3. 若给关键词：打印节点名含关键词的节点（path/类型/d长度/子节点数/d开头）
"""
import io
import json
import sys

SHOULD_HAVE_D = ("detail", "lineage", "note", "idea")


def parse_T(s):
    """稳健定位 const T 数据行：逐个候选尝试解析，第一个能解析成 JSON 的即数据行。"""
    pos = 0
    while True:
        i = s.find("const T=[", pos)
        if i < 0:
            raise ValueError("const T data line not found")
        a = i + len("const T=")
        b = s.index("];", a) + 1
        try:
            return json.loads(s[a:b])
        except Exception:
            pos = i + 1


def main(html_path, kw=None):
    s = io.open(html_path, encoding="utf-8-sig").read()
    T = parse_T(s)

    nodes = [0]
    term = [0]
    term_with_d = [0]
    term_no_d = []
    hits = []

    def walk(o, path):
        if isinstance(o, dict):
            nodes[0] += 1
            n = o.get("n") or ""
            d = o.get("d") or ""
            ch = o.get("ch") or []
            if not ch:
                term[0] += 1
                if d:
                    term_with_d[0] += 1
                else:
                    term_no_d.append((path, o.get("t"), n))
            if kw and kw in n:
                hits.append((path, o.get("t"), n, len(d), len(ch), d[:40].replace("\n", "|")))
            for i, c in enumerate(ch):
                walk(c, path + "." + str(i))
        elif isinstance(o, list):
            for i, c in enumerate(o):
                walk(c, str(i))

    walk(T, "")
    print("nodes:", nodes[0], "| terminal:", term[0], "| terminal with d:", term_with_d[0])

    missing = [x for x in term_no_d if x[1] in SHOULD_HAVE_D]
    if missing:
        print("!! 末端应有 d 但缺失", len(missing), "个：")
        for x in missing[:20]:
            print("   ", x)
    else:
        print("detail/idea/note/lineage 末端 d 覆盖率 100%")

    if kw:
        for h in hits:
            print("HIT", h)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
