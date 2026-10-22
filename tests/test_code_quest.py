"""Synthetic inputs exist only in tests. Production always requests real GitHub data."""

from datetime import date, timedelta
from io import BytesIO
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from code_quest.data import fetch_calendar, normalize_graphql, validate_calendar, LEVELS
from code_quest.motion import DURATION, FINISH, START, Route
from code_quest.scene import render, validate_svg
from generate_code_quest import write_if_changed
import generate_code_quest


def fixture(first=date(2025, 10, 19), length=369, level=None):
    days = []
    for i in range(length):
        value = (i // 7) % 5 if level is None else level
        days.append(dict(date=str(first + timedelta(days=i)), count=value * 2, level=value))
    return dict(login='PedroCostinha', source='github-graphql', days=days, total=sum(d['count'] for d in days))


def api_response(payload):
    calendar = validate_calendar(payload)
    weeks = [[] for _ in range(calendar.weeks)]
    for day in calendar.days:
        weeks[day.week].append(dict(date=str(day.date), weekday=day.weekday,
                                    contributionCount=day.count, contributionLevel=LEVELS[day.level]))
    return dict(data=dict(user=dict(contributionsCollection=dict(contributionCalendar=dict(
        totalContributions=calendar.total, weeks=[dict(contributionDays=w) for w in weeks])))))


class CalendarTests(unittest.TestCase):
    def test_52_53_54_weeks_and_partial_weeks(self):
        for first, length, weeks in [(date(2025, 1, 5), 364, 52), (date(2025, 1, 6), 365, 53),
                                     (date(2023, 12, 30), 371, 54)]:
            with self.subTest(weeks=weeks):
                result = validate_calendar(fixture(first, length))
                self.assertEqual(result.weeks, weeks)
                self.assertEqual(result.days[0].weekday, (first.weekday()+1) % 7)
                self.assertEqual(len(result.days), length)

    def test_real_saved_calendar(self):
        payload = json.loads((Path(__file__).parents[1] / 'assets/code-quest/calendar.json').read_text())
        calendar = validate_calendar(payload)
        self.assertEqual(calendar.total, sum(d.count for d in calendar.days))
        self.assertIn(calendar.source, ('github-graphql', 'github-public-calendar'))

    def test_reject_missing_duplicates_disorder_negative_false_totals(self):
        for mutation in ('missing', 'duplicate', 'reverse', 'negative', 'total', 'level', 'fake-source', 'wrong-user'):
            p = fixture()
            if mutation == 'missing': p['days'].pop(10)
            if mutation == 'duplicate': p['days'][10] = p['days'][9]
            if mutation == 'reverse': p['days'].reverse()
            if mutation == 'negative': p['days'][10]['count'] = -1
            if mutation == 'total': p['total'] += 1
            if mutation == 'level': p['days'][0]['level'] = 4
            if mutation == 'fake-source': p['source'] = 'synthetic'
            if mutation == 'wrong-user': p['login'] = 'someone-else'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): validate_calendar(p)

    def test_graphql_round_trip(self):
        p = fixture()
        self.assertEqual(normalize_graphql(api_response(p)), p)

    def test_invalid_api_responses(self):
        for p in (None, [], {}, {'errors':[{'message':'denied'}]}, {'data':{'user':None}}):
            with self.subTest(p=p), self.assertRaises(ValueError): normalize_graphql(p)
        p = api_response(fixture())
        p['data']['user']['contributionsCollection']['contributionCalendar']['weeks'][0]['contributionDays'][0]['weekday'] = 6
        with self.assertRaises(ValueError): normalize_graphql(p)


class NetworkTests(unittest.TestCase):
    def test_no_token_no_request_or_fallback(self):
        opener = Mock()
        with self.assertRaises(ValueError): fetch_calendar(None, opener=opener)
        opener.assert_not_called()

    def test_transient_network_and_rate_limit_retry(self):
        result = json.dumps(api_response(fixture())).encode()
        for failure in (URLError('offline'), HTTPError('url', 429, 'limited', {'Retry-After':'1'}, None),
                        HTTPError('url', 503, 'unavailable', {}, None)):
            opener = Mock(side_effect=[failure, BytesIO(result)])
            sleep = Mock()
            self.assertEqual(fetch_calendar('test-only', opener=opener, sleep=sleep)['source'], 'github-graphql')
            self.assertEqual(opener.call_count, 2)
            sleep.assert_called_once()

    def test_auth_failure_does_not_retry(self):
        opener = Mock(side_effect=HTTPError('url', 401, 'denied', {}, None))
        with self.assertRaises(ValueError): fetch_calendar('test-only', opener=opener, sleep=Mock())
        self.assertEqual(opener.call_count, 1)

    def test_exhaustion_does_not_return_empty_calendar(self):
        opener = Mock(side_effect=URLError('offline'))
        with self.assertRaises(ValueError): fetch_calendar('test-only', opener=opener, sleep=Mock())
        self.assertEqual(opener.call_count, 4)

    def test_graphql_rate_limit_and_errors(self):
        opener = Mock(side_effect=[BytesIO(b'{"errors":[{"type":"RATE_LIMITED"}]}'),
                                   BytesIO(json.dumps(api_response(fixture())).encode())])
        self.assertEqual(fetch_calendar('test-only', opener=opener, sleep=Mock())['source'], 'github-graphql')

    def test_null_api_response_is_rejected(self):
        with self.assertRaises(ValueError):
            fetch_calendar('test-only', opener=Mock(return_value=BytesIO(b'null')), sleep=Mock())


