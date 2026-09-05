#!/usr/bin/env python3
"""Locate a counter-numbered tcb theorem inside the MATH book.

Usage: locate_math.py <part> <type> <section> <index>
  part    : I | II | III      (I=calculus, II=algebra, III=probality)
  type    : def | formula | concl
  section : section number within that part (resets per part)
  index   : k-th box of that type within the section (1-based)
Prints: <file>:<line>  <title>
"""
import sys, re, glob

DRIVERS = {
    'I': ('calculus', ['math/calculus/chap1.tex','math/calculus/chap2.tex','math/calculus/chap3.tex',
                       'math/calculus/chap4.tex','math/calculus/chap5.tex','math/calculus/chap6.tex',
                       'math/calculus/chap7.tex','math/calculus/chap8.tex','math/calculus/chap9.tex']),
    'II': ('algebra', ['math/algebra/chap1.tex','math/algebra/chap2.tex','math/algebra/chap3.tex',
                       'math/algebra/chap4.tex','math/algebra/chap5.tex','math/algebra/chap6.tex',
                       'math/algebra/chap7.tex']),
    'III': ('probality', ['math/probality/chap1.tex','math/probality/chap2.tex','math/probality/chap3.tex',
                          'math/probality/chap4.tex','math/probality/chap5.tex','math/probality/chap6.tex',
                          'math/probality/chap7.tex']),
}
TYPE = {'def': 'mydef', 'formula': 'formula', 'concl': 'conclusion'}

def main():
    part, typ, sec, idx = sys.argv[1].upper(), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    env = TYPE[typ]
    _, files = DRIVERS[part]
    sec_num = 0
    counters = {}
    for f in files:
        lines = open(f, encoding='utf-8', errors='replace').read().split('\n')
        for i, line in enumerate(lines):
            if re.match(r'\s*\\section\b', line):
                sec_num += 1
                counters = {}
            m = re.match(r'\s*\\begin\{(%s)\}\{([^}]*)\}' % env, line)
            if m and sec_num == sec:
                counters[env] = counters.get(env, 0) + 1
                if counters[env] == idx:
                    print(f"{f}:{i+1}  [sec {sec}] {m.group(2)}")
                    return
    print(f"NOT FOUND part {part} {env} sec={sec} idx={idx} (sec reached {sec_num})")
    sys.exit(1)

if __name__ == '__main__':
    main()
