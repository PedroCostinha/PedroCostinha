"""Generate CODE QUEST from GitHub GraphQL, or explicitly replay its saved calendar."""

import argparse
import json
import os
from pathlib import Path
import sys

from code_quest.data import fetch_calendar, validate_calendar
from code_quest.scene import render, render_static, validate_svg

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets' / 'code-quest'


def write_if_changed(path, content):
    data = content.encode('utf-8')
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--calendar', type=Path, help='Explicitly replay a saved real calendar, without a network request')
    parser.add_argument('--check', action='store_true', help='Validate committed SVG and its saved calendar')
    args = parser.parse_args()
    if args.check:
        payload = json.loads((ASSETS / 'calendar.json').read_text(encoding='utf-8'))
        calendar = validate_calendar(payload)
        svg = (ASSETS / 'code-quest.svg').read_text(encoding='utf-8')
        validate_svg(svg, calendar)
        if svg != render(calendar):
            raise ValueError('Saved SVG is not reproducible from the saved calendar')
        static = (ASSETS / 'code-quest-static.svg').read_text(encoding='utf-8')
        validate_svg(static, calendar)
        if static != render_static(calendar):
            raise ValueError('Static SVG is not reproducible from the saved calendar')
        print(f'Valid: {len(calendar.days)} days, {calendar.weeks} weeks, {calendar.total} contributions, {len(svg.encode())} bytes')
        return
    payload = json.loads(args.calendar.read_text(encoding='utf-8')) if args.calendar else fetch_calendar(os.environ.get('GITHUB_TOKEN'))
    calendar = validate_calendar(payload)
    svg = render(calendar)
    static = render_static(calendar)
    # Fetch, validate and render everything before replacing any output.
    saved = json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n'
    changed = write_if_changed(ASSETS / 'code-quest.svg', svg)
    changed |= write_if_changed(ASSETS / 'code-quest-static.svg', static)
    changed |= write_if_changed(ASSETS / 'calendar.json', saved)
    print(f'{"Updated" if changed else "Unchanged"}: {calendar.total} real contributions, source={calendar.source}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(f'CODE QUEST: {exc}', file=sys.stderr)
        sys.exit(1)
