# SPDX-License-Identifier: MIT
import json
from pathlib import Path
import socket
import sys
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from code_quest.data import validate_calendar
from code_snake.model import replay
from code_snake.scene import render, validate_svg
from code_snake.art import HEAD
import generate_code_snake
import generate_code_quest
import generate_arcade
from test_code_quest import fixture

class CodeSnakeTests(unittest.TestCase):
    def test_shared_pipeline_single_fetch_updates_only_nine_artifacts_and_is_idempotent(self):
        # Exercise the daily sequence with test-only calendars and no real network.
        allowed = {
            'assets/code-quest/calendar.json', 'assets/code-quest/code-quest.svg',
            'assets/code-quest/code-quest-static.svg', 'assets/arcade/barrel-quest.svg',
            'assets/arcade/barrel-quest-static.svg',
            *{f'assets/code-snake/code-snake{static}{mobile}.svg'
              for static in ('', '-static') for mobile in ('', '-mobile')},
        }
        with TemporaryDirectory() as temp:
            root = Path(temp)
            sentinel = root/'README.md'
            sentinel.write_text('must survive unchanged')
            def snapshot():
                return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                        for p in root.rglob('*') if p.is_file()}
            with patch.object(generate_code_quest, 'ASSETS', root/'assets/code-quest'), \
                 patch.object(generate_arcade, 'CALENDAR', root/'assets/code-quest/calendar.json'), \
                 patch.object(generate_arcade, 'ASSETS', root/'assets/arcade'), \
                 patch.object(generate_code_snake, 'ROOT', root), \
                 patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
                for payload in (fixture(level=4), fixture(level=0)):
                    with patch.object(generate_code_quest, 'fetch_calendar', return_value=payload) as fetch:
                        with patch.object(sys, 'argv', ['generator']):
                            generate_code_quest.main()
                            generate_arcade.main()
                            generate_code_snake.main()
                        fetch.assert_called_once()
                    before = snapshot()
                    self.assertEqual(set(before), allowed | {'README.md'})
                    self.assertEqual(sentinel.read_text(), 'must survive unchanged')
                    with patch.object(sys, 'argv', ['generator', '--check']):
                        generate_code_quest.main()
                        generate_arcade.main()
                        generate_code_snake.main()
                    with patch.object(generate_code_quest, 'fetch_calendar', return_value=payload), \
                         patch.object(sys, 'argv', ['generator']):
                        generate_code_quest.main()
                        generate_arcade.main()
                        generate_code_snake.main()
                    self.assertEqual(before, snapshot(), 'Identical data preserves bytes and mtimes')
                with patch.object(generate_code_quest, 'fetch_calendar', return_value={}), \
                     patch.object(sys, 'argv', ['generator']):
                    with self.assertRaises(ValueError):
                        generate_code_quest.main()
                self.assertEqual(before, snapshot(), 'Failed update preserves all prior artifacts')

    def calendars(self):
        return [validate_calendar(p) for p in (fixture(level=0),fixture(level=4),fixture(),json.loads((ROOT/'assets/code-quest/calendar.json').read_text()))]

    def test_route_is_orthogonal_unique_and_body_cannot_collide(self):
        for c in self.calendars():
            for mobile in (False,True):
                d=replay(c,mobile)
                self.assertEqual(len(set(d.route)),len(d.route))
                for a,b in zip(d.route,d.route[1:]):
                    self.assertEqual(abs(a[0]-b[0])+abs(a[1]-b[1]),1)
                for i in range(len(d.route)):
                    body=d.route[max(0,i-d.length(i)+1):i+1]
                    self.assertEqual(len(body),len(set(body)))
                self.assertTrue(all(0<=x<d.columns and 0<=y<7 for x,y in d.route))

    def test_items_score_growth_and_zero_calendar(self):
        for c in self.calendars():
            for mobile in (False,True):
                d=replay(c,mobile)
                for i,day in d.items:
                    self.assertIn(day,c.days)
                    self.assertEqual(d.route[i],(day.week-d.offset,day.weekday))
                    self.assertGreater(day.count,0)
                    self.assertEqual(d.score(i)-d.score(i-1),day.count)
                    self.assertEqual(d.length(i)-d.length(i-1),1)
                self.assertLessEqual(d.score(len(d.route)),c.total)
                if not c.total:
                    self.assertEqual(d.items,())

    def test_offline_determinism_all_dates_and_static(self):
        with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
            for c in self.calendars():
                for mobile in (False,True):
                    for static in (False,True):
                        svg=render(c,static=static,mobile=mobile)
                        self.assertEqual(svg,render(c,static=static,mobile=mobile))
                        validate_svg(svg,c,static=static)
                        root=ET.fromstring(svg)
                        ids={e.get('id') for e in root.iter() if e.get('id')}
                        for e in root.iter():
                            if e.get('href'):
                                self.assertIn(e.get('href')[1:],ids)
                        if not static:
                            self.assertIn('prefers-reduced-motion:reduce',svg)

    def test_sprite_and_malicious_svg(self):
        self.assertEqual(len(HEAD),12)
        self.assertTrue(all(len(row)==12 for row in HEAD))
        c=self.calendars()[-1]
        for bad in ('<script/>','<image href="https://example.com"/>','<g onclick="bad()"/>'):
            with self.assertRaises(ValueError):
                validate_svg(render(c).replace('</svg>',bad+'</svg>'),c)

    def test_cli_idempotence_check_and_failed_input_preserve_outputs(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            calendar=root/'assets/code-quest/calendar.json'
            calendar.parent.mkdir(parents=True)
            calendar.write_bytes((ROOT/'assets/code-quest/calendar.json').read_bytes())
            with patch.object(generate_code_snake,'ROOT',root),patch.object(sys,'argv',['generate_code_snake.py']):
                generate_code_snake.main()
                files=list((root/'assets/code-snake').glob('*.svg'))
                before={p:(p.read_bytes(),p.stat().st_mtime_ns) for p in files}
                generate_code_snake.main()
                self.assertEqual(before,{p:(p.read_bytes(),p.stat().st_mtime_ns) for p in files})
                with patch.object(sys,'argv',['generate_code_snake.py','--check']):
                    generate_code_snake.main()
                calendar.write_text('{}')
                with self.assertRaises(ValueError):
                    generate_code_snake.main()
                self.assertEqual(before,{p:(p.read_bytes(),p.stat().st_mtime_ns) for p in files})
