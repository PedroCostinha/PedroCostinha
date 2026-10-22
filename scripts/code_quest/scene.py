"""Compose a self-contained SVG; CSS timelines also work inside an image element."""

from html import escape
import re
import xml.etree.ElementTree as ET

from .motion import DURATION, FINISH, START, GRID_X, GRID_Y, GRID_WIDTH, GROUND, Route
from .sprites import pixel_text, sprite_defs

COLORS = ('#202027', '#54232C', '#872A36', '#BD343E', '#EF5651')
POSES = ('idle', 'run0', 'run1', 'run2', 'run3', 'jump', 'fall', 'land', 'collect', 'celebrate')


def pct(t):
    return f'{100 * t / DURATION:.4f}%'


def timeline(name, events, prop='opacity', discrete=False):
    frames = ''.join(f'{pct(t)}{{{prop}:{value}}}' for t, value in events)
    return (f'@keyframes {name}{{{frames}}}'
            f'.{name}{{animation:{name} {DURATION}s {"steps(1,end)" if discrete else "linear"} infinite}}')


def build_styles(route):
    css = ['svg{background:#0D0D0F}text{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}',
           '.cinematic{animation:fade 20.8s linear infinite}',
           '@keyframes fade{0%,100%{opacity:0}5%,95%{opacity:1}}',
           '.runner{transform:translate(78px,302px)}.pose{opacity:0}.idle{opacity:1}',
           '.complete{opacity:0}.press{opacity:0}',
           '.progress{transform-box:fill-box;transform-origin:left;transform:scaleX(0)}',
           timeline('press', [(0, 1), (.7, 1), (1.3, 0), (DURATION, 0)]),
           timeline('complete', [(0, 0), (17.2, 0), (17.6, 1), (20.0, 1), (20.6, 0), (DURATION, 0)]),
           timeline('progress', [(0, 'scaleX(0)'), (START, 'scaleX(0)'), (FINISH, 'scaleX(1)'),
                                 (20.4, 'scaleX(1)'), (DURATION, 'scaleX(0)')], 'transform')]
    samples = sorted(set([round(i * DURATION / 1248, 6) for i in range(1249)] +
                         [START, FINISH, 17.65, 20, DURATION]))
    css.append(timeline('runner', [(t, f'translate({route.position(t)[0]:.2f}px,{route.position(t)[1]:.2f}px)')
                                   for t in samples], 'transform'))
    # Compress pose changes into discrete events rather than duplicating every sample.
    events = []
    previous = None
    for t in samples:
        pose = route.pose(t)
        if pose != previous:
            events.append((t, pose))
            previous = pose
    for pose in POSES:
        values = [(t, int(selected == pose)) for t, selected in events]
        values.append((DURATION, int(pose == 'idle')))
        css.append(timeline(pose, values, discrete=True))
    css.append('@keyframes drift{0%,100%{transform:translateX(0)}50%{transform:translateX(18px)}}'
               '.cloud{animation:drift 20.8s ease-in-out infinite}'
               '@keyframes turn{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.22)}}'
               '.turn{animation:turn 1.1s linear infinite;transform-box:fill-box;transform-origin:center}'
               '@keyframes wave{0%,100%{transform:skewY(0deg)}50%{transform:skewY(6deg)}}'
               '.flag{animation:wave 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:left}')
    for i, coin in enumerate(route.coins):
        css.append(timeline(f'coin{i}', [(0, 1), (coin.collected - .07, 1), (coin.collected + .10, 0),
                                         (DURATION, 0)]))
        css.append(timeline(f'spark{i}', [(0, 0), (coin.collected - .01, 0), (coin.collected + .02, 1),
                                          (coin.collected + .35, 0), (DURATION, 0)]))
    for i in range(len(route.coins) + 1):
        begin = route.coins[i - 1].collected if i else 0
        end = route.coins[i].collected if i < len(route.coins) else DURATION
        css.append(timeline(f'count{i}', [(0, int(i == 0)), (begin, 1), (end, 0), (DURATION, 0)], discrete=True))
    for i, jump in enumerate(route.jumps):
        t = route.time_at(jump.end)
        css.append(timeline(f'dust{i}', [(0, 0), (t, 0), (t + .02, .7), (t + .25, 0), (DURATION, 0)]))
    css.append('.static-count{display:none}'
               '@media(prefers-reduced-motion:reduce){*{animation:none!important}'
               '.cinematic{opacity:1}.runner{transform:translate(1116px,302px)}'
               '.pose,.press,.coin,.spark,.dust,.counter{display:none}.idle{display:inline;opacity:1}'
               '.complete{opacity:1}.progress{transform:scaleX(1)}.static-count{display:inline}}')
    return ''.join(css)


def rect(x, y, w, h, fill, extra=''):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" {extra}/>'


