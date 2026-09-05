#!/usr/bin/env python3
"""Locate the line number of a counter-numbered tcb theorem inside a 408 subject.

Usage: locate.py <subject> <type> <section> <index>
  subject : ds | co | os | cn     (which 408 part)
  type    : def | formula | concl | attention | example
            (def=mydef, formula=formula, concl=conclusion)
  section : section number within that part (1-based, increments across chapter files)
  index   : k-th box of that type within the section (1-based)
Prints: <file>:<line>  <title>
"""
import sys, re, glob, os

def build(subject):
    # walk chapter files in driver order
    files = []
    for f in sorted(glob.glob(f'408/{subject}/chap*.tex')):
        files.append(f)
    return files

def main():
    subject, typ, sec, idx = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    type_map = {'def': 'mydef', 'formula': 'formula', 'concl': 'conclusion',
                'attention': 'attention', 'example': 'examplebox'}
    env = type_map[typ]
    sec_num = 0
    # per-type counters within current section
    counters = {}
    results = []
    for f in build(subject):
        txt = open(f, encoding='utf-8', errors='replace').read()
        lines = txt.split('\n')
        for i, line in enumerate(lines):
            m = re.match(r'\s*\\section\b', line)
            if m:
                sec_num += 1
                counters = {}
            m = re.match(r'\s*\\begin\{(%s)\}\{([^}]*)\}' % env, line)
            if m and sec_num == sec:
                counters[env] = counters.get(env, 0) + 1
                if counters[env] == idx:
                    results.append((f, i + 1, m.group(2), sec_num))
    if not results:
        print(f"NOT FOUND {subject} {env} sec={sec} idx={idx} (section count reached {sec_num})")
        sys.exit(1)
    for f, ln, title, s in results:
        print(f"{f}:{ln}  [sec {s}] {title}")

if __name__ == '__main__':
    main()
