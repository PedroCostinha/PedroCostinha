"""Generate original arcade SVGs from the single saved CODE QUEST calendar, offline."""

import argparse
import json
from pathlib import Path
import sys

from arcade.scene import render, validate_svg
from code_quest.data import validate_calendar
from generate_code_quest import write_if_changed

ROOT = Path(__file__).resolve().parents[1]
CALENDAR = ROOT / 'assets/code-quest/calendar.json'
ASSETS = ROOT / 'assets/arcade'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate saved SVGs and exact reproducibility')
    args = parser.parse_args()
    calendar = validate_calendar(json.loads(CALENDAR.read_text(encoding='utf-8')))
    # Validate/render both before writing either. Never fetch, modify or copy the calendar.
    outputs = {ASSETS/'barrel-quest.svg': render(calendar),
               ASSETS/'barrel-quest-static.svg': render(calendar,static=True)}
    changed = False
    for path,svg in outputs.items():
        if args.check:
            saved = path.read_text(encoding='utf-8')
            validate_svg(saved,calendar)
            if saved != svg:
                raise ValueError(f'{path.name} is not reproducible from the saved calendar')
        else:
            changed |= write_if_changed(path,svg)
    print(f'{"Valid" if args.check else "Updated" if changed else "Unchanged"}: Barrel Quest; '
          f'{len(calendar.days)} real days; {calendar.total} points; '
          + ', '.join(f'{p.name}={len(s.encode())} bytes' for p,s in outputs.items()))


if __name__ == '__main__':
    try:
        main()
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print(f'ARCADE: {exc}',file=sys.stderr)
        sys.exit(1)
