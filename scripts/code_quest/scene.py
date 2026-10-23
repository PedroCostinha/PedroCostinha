"""Self-contained CODE QUEST V2: data-linked ledges and synchronized CSS timelines."""

from html import escape
import re
import xml.etree.ElementTree as ET

from .motion import DURATION, FINISH, START, GRID_X, GRID_Y, GRID_WIDTH, GROUND, Route, POSES
from .sprites import pixel_text, sprite_defs

COLORS = ('#202027', '#54232C', '#872A36', '#BD343E', '#EF5651')


def pct(t):
    return f'{100 * t / DURATION:.4f}%'


def timeline(name, events, prop='opacity', discrete=False):
    # Coalesce equal timestamps; the final value is intentional at each boundary.
    frames = ''.join(f'{pct(t)}{{{prop}:{value}}}' for t,value in sorted(dict(events).items()))
    return (f'@keyframes {name}{{{frames}}}'
            f'.{name}{{animation:{name} {DURATION}s {"steps(1,end)" if discrete else "linear"} infinite}}')


def build_styles(route):
    css = ['svg{background:#0D0D0F}text{font-family:ui-monospace,Consolas,monospace}',
           f'.cinematic{{animation:fade {DURATION}s linear infinite}}',
           '@keyframes fade{0%,100%{opacity:0}4%,94%{opacity:1}98%{opacity:0}}',
           '.runner{transform:translate(78px,312px)}.pose{opacity:0}.idle{opacity:1}',
           '.complete,.press,.week,.spark,.dust,.counter,.activity-link{opacity:0}',
           '.progress{transform-box:fill-box;transform-origin:left;transform:scaleX(0)}',
           timeline('press', [(0,1),(.65,1),(1.35,0),(DURATION,0)]),
           timeline('complete', [(0,0),(FINISH+.15,0),(17.8,1),(19.6,1),(20.35,0),(DURATION,0)]),
           timeline('portal', [(0,.2),(.5,1),(1.25,.8),(2.1,.12),(19.9,.12),(DURATION,.2)]),
           timeline('progress', [(0,'scaleX(0)'),(START,'scaleX(0)'),(FINISH,'scaleX(1)'),
                                 (20.4,'scaleX(1)'),(DURATION,'scaleX(0)')], 'transform')]
    # Exact event boundaries plus 30 Hz parabola samples keep geometry accurate without
    # the V1's redundant 60 Hz frame list. Poses only emit when their visibility changes.
    boundaries = [0,START,START+route.acceleration,FINISH,17.65,20,DURATION]
    for j in route.jumps:
        boundaries.extend((route.time_at(j.x),route.time_at(j.end),route.time_at(j.end)+.10))
    boundaries.extend(c.collected for c in route.coins)
    samples = sorted(set([round(i * DURATION / 624,6) for i in range(625)] + boundaries))
    css.append(timeline('runner', [(t,f'translate({route.position(t)[0]:.2f}px,{route.position(t)[1]:.2f}px)')
                                  for t in samples], 'transform'))
    for pose in POSES:
        events,previous = [],None
        for t in samples:
            visible = int(route.pose(t) == pose)
            if visible != previous:
                events.append((t,visible))
                previous = visible
        events.append((DURATION,int(pose=='idle')))
        css.append(timeline(pose,events,discrete=True))
    css.extend(['@keyframes drift{0%,100%{transform:translateX(0)}50%{transform:translateX(12px)}}'
                '.cloud{animation:drift 20.8s ease-in-out infinite}',
                '@keyframes parallax{0%,100%{transform:translateX(0)}50%{transform:translateX(-5px)}}'
                '.skyline{animation:parallax 20.8s ease-in-out infinite}',
                '@keyframes turn{0%,100%{transform:scaleX(1)}25%,75%{transform:scaleX(.55)}50%{transform:scaleX(.18)}}'
                '.turn{animation:turn 1.2s steps(2,end) infinite;transform-box:fill-box;transform-origin:center}',
                '@keyframes wave{0%,100%{transform:skewY(-3deg)}50%{transform:skewY(5deg)}}'
                '.flag{animation:wave 1.6s ease-in-out infinite;transform-box:fill-box;transform-origin:left}',
                '@keyframes burst{from{transform:scale(.4)}to{transform:scale(1.6)}}'
                '.burst{animation:burst .48s ease-out infinite}',
                '@keyframes twinkle{0%,100%{opacity:.3}50%{opacity:.8}}'
                '.twinkle{animation:twinkle 4s ease-in-out infinite}'])
    for week,t in enumerate(route.week_times):
        css.append(timeline(f'week{week}',[(0,0),(t-.18,0),(t,.8),(t+.42,0),(DURATION,0)]))
    for i,c in enumerate(route.coins):
        css.append(timeline(f'coin{i}',[(0,1),(c.collected,0),(DURATION,0)],discrete=True))
        css.append(timeline(f'spark{i}',[(0,0),(c.collected,0),(c.collected+.025,1),
                                        (c.collected+.42,0),(DURATION,0)]))
        css.append(timeline(f'link{i}',[(0,0),(c.collected-.25,0),(c.collected,.9),
                                       (c.collected+.65,0),(DURATION,0)]))
        css.append(timeline(f'burst{i}',[(0,'scale(.4)'),(c.collected,'scale(.4)'),
                                        (c.collected+.42,'scale(1.6)'),(DURATION,'scale(1.6)')],'transform'))
    for i in range(len(route.coins)+1):
        begin = route.coins[i-1].collected if i else 0
        events = [(0,int(i==0)),(begin,1)]
        if i < len(route.coins):
            events.append((route.coins[i].collected,0))
        events.append((DURATION,int(i==len(route.coins))))
        css.append(timeline(f'count{i}',events,discrete=True))
    for i,j in enumerate(route.jumps):
        t=route.time_at(j.end)
        css.append(timeline(f'dust{i}',[(0,0),(t,0),(t+.025,.65),(t+.24,0),(DURATION,0)]))
    css.append('.static-count{display:none}@media(prefers-reduced-motion:reduce){'+static_styles()+'}')
    return ''.join(css)


