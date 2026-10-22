"""Read only aggregate contribution dates, counts and activity levels."""

from dataclasses import dataclass
from datetime import date, timedelta
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LEVELS = ('NONE', 'FIRST_QUARTILE', 'SECOND_QUARTILE', 'THIRD_QUARTILE', 'FOURTH_QUARTILE')
QUERY = '''query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
  }
}'''


@dataclass(frozen=True)
class Day:
    date: date
    count: int
    level: int
    week: int
    weekday: int


@dataclass(frozen=True)
class Calendar:
    days: tuple[Day, ...]
    weeks: int
    total: int
    source: str


def validate_calendar(payload):
    """Reject incomplete/ambiguous calendars before touching existing artifacts."""
    if not isinstance(payload, dict) or payload.get('login') != 'PedroCostinha':
        raise ValueError('Calendar must belong to PedroCostinha')
    source = payload.get('source')
    if source not in ('github-graphql', 'github-public-calendar'):
        raise ValueError('Unsupported calendar provenance')
    rows = payload.get('days')
    if not isinstance(rows, list) or not 364 <= len(rows) <= 371:
        raise ValueError('Expected a complete rolling year (364–371 days)')
    days = []
    for row in rows:
        when = date.fromisoformat(row['date'])
        count, level = row['count'], row['level']
        if type(count) is not int or count < 0 or type(level) is not int or not 0 <= level <= 4:
            raise ValueError('Invalid count or activity level')
        if (count == 0) != (level == 0):
            raise ValueError('Count and activity level disagree')
        if days and when != days[-1].date + timedelta(days=1):
            raise ValueError('Dates must be ordered, unique and consecutive')
        first = days[0].date if days else when
        sunday = first - timedelta(days=(first.weekday() + 1) % 7)
        days.append(Day(when, count, level, (when - sunday).days // 7, (when.weekday() + 1) % 7))
    total = payload.get('total')
    if type(total) is not int or total != sum(d.count for d in days):
        raise ValueError('Total must match the sum of daily contributions')
    weeks = days[-1].week + 1
    if not 51 <= weeks <= 54:
        raise ValueError('Invalid number of calendar weeks')
    return Calendar(tuple(days), weeks, total, source)


def normalize_graphql(response, login='PedroCostinha'):
    if not isinstance(response, dict):
        raise ValueError('Malformed GitHub GraphQL response')
    if response.get('errors'):
        raise ValueError('GitHub GraphQL returned errors; previous artifacts preserved')
    try:
        calendar = response['data']['user']['contributionsCollection']['contributionCalendar']
        rows = []
        for week in calendar['weeks']:
            for day in week['contributionDays']:
                when = date.fromisoformat(day['date'])
                if day['weekday'] != (when.weekday() + 1) % 7:
                    raise ValueError('API weekday disagrees with date')
                rows.append(dict(date=day['date'], count=day['contributionCount'],
                                 level=LEVELS.index(day['contributionLevel'])))
        payload = dict(login=login, source='github-graphql', total=calendar['totalContributions'], days=rows)
        validate_calendar(payload)
        return payload
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError('Missing or malformed GitHub contribution calendar') from exc


def fetch_calendar(token, *, opener=urlopen, sleep=time.sleep):
    if not token:
        raise ValueError('GITHUB_TOKEN is required; there is no synthetic-data fallback')
    request = Request('https://api.github.com/graphql',
                      data=json.dumps(dict(query=QUERY, variables=dict(login='PedroCostinha'))).encode(),
                      headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json',
                               'User-Agent': 'PedroCostinha-CodeQuest'})
    for attempt in range(4):
        try:
            with opener(request, timeout=30) as response:
                result = json.load(response)
            # GraphQL errors can arrive with HTTP 200; retry only rate-limit errors.
            if isinstance(result, dict) and any(e.get('type') == 'RATE_LIMITED' for e in result.get('errors', [])):
                if attempt < 3:
                    sleep(20 * (attempt + 1))
                    continue
            return normalize_graphql(result)
        except HTTPError as exc:
            retryable = exc.code in (429, 500, 502, 503, 504) or (
                exc.code == 403 and (exc.headers.get('X-RateLimit-Remaining') == '0'
                                    or exc.headers.get('Retry-After') is not None))
            if not retryable or attempt == 3:
                raise ValueError(f'GitHub API HTTP {exc.code}; previous artifacts preserved') from None
            try:
                delay = min(60, max(2, int(exc.headers.get('Retry-After', 2 ** (attempt + 1)))))
            except ValueError:
                delay = 2 ** (attempt + 1)
            sleep(delay)
        except (URLError, TimeoutError, OSError):
            if attempt == 3:
                raise ValueError('GitHub API unavailable; previous artifacts preserved') from None
            sleep(2 ** (attempt + 1))
    raise ValueError('GitHub API rate limited; previous artifacts preserved')