class MotionTests(unittest.TestCase):
    def test_no_body_intersects_any_platform(self):
        for p in (fixture(), fixture(level=0), fixture(level=4), fixture(date(2023,12,30),371)):
            route = Route(validate_calendar(p))
            previous_x = -1
            for i in range(4001):
                t = START + (FINISH-START) * i / 4000
                x, y = route.position(t)
                self.assertGreaterEqual(x, previous_x)
                previous_x = x
                for platform in route.platforms:
                    if x + 12 > platform.x and x - 12 < platform.end:
                        self.assertLessEqual(y, platform.y + .02, (t,x,y,platform))

    def test_continuous_jump_endpoints(self):
        route = Route(validate_calendar(fixture()))
        for jump in route.jumps:
            self.assertAlmostEqual(jump.feet(jump.x), jump.y)
            self.assertAlmostEqual(jump.feet(jump.end), jump.end_y)
            self.assertLess(jump.feet((jump.x+jump.end)/2), min(jump.y,jump.end_y))

    def test_coin_collection_matches_character_and_real_activity(self):
        route = Route(validate_calendar(fixture()))
        for coin in route.coins:
            x,y = route.position(coin.collected)
            self.assertAlmostEqual(x, coin.x)
            self.assertTrue(y-40 <= coin.y <= y)
            self.assertTrue(any(p.x <= x <= p.end and p.level >= 3 for p in route.platforms))
        self.assertEqual(Route(validate_calendar(fixture(level=0))).coins, [])

    def test_all_animation_states_and_loop_fade(self):
        route = Route(validate_calendar(fixture()))
        poses = {route.pose(i/100) for i in range(2080)}
        self.assertTrue({'idle','jump','fall','land','collect','celebrate','run0','run1','run2','run3'} <= poses)
        self.assertEqual(route.position(0), route.position(DURATION % DURATION))
        self.assertEqual(route.position(FINISH)[0], route.right)


class RenderTests(unittest.TestCase):
    def test_xml_data_references_budget_and_reproducibility(self):
        c = validate_calendar(fixture())
        svg = render(c)
        validate_svg(svg, c)
        self.assertEqual(svg, render(c))
        self.assertLess(len(svg.encode()), 250_000)
        self.assertIn('prefers-reduced-motion:reduce', svg)
        self.assertIn('0%,100%{opacity:0}', svg)
        self.assertEqual(len([e for e in ET.fromstring(svg).iter() if e.get('data-date')]),len(c.days))

    def test_reject_external_references_and_scripts(self):
        svg = render(validate_calendar(fixture()))
        for extra in ('<script/>', '<foreignObject/>', '<use href="https://example.com/a.svg"/>', '<use href="#missing"/>'):
            with self.subTest(extra=extra), self.assertRaises(ValueError): validate_svg(svg.replace('</svg>',extra+'</svg>'))

    def test_write_only_when_content_changes(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)/'test.svg'
            self.assertTrue(write_if_changed(path,'one'))
            stamp = path.stat().st_mtime_ns
            self.assertFalse(write_if_changed(path,'one'))
            self.assertEqual(stamp,path.stat().st_mtime_ns)
            self.assertTrue(write_if_changed(path,'two'))

    def test_failed_fetch_preserves_existing_files(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'code-quest.svg').write_text('previous SVG')
            (root/'calendar.json').write_text('previous calendar')
            with patch.object(generate_code_quest, 'ASSETS', root), patch.object(sys, 'argv', ['generate_code_quest.py']), \
                 patch.object(generate_code_quest, 'fetch_calendar', side_effect=ValueError('offline')):
                with self.assertRaises(ValueError): generate_code_quest.main()
            self.assertEqual((root/'code-quest.svg').read_text(), 'previous SVG')
            self.assertEqual((root/'calendar.json').read_text(), 'previous calendar')


if __name__ == '__main__':
    unittest.main()