def background():
    result = [rect(.5, .5, 1199, 519, '#0D0D0F', 'rx="16" stroke="#303039"'),
              rect(32, 31, 4, 59, '#E53935'),
              pixel_text('CODE QUEST', 52, 34, 4.5),
              pixel_text('PEDRO COSTINHA', 54, 78, 1.5, '#909099'),
              pixel_text('WORLD 01', 1146, 35, 1.5, '#909099', anchor='end'),
              rect(32, 113, 1136, 1, '#2A2A33'),
              rect(32, 472, 1136, 1, '#2A2A33')]
    # Fixed positions keep builds reproducible; stars are decorative, never data.
    for i in range(20):
        x = 45 + (i * 157) % 1100
        y = 164 + (i * 31) % 85
        result.append(rect(x, y, 2, 2, '#34323B'))
    for x, y, w in ((220, 194, 64), (750, 178, 80), (937, 226, 48)):
        result.append(f'<g class="cloud" fill="#1D1D25"><path d="M{x} {y}h{w}v8h-8v5h-{w-16}v-5h-8z"/>'
                      f'<path d="M{x+14} {y}v-8h{w-28}v8z"/></g>')
    for i in range(29):
        x, w, h = 52 + i * 39, 26 + i % 3 * 4, 14 + (i * 17) % 49
        result.append(rect(x, 302 - h, w, h, '#15151C'))
        if i % 3 == 0:
            result.append(rect(x + 6, 310 - h, 3, 5, '#39252D'))
    # A stepped moon, rendered as pixels rather than a photographic backdrop.
    result.append('<path fill="#29252C" d="M1014 158h22v6h8v8h6v22h-6v8h-8v6h-22v-6h-8v-8h-6v-22h6v-8h8z"/>')
    result.append('<path fill="#181820" d="M1032 158h4v6h8v8h6v22h-6v8h-8v6h-15v-6h11v-8h6v-22h-6z"/>')
    return ''.join(result)


def calendar_layer(calendar, route):
    result = []
    last_month = None
    last_label_x = -100
    months = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')
    for day in calendar.days:
        x = GRID_X + day.week * route.pitch
        y = GRID_Y + day.weekday * 18
        result.append(rect(x, y, route.pitch - 4, 14, COLORS[day.level],
                           f'rx="2" stroke="#34303A" stroke-width=".5" data-date="{day.date}" '
                           f'data-count="{day.count}" data-level="{day.level}"')[:-2] +
                      f'><title>{day.date}: {day.count} contributions</title></rect>')
        if day.date.month != last_month and (day.date.day == 1 or last_month is None):
            if x < 1035 and x - last_label_x >= 34:
                result.append(f'<text x="{x:g}" y="459" font-size="11" fill="#909099">{months[day.date.month-1]}</text>')
                last_label_x = x
            last_month = day.date.month
    for row, label in ((1, 'MON'), (3, 'WED'), (5, 'FRI')):
        result.append(pixel_text(label, 74, GRID_Y + row * 18 + 3, .9, '#909099'))
    for platform in route.platforms:
        result.append(rect(platform.x, platform.y, platform.end - platform.x, 7, '#30303B'))
        result.append(rect(platform.x, platform.y, platform.end - platform.x, 2,
                           '#A14A50' if platform.level else '#555560'))
        result.append(rect(platform.x + 4, platform.y + 7, 2, GRID_Y - platform.y - 10, '#24232C'))
        result.append(rect(platform.end - 6, platform.y + 7, 2, GRID_Y - platform.y - 10, '#24232C'))
    return ''.join(result)


def portals():
    return ('<g shape-rendering="crispEdges">'
            '<path fill="#24242E" d="M54 302v-51h8v-8h30v8h8v51H88v-42H66v42z"/>'
            '<path fill="#9F303B" d="M58 302v-49h6v-6h26v6h6v49h-5v-46h-6v-4H68v4h-5v46z"/>'
            '<path fill="#E53935" d="M66 247h18v3H66zM58 265h3v15h-3z"/>'
            '<path fill="#17171C" d="M1070 302h86v8h-86zM1094 310h48v8h-48z"/>'
            '<path fill="#666675" d="M1125 302V222h3v80z"/>'
            '<path fill="#E3BA61" d="M1123 218h7v5h-7z"/>'
            '<g class="flag"><path fill="#A71D2A" d="M1128 226h34v23h-34z"/>'
            '<path fill="#E53935" d="M1128 226h28v19h-28z"/>'
            '<path fill="#F2F2F2" d="M1137 232h4v3h-4zM1144 232h4v3h-4zM1140 238h5v3h-5z"/></g></g>')


