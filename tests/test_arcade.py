"""Data fixtures are test-only; preview generation reads the real saved snapshot."""

from datetime import date
import json
import re
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from arcade.barrel import Demo, DURATION, FINISH, PHASES, POSES, barrel, floor_y
from arcade.scene import render, validate_svg
from arcade.sprites import sprite_grid
from code_quest.data import validate_calendar
from test_code_quest import fixture
import generate_arcade


class ArcadeModelTests(unittest.TestCase):
    def test_all_days_partitioned_once_and_score_exact_for_sparse_empty_full(self):
        for payload in (fixture(),fixture(level=0),fixture(level=4),fixture(date(2023,12,30),371),
                        json.loads((ROOT/'assets/code-quest/calendar.json').read_text())):
            c = validate_calendar(payload)
            demo = Demo(c)
            self.assertEqual(tuple(d for s in demo.stages for d in s.days),c.days)
            self.assertEqual(demo.score(0),0)
            self.assertEqual(demo.score(FINISH),c.total)
            previous = 0
            for s in demo.stages:
                self.assertEqual(demo.score(s.collected-.00001),previous)
                previous += s.points
                self.assertEqual(demo.score(s.collected),previous)

    def test_route_uses_every_ramp_and_ladder_and_is_continuous(self):
        demo = Demo(validate_calendar(fixture()))
        for s in demo.stages:
            for t in (s.begin,s.end):
                x,y = demo.position(t)
                self.assertAlmostEqual(y,floor_y(s.floor,x))
            if s.floor < 4:
                x,y = demo.position(s.end+.75)
                self.assertEqual(x,s.right)
                self.assertAlmostEqual(y,(floor_y(s.floor,x)+floor_y(s.floor+1,x))/2)
        for i in range(1,32001):
            t = i/1000
            a,b = demo.position(t-.001),demo.position(t)
            self.assertLess(abs(a[0]-b[0]),.15)
            self.assertLess(abs(a[1]-b[1]),.2)

    def test_poses_jumps_and_hidden_loop(self):
        demo = Demo(validate_calendar(fixture()))
        poses = {demo.pose(i/100) for i in range(3201)}
        self.assertEqual(poses,set(POSES))
        self.assertGreater(len(demo.jumps),0)
        for begin,end,floor in demo.jumps:
            self.assertGreater(begin,demo.stages[floor].begin)
            self.assertLess(end,demo.stages[floor].end)
            for t in (begin,end):
                x,y = demo.position(t)
                self.assertAlmostEqual(y,floor_y(floor,x))
            t = (begin+end)/2
            x,y=demo.position(t)
            self.assertAlmostEqual(floor_y(floor,x)-y,28)
        self.assertEqual(demo.position(0),demo.position(DURATION % DURATION))

    def test_runner_clears_barrels_and_overhead_platforms(self):
        demo=Demo(validate_calendar(fixture()))
        for i in range(6401):
            t=i/200
            x,y=demo.position(t)
            _,_,floor,climbing=demo.ground_position(t)
            # Conservative box around the full original 32x40 sprite.
            for phase in PHASES:
                bx,by,visible,_=barrel(t,phase)
                if visible and abs(x-bx)<25:
                    self.assertTrue(y<=by-9+.05 or y-40>=by+9-.05,(t,phase,x,y,bx,by))
            if not climbing and floor<4 and 180<x<740:
                self.assertGreaterEqual(y-40,floor_y(floor+1,x)+10-.05,(t,x,y,floor))

    def test_barrels_follow_downhill_ramps_then_drop(self):
        for phase in PHASES:
            last=None
            for i in range(3201):
                x,y,visible,floor=barrel(i/100,phase)
                if visible and floor is not None:
                    self.assertAlmostEqual(y+9,floor_y(floor,x))
                    if last and last[2]==floor:
                        self.assertGreaterEqual(y+.001,last[1])
                last=(x,y,floor) if visible else None

    def test_original_sprite_dimensions_and_distinct_gaits(self):
        for pose in POSES:
            grid=sprite_grid(pose)
            self.assertEqual(len(grid),20)
            self.assertTrue(all(len(row)==16 for row in grid))
        for prefix,count in (('walk',2),('run',4),('climb',2)):
            self.assertEqual(len({str(sprite_grid(f'{prefix}{i}')) for i in range(count)}),count)