def static_styles():
    return ('*{animation:none!important}'
            '.cinematic{opacity:1}.runner{transform:translate(1116px,312px)}'
            '.pose,.press,.coin,.spark,.dust,.counter,.week,.activity-link{display:none}'
            '.victory{display:inline;opacity:1}.idle{display:none}'
            '.complete{opacity:1}.portal{opacity:.35}.progress{transform:scaleX(1)}.static-count{display:inline}')


def rect(x,y,w,h,fill,extra=''):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" {extra}/>'


def background():
    out=[rect(.5,.5,1199,519,'#0D0D0F','rx="16" stroke="#303039"'),
         rect(32,31,4,59,'#D94A4A'),pixel_text('CODE QUEST',52,34,4.5),
         pixel_text('PEDRO COSTINHA',54,78,1.5,'#909099'),
         pixel_text('V2',357,40,1.1,'#D94A4A'),
         pixel_text('WORLD 01',1146,35,1.5,'#909099',anchor='end'),
         rect(32,113,1136,1,'#2A2A33'),rect(32,472,1136,1,'#2A2A33'),
         rect(40,177,1120,139,'url(#sky)'),
         '<ellipse cx="1015" cy="276" rx="195" ry="84" fill="url(#red-haze)"/>']
    for i in range(39):
        x,y=48+(i*157)%1100,184+(i*31)%82
        out.append(rect(x,y,2 if i%4 else 3,2 if i%4 else 3,'#66535D',
                        'class="twinkle"' if i%6==0 else 'opacity=".45"'))
    for x,y,w in ((205,205,76),(530,187,54),(790,220,90)):
        out.append(f'<g class="cloud" fill="#24222C" opacity=".65"><path d="M{x} {y}h{w}v6h-6v6h-{w-12}v-6h-6z"/>'
                   f'<path d="M{x+12} {y}v-7h14v-5h{w-45}v5h13v7z"/>'
                   f'<path fill="#322631" d="M{x+8} {y+10}h{w-16}v2h-{w-16}z"/></g>')
    out.append('<g class="skyline">')
    for i in range(37):
        x,w,h=40+i*31,22+i%3*3,20+(i*17)%53
        out.append(rect(x,310-h,w,h,'#191923'))
        out.append(rect(x+4,307-h,w-8,2,'#24212B'))
        if i%4==0:
            out.extend([rect(x+w/2,300-h,1,10,'#34303B'),rect(x+w/2,298-h,2,2,'#96313E')])
        for row in range(h//14):
            if (row+i)%3==0:
                out.append(rect(x+6,319-h+row*10,3,3,'#46303B'))
    out.append('</g>')
    for i in range(17):
        x,w,h=42+i*68,43+i%3*5,12+(i*13)%34
        out.append(rect(x,314-h,w,h,'#20202A'))
        out.append(rect(x+4,314-h,w-8,2,'#342832'))
    out.append('<path fill="#3D2B36" d="M1012 187h20v5h7v7h5v20h-5v7h-7v5h-20v-5h-7v-7h-5v-20h5v-7h7z"/>')
    out.append('<path fill="#201D28" d="M1026 187h6v5h7v7h5v20h-5v7h-7v5h-14v-5h9v-7h5v-20h-6z"/>')
    return ''.join(out)


def calendar_layer(calendar,route):
    out=[rect(GRID_X-8,GRID_Y-5,GRID_WIDTH+12,132,'#121217','rx="5" stroke="#2A252E"')]
    # Ledges sit on the calendar's upper rim. Six-week activity summaries set elevation.
    # Foundations end above the first row, so no data cell is covered.
    for p in route.platforms:
        width=p.end-p.x
        out.extend([rect(p.x,p.y+3,width,GRID_Y-p.y-5,'#231F29'),
                    rect(p.x,p.y,width,4,'#33303B'),
                    rect(p.x,p.y,width,1.5,'#D94A4A' if p.level else '#64606D')])
        for x in range(round(p.x)+4,round(p.end)-2,12):
            out.append(rect(x,p.y+6,5,2,'#3E2A34' if p.level else '#2C2831'))
    last_month,last_label_x=None,-100
    months=('JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC')
    for d in calendar.days:
        x,y=GRID_X+d.week*route.pitch,GRID_Y+d.weekday*18
        out.append(rect(x,y,route.pitch-4,14,COLORS[d.level],
                        f'rx="2" stroke="#34303A" stroke-width=".5" data-date="{d.date}" '
                        f'data-count="{d.count}" data-level="{d.level}"')[:-2]+
                   f'><title>{d.date}: {d.count} contributions</title></rect>')
        if d.date.month != last_month and (d.date.day==1 or last_month is None):
            if x<1035 and x-last_label_x>=34:
                out.append(f'<text x="{x:g}" y="459" font-size="11" fill="#909099">{months[d.date.month-1]}</text>')
                last_label_x=x
            last_month=d.date.month
    out.append('<g class="cinematic" fill="none" stroke="#EF7972">')
    for week in range(calendar.weeks):
        commands = []
        for d in calendar.days:
            if d.week==week:
                x,y = GRID_X+week*route.pitch,GRID_Y+d.weekday*18
                commands.append(f'M{x:.2f} {y}h{route.pitch-4:.2f}v14h{-route.pitch+4:.2f}z')
        out.append(f'<path class="week week{week}" data-week="{week}" stroke-width="1.2" '
                   f'd="{"".join(commands)}"/>')
    for i,c in enumerate(route.coins):
        d=next(d for d in calendar.days if str(d.date)==c.date)
        y=GRID_Y+d.weekday*18
        out.append(f'<g class="activity-link link{i}" data-linked-date="{c.date}" stroke="#F5D57C">'
                   f'<path d="M{c.x:.2f} {route.feet_at(c.x):.2f}V{GRID_Y-2}" stroke-dasharray="2 3"/>')
        out.append(rect(GRID_X+d.week*route.pitch,y,route.pitch-4,14,'none','rx="2" stroke-width="1.5"'))
        out.append('</g>')
    out.append('</g>')
    for row,label in ((1,'MON'),(3,'WED'),(5,'FRI')):
        out.append(pixel_text(label,74,GRID_Y+row*18+3,.9,'#909099'))
    return ''.join(out)


def portals():
    return ('<g shape-rendering="crispEdges">'
            '<path fill="#24242E" d="M54 312v-53h8v-8h30v8h8v53H88v-44H66v44z"/>'
            '<path fill="#96313E" d="M58 312v-51h6v-6h26v6h6v51h-5v-48h-6v-4H68v4h-5v48z"/>'
            '<g class="portal"><path fill="#EF5651" d="M65 264h23v48H65z" opacity=".22"/>'
            '<path fill="#EF7972" d="M66 255h18v3H66zM58 273h3v15h-3zM91 285h2v12h-2z"/></g>'
            '<path fill="#17171C" d="M1070 312h86v8h-86zM1094 320h48v7h-48z"/>'
            '<path fill="#888C9F" d="M1125 312V228h3v84z"/>'
            '<path fill="#E3BA61" d="M1123 222h7v6h-7z"/>'
            '<g class="flag"><path fill="#96313E" d="M1128 232h34v23h-34z"/>'
            '<path fill="#EF5651" d="M1128 232h28v19h-28z"/>'
            '<path fill="#E6EDF3" d="M1135 237h5v5h-5zM1145 237h5v5h-5zM1140 242h5v5h-5z"/></g></g>')


def animated_layer(route):
    out=['<g class="cinematic">',pixel_text('PRESS START',600,212,2,'#E3BA61','press','middle'),
         '<g class="complete">',rect(360,177,480,66,'#15141C','rx="4" stroke="#4A2934"'),
         pixel_text('LEVEL COMPLETE!',600,190,3,'#E6EDF3',anchor='middle'),
         pixel_text('PEDRO COSTINHA',600,223,1.6,'#EF5651',anchor='middle'),'</g>']
    for i,c in enumerate(route.coins):
        out.append(f'<g transform="translate({c.x:.2f} {c.y:.2f})">'
                   f'<g class="coin coin{i}" data-collected="{c.collected:.6f}" data-coin-date="{c.date}">'
                   '<ellipse rx="11" ry="13" fill="#D4A347" opacity=".09"/>'
                   '<g class="turn"><use href="#coin"/></g></g>'
                   f'<g class="spark spark{i}" fill="#F5D57C"><g class="burst{i}">'
                   '<path d="M-1-15h2v5h-2zM-1 10h2v5h-2zM-15-1h5v2h-5zM10-1h5v2h-5z"/>'
                   '<path fill="#FFF0BF" d="M-10-10h3v3h-3zM7 7h3v3H7zM7-10h2v2H7zM-10 7h2v2h-2z"/>'
                   '</g></g></g>')
    for i,j in enumerate(route.jumps):
        out.append(f'<g class="dust dust{i}" fill="#88808C" transform="translate({j.end:.2f} {j.end_y:.2f})">'
                   '<path d="M-21-3h6v2h-6zM-14-7h3v3h-3zM15-3h6v2h-6zM11-7h3v3h-3z"/></g>')
    out.append('<g clip-path="url(#playfield)"><g class="runner">')
    for pose in POSES:
        out.append(f'<g class="pose {pose}"><use href="#sprite-{pose}"/></g>')
    out.extend(['</g></g>', '<g class="complete" fill="#E3BA61">'])
    for i in range(14):
        x,y=1080+(i*23)%81,235+(i*17)%57
        out.append(rect(x,y,2,3,'#E3BA61' if i%2 else '#D94A4A'))
    out.append('</g></g>')
    return ''.join(out)


def render(calendar):
    route=Route(calendar)
    first,last=calendar.days[0].date,calendar.days[-1].date
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="0 0 1200 520" '
         'role="img" aria-labelledby="title description">',
         '<title id="title">CODE QUEST V2 — Pedro Costinha</title>',
         f'<desc id="description">Original 42 pixel explorer runs along the rim of PedroCostinha’s real GitHub '
         f'calendar. Each week lights up as the explorer passes. {first} to {last}, {calendar.total} contributions. '
         'Every square retains its real date, count and activity level. Coins mark real high-activity days, not commits. '
         'The 20.8 second animation loops. Reduced motion shows the complete calendar and finish screen.</desc>',
         f'<metadata>version=2; source={escape(calendar.source)}; login=PedroCostinha; from={first}; to={last}</metadata>',
         '<defs><clipPath id="playfield"><rect x="40" y="176" width="1125" height="138"/></clipPath>',
         '<linearGradient id="sky" x2="0" y2="1"><stop stop-color="#12121C"/><stop offset="1" stop-color="#201923"/></linearGradient>',
         '<radialGradient id="red-haze"><stop stop-color="#96313E" stop-opacity=".18"/><stop offset="1" stop-color="#96313E" stop-opacity="0"/></radialGradient>',
         sprite_defs(),'</defs><style>',build_styles(route),'</style>',background(),
         pixel_text('CONTRIBUTION RUN',54,133,1.15,'#909099'),
         f'<text x="1146" y="145" text-anchor="end" font-size="13" fill="#909099">{first} / {last}</text>',
         pixel_text(f'{calendar.total} CONTRIBUTIONS',54,158,1.45,'#C4C4CE'),
         pixel_text('COINS',994,77,1.5,'#909099'),
         '<g transform="translate(1064 82)"><use href="#coin"/></g>']
    out.append('<g class="cinematic">')
    for i in range(len(route.coins)+1):
        out.append(pixel_text(f'{i:02}',1146,76,2,'#E3BA61',f'counter count{i}','end'))
    out.append('</g>')
    out.append(pixel_text(f'{len(route.coins):02}',1146,76,2,'#E3BA61','static-count','end'))
    out.extend([calendar_layer(calendar,route),portals(),animated_layer(route),
                rect(116,483,954,2,'#24242C'),rect(116,483,954,2,'#D94A4A','class="progress"'),
                pixel_text('REAL DAYS. REAL PROGRESS.',54,497,1.15,'#909099'),pixel_text('LESS',924,498,.9,'#909099')])
    for i,color in enumerate(COLORS):
        out.append(rect(958+i*18,497,12,9,color,'rx="1"'))
    out.append(pixel_text('MORE',1056,498,.9,'#909099'))
    out.append('</svg>')
    svg=''.join(out)
    validate_svg(svg,calendar)
    return svg


def render_static(calendar):
    """Explicit picture source for image hosts that do not inherit motion preferences."""
    svg = render(calendar)
    styles = 'svg{background:#0D0D0F}text{font-family:ui-monospace,Consolas,monospace}'+static_styles()
    svg = re.sub(r'<style>.*?</style>',lambda _: '<style>'+styles+'</style>',svg,flags=re.S)
    svg = svg.replace('The 20.8 second animation loops.', 'This is the static, reduced-motion version.')
    validate_svg(svg,calendar)
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