def animated_layer(route):
    result = ['<g class="cinematic">',
              pixel_text('PRESS START', 600, 211, 2, '#E3BA61', 'press', 'middle'),
              '<g class="complete">',
              pixel_text('LEVEL COMPLETE!', 600, 190, 3, '#F2F2F2', anchor='middle'),
              pixel_text('PEDRO COSTINHA', 600, 226, 1.6, '#EF5651', anchor='middle'), '</g>']
    for i, coin in enumerate(route.coins):
        result.append(f'<g transform="translate({coin.x:.2f} {coin.y:.2f})">'
                      f'<g class="coin coin{i}"><g class="turn"><use href="#coin"/></g></g>'
                      f'<g class="spark spark{i}" opacity="0" fill="#E3BA61">'
                      '<path d="M-1-14h2v5h-2zM-1 9h2v5h-2zM-14-1h5v2h-5zM9-1h5v2H9z"/></g></g>')
    for i, jump in enumerate(route.jumps):
        result.append(f'<g class="dust dust{i}" opacity="0" fill="#909099" '
                      f'transform="translate({jump.end:.2f} {jump.end_y:.2f})">'
                      '<path d="M-18-3h6v2h-6zM-12-7h3v3h-3zM12-3h6v2h-6zM9-7h3v3H9z"/></g>')
    result.append('<g clip-path="url(#playfield)"><g class="runner">')
    for pose in POSES:
        result.append(f'<g class="pose {pose}"><use href="#sprite-{pose}"/></g>')
    result.extend(['</g>', '</g>', '</g>'])
    return ''.join(result)


def render(calendar):
    route = Route(calendar)
    first, last = calendar.days[0].date, calendar.days[-1].date
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="0 0 1200 520" '
           'role="img" aria-labelledby="title description">',
           '<title id="title">CODE QUEST — Pedro Costinha</title>',
           f'<desc id="description">Original pixel explorer runs and jumps across platforms derived from '
           f'PedroCostinha’s real GitHub contribution calendar. {first} to {last}, {calendar.total} contributions. '
           'Each colored square is one day; gold coins are decorative milestones, not commit counts. '
           'The 20.8 second animation loops. Reduced motion shows the complete calendar and finish screen.</desc>',
           f'<metadata>source={escape(calendar.source)}; login=PedroCostinha; from={first}; to={last}</metadata>',
           '<defs><clipPath id="playfield"><rect x="40" y="170" width="1125" height="132"/></clipPath>',
           sprite_defs(), '</defs>', '<style>', build_styles(route), '</style>', background(),
           pixel_text('CONTRIBUTION RUN', 54, 133, 1.15, '#909099'),
           f'<text x="1146" y="145" text-anchor="end" font-size="13" fill="#909099">{first} / {last}</text>',
           pixel_text(f'{calendar.total} CONTRIBUTIONS', 54, 158, 1.45, '#C4C4CE'),
           pixel_text('COINS', 994, 77, 1.5, '#909099'),
           '<g transform="translate(1064 82)"><use href="#coin"/></g>']
    for i in range(len(route.coins) + 1):
        out.append(pixel_text(f'{i:02}', 1146, 76, 2, '#E3BA61', f'counter count{i}', 'end'))
    out.append(pixel_text(f'{len(route.coins):02}', 1146, 76, 2, '#E3BA61', 'static-count', 'end'))
    out.extend([calendar_layer(calendar, route), portals(), animated_layer(route),
                rect(116, 483, 954, 2, '#24242C'),
                rect(116, 483, 954, 2, '#E53935', 'class="progress"'),
                pixel_text('REAL DAYS. REAL PROGRESS.', 54, 497, 1.15, '#909099')])
    out.append(pixel_text('LESS', 924, 498, .9, '#909099'))
    for i, color in enumerate(COLORS):
        out.append(rect(958 + i * 18, 497, 12, 9, color, 'rx="1"'))
    out.append(pixel_text('MORE', 1056, 498, .9, '#909099'))
    out.append('</svg>')
    svg = ''.join(out)
    validate_svg(svg, calendar)
    return svg


def validate_svg(svg, calendar=None):
    root = ET.fromstring(svg)
    if root.get('viewBox') != '0 0 1200 520' or len(svg.encode()) > 250_000:
        raise ValueError('SVG dimensions or size budget exceeded')
    ids = [e.get('id') for e in root.iter() if e.get('id')]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate SVG IDs')
    for element in root.iter():
        if element.tag.split('}')[-1] in ('script', 'foreignObject', 'image', 'animate', 'animateTransform'):
            raise ValueError('Unsupported or external SVG content')
        for key, value in element.attrib.items():
            if key.lower().startswith('on'):
                raise ValueError('Event handlers are not permitted')
            if key.split('}')[-1] == 'href' and (not value.startswith('#') or value[1:] not in ids):
                raise ValueError('Broken or external SVG reference')
    if re.search(r'url\(\s*["\']?(?!#)', svg):
        raise ValueError('External CSS references are not permitted')
    if calendar:
        cells = [e for e in root.iter() if e.get('data-date')]
        if [(e.get('data-date'), int(e.get('data-count')), int(e.get('data-level'))) for e in cells] != [
                (str(d.date), d.count, d.level) for d in calendar.days]:
            raise ValueError('SVG cells do not match the validated source calendar')