class ArcadeRenderTests(unittest.TestCase):
    def test_cinematic_fade_has_no_competing_animation_on_same_element(self):
        svg=render(validate_calendar(fixture()))
        animated=set(re.findall(r'\.([a-zA-Z0-9_-]+)\{animation:',svg))
        for element in ET.fromstring(svg).iter():
            animations=set(element.get('class','').split()) & animated
            self.assertLessEqual(len(animations),1,(element.get('class'),animations))

    def test_xml_reproducibility_budget_and_no_duplicate_calendar(self):
        for payload in (fixture(),fixture(level=0),fixture(date(2023,12,30),371,4)):
            c=validate_calendar(payload)
            for static in (False,True):
                svg=render(c,static=static)
                validate_svg(svg,c)
                self.assertEqual(svg,render(c,static=static))
                self.assertLess(len(svg.encode()),250_000)
                root=ET.fromstring(svg)
                self.assertEqual(len([e for e in root.iter() if e.get('data-stage') is not None]),5)
                self.assertFalse(any(e.get('data-date') for e in root.iter()))
                self.assertEqual(len([e for e in root.iter() if e.get('data-ladder') is not None]),4)
                if static:
                    self.assertNotIn('@keyframes',svg)
                    self.assertNotIn('animation:',svg)
                else:
                    self.assertIn('prefers-reduced-motion:reduce',svg)
                    self.assertIn('0%,100%{opacity:0}',svg)

    def test_reject_scripts_external_resources_and_data_tampering(self):
        c=validate_calendar(fixture())
        svg=render(c)
        for extra in ('<script/>','<foreignObject/>','<image href="data:image/png;base64,a"/>',
                      '<use href="https://example.org/x"/>','<use href="#missing"/>',
                      '<rect onload="alert(1)"/>','<style>@import "bad.css";</style>',
                      '<rect style="fill:red"/>','<g id="title"/>'):
            with self.subTest(extra=extra),self.assertRaises(ValueError):
                validate_svg(svg.replace('</svg>',extra+'</svg>'),c)
        for bad in (svg.replace('data-points="','data-points="1',1),
                    svg.replace('&quot;total&quot;:','&quot;total&quot;: 1, &quot;wrong&quot;:',1)):
            with self.assertRaises(ValueError): validate_svg(bad,c)

    def test_offline_cli_idempotence_and_failed_input_preserves_outputs(self):
        real=ROOT/'assets/code-quest/calendar.json'
        before=real.read_bytes()
        with TemporaryDirectory() as folder:
            output=Path(folder)/'arcade'
            with patch.object(generate_arcade,'ASSETS',output),patch.object(sys,'argv',['generate_arcade.py']):
                generate_arcade.main()
                stamps={p.name:p.stat().st_mtime_ns for p in output.iterdir()}
                generate_arcade.main()
                self.assertEqual(stamps,{p.name:p.stat().st_mtime_ns for p in output.iterdir()})
                with patch.object(sys,'argv',['generate_arcade.py','--check']):
                    generate_arcade.main()
                bad=Path(folder)/'invalid.json'
                bad.write_text('{"source":"synthetic"}')
                with patch.object(generate_arcade,'CALENDAR',bad),self.assertRaises(ValueError):
                    generate_arcade.main()
                self.assertEqual(stamps,{p.name:p.stat().st_mtime_ns for p in output.iterdir()})
        self.assertEqual(real.read_bytes(),before)

    def test_readme_static_fallback_and_shared_workflow(self):
        readme=(ROOT/'README.md').read_text(encoding='utf-8')
        self.assertIn('media="(prefers-reduced-motion: reduce)" srcset="assets/arcade/barrel-quest-static.svg"',readme)
        workflow=(ROOT/'.github/workflows/update-code-quest.yml').read_text()
        self.assertEqual(workflow.count('run: python scripts/generate_code_quest.py\n'),1)
        self.assertIn('run: python scripts/generate_arcade.py\n',workflow)
        self.assertIn('assets/arcade/barrel-quest-static.svg',workflow)


if __name__=='__main__':
    unittest.main()
