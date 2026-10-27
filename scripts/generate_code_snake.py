# SPDX-License-Identifier: MIT
# Copyright (c) 2026 PedroCostinha
"""Generate only Code Snake SVGs, offline, from the existing calendar."""
import argparse
import json
from pathlib import Path
from code_quest.data import validate_calendar
from generate_code_quest import write_if_changed
from code_snake.scene import render

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    calendar=validate_calendar(json.loads((ROOT/'assets/code-quest/calendar.json').read_text(encoding='utf-8')))
    outputs={ROOT/'assets/code-snake'/f'code-snake{"-static" if static else ""}{"-mobile" if mobile else ""}.svg':render(calendar,static=static,mobile=mobile) for static in (False,True) for mobile in (False,True)}
    for path,svg in outputs.items():
        if args.check:
            if path.read_text(encoding='utf-8')!=svg:
                raise ValueError(f'Non-reproducible output: {path.name}')
        else:
            write_if_changed(path,svg)
        print(f'{path.name}: {len(svg.encode())} bytes')

if __name__=='__main__':
    main()
