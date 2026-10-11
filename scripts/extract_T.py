# -*- coding: utf-8 -*-
"""从思维导图 HTML 提取 const T=[...] 数据行。

用法：
    python extract_T.py <html_path> <out_dir>

输出：
    T.json        全树（可直接编辑后交回 merge 的旁路用法）
    T_paths.json  扁平清单 [{path,t,n,d,dlen,terminal,nch}, ...]，用于切分摘录任务

数据行格式约定：单行、双引号 JSON 风格、段内换行为字面 \\n 转义。
"""
import io
import json
import os
import sys


def parse_T(s):
    """稳健定位 const T 数据行：页面说明文字里也可能出现同名字样，
    逐个候选尝试解析，第一个能解析成 JSON 的即数据行。"""
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


def extract(html_path):
    s = io.open(html_path, encoding="utf-8-sig").read()
    return parse_T(s)


def main(html_path, out_dir):
    T = extract(html_path)
    flat = []

    def walk(o, path):
        if isinstance(o, dict):
            ch = o.get("ch") or []
            d = o.get("d") or ""
            flat.append({
                "path": path,
                "t": o.get("t"),
                "n": o.get("n"),
                "d": d,
                "dlen": len(d),
                "terminal": not ch,
                "nch": len(ch),
            })
            for i, c in enumerate(ch):
                walk(c, path + "." + str(i))
        elif isinstance(o, list):
            for i, c in enumerate(o):
                walk(c, str(i))

    walk(T, "")
    os.makedirs(out_dir, exist_ok=True)
    p1 = os.path.join(out_dir, "T.json")
    p2 = os.path.join(out_dir, "T_paths.json")
    json.dump(T, io.open(p1, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(flat, io.open(p2, "w", encoding="utf-8"), ensure_ascii=False)
    terms = sum(1 for f in flat if f["terminal"])
    with_d = sum(1 for f in flat if f["terminal"] and f["dlen"] > 0)
    print("nodes:", len(flat), "| terminal:", terms, "| terminal with d:", with_d)
    print("tree ->", p1)
    print("flat ->", p2)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
