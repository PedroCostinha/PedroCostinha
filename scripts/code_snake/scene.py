# SPDX-License-Identifier: MIT
# Copyright (c) 2026 PedroCostinha
# Composition and imported art remain reserved. See docs/CODE_SNAKE_LICENSING.md.
from html import escape
import json
import xml.etree.ElementTree as ET
from .art import PALETTE, head
from .model import DURATION, replay

def rect(x, y, w, h, color, extra=''):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{color}" {extra}/>'

def label(x, y, value, size=14, color='#a6a3ad'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{escape(str(value))}</text>'

def render(calendar, *, static=False, mobile=False):
    demo = replay(calendar, mobile)
    width, height = (480, 590) if mobile else (1080, 640)
    cell = 26 if mobile else 41
    left, top = (32, 143) if mobile else (48, 130)
    footer = 417 if mobile else 458
    def pos(i):
        x, y = demo.route[max(0, min(i, len(demo.route)-1))]
        return left+x*cell, top+y*cell
    def timeline(name, pairs, prop='transform', stepped=False):
        frames = ''.join(f'{p:.5f}%{{{prop}:{v}}}' for p,v in pairs)
        return f'@keyframes {name}{{{frames}}}.{name}{{animation:{name} {DURATION}s {"steps(1,end)" if stepped else "linear"} infinite}}'
    css = ['svg{background:#0d0d0f;max-width:100%;height:auto}text{font-family:ui-monospace,Consolas,monospace}.moving{display:none}.still{display:inline}']
    if not static:
        css.append('@media(prefers-reduced-motion:no-preference){.moving{display:inline}.still{display:none}')
        css.append('@keyframes curtain{0%,100%{opacity:0}4%,90%{opacity:1}98%{opacity:0}}.curtain{animation:curtain 18s linear infinite}')
        css.append(timeline('complete',[(0,'0'),(15/DURATION*100,'1'),(100,'1')],'opacity',True))
        for segment in range(10):
            events = [(0, f'translate({pos(3-segment)[0]}px,{pos(3-segment)[1]}px)')]
            events += [(demo.time(i)/DURATION*100, f'translate({pos(i-segment)[0]}px,{pos(i-segment)[1]}px)') for i in range(3,len(demo.route))]
            events.append((100, events[-1][1]))
            css.append(timeline(f'seg{segment}', events))
            visible = [(0, '1' if segment < 4 else '0')]
            if segment >= 4 and segment-4 < len(demo.items):
                visible.append((demo.time(demo.items[segment-4][0])/DURATION*100, '1'))
            visible.append((100,visible[-1][1]))
            css.append(timeline(f'grow{segment}',visible,'opacity',True))
        for n,(i,_) in enumerate(demo.items):
            css.append(timeline(f'item{n}',[(0,'1'),(demo.time(i)/DURATION*100,'0'),(100,'0')],'opacity',True))
        stages = [(0,0)] + [(demo.time(i)/DURATION*100,demo.score(i)) for i,_ in demo.items]
        for n,(p,_) in enumerate(stages):
            end = stages[n+1][0] if n+1<len(stages) else 100
            css.append(timeline(f'score{n}',[(0,'1' if n==0 else '0'),(p,'1'),(end,'0' if end<100 else '1'),(100,'1' if end==100 else '0')],'opacity',True))
        css.append('}@media(prefers-reduced-motion:reduce){.moving{display:none}.still{display:inline}*{animation:none!important}}')
    metadata = json.dumps({'source':calendar.source,'total':calendar.total,'days':[{'date':str(d.date),'count':d.count,'level':d.level} for d in calendar.days]},separators=(',',':'))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
           '<!-- SPDX-License-Identifier: LicenseRef-Arcade-Art-Reserved; Copyright (c) 2026 PedroCostinha -->',
           '<title id="title">Code Snake — Nib no calendário real</title>',
           '<desc id="desc">Demonstração automática. Núcleos marcam dias reais ativos; coletado é a soma desses dias no recorte. Calendário anual completo abaixo. Sem controles.</desc>',
           f'<metadata>{escape(metadata)}</metadata><style>{"".join(css)}</style>',
           '<defs><g id="nib">'+head()+'</g></defs>',
           rect(1,1,width-2,height-2,'#111115','rx="18" stroke="#33232c"'),
           rect(28,30,5,44,'#ed6572'),label(45,47,'ARCADE COLLECTION / 02',11,'#ed8893'),
           label(45,78,'CODE SNAKE',29,'#f4efe6'),
           label(32 if mobile else 48,112,f'NIB / ÚLTIMAS {demo.columns} SEMANAS · DEMO',11),
           rect(left-8,top-8,demo.columns*cell+14,7*cell+14,'#0b0c10','rx="6" stroke="#32252e"')]
    for day in calendar.days:
        x = day.week-demo.offset
        if x >= 0:
            out.append(rect(left+x*cell,top+day.weekday*cell,cell-3,cell-3,PALETTE[day.level]))
    def body(i,segment=0):
        x,y=pos(i)
        color='#a74155' if segment%2 else '#ce5267'
        return rect(x+cell*.18,y+cell*.18,cell*.64,cell*.64,color)+rect(x+cell*.26,y+cell*.25,cell*.36,cell*.12,'#ff8890')
    def head_at(i):
        x,y=pos(i)
        return f'<g transform="translate({x},{y}) scale({cell/12})"><use href="#nib"/></g>'
    static_i = demo.items[-1][0] if demo.items else len(demo.route)//2
    out.append('<g class="still">')
    for s in reversed(range(demo.length(static_i))):
        out.append(body(max(0,static_i-s),s) if s else head_at(static_i))
    out.append('</g><g class="moving curtain">')
    for n,(i,day) in enumerate(demo.items):
        x,y=pos(i)
        out.append(f'<g class="item{n}" data-item-date="{day.date}" data-count="{day.count}"><title>{day.date}: {day.count} contribuições</title><path d="M{x+cell/2} {y+5}l{cell/2-5} {cell/2-5}l{-cell/2+5} {cell/2-5}l{-cell/2+5} {-cell/2+5}z" fill="#efd7a4"/>'+rect(x+cell/2-2,y+cell/2-2,4,4,'#9e535a')+'</g>')
    for s in reversed(range(10)):
        out.append(f'<g class="grow{s}"><g class="seg{s}">')
        out.append(f'<g transform="scale({cell/12})"><use href="#nib"/></g>' if not s else rect(cell*.18,cell*.18,cell*.64,cell*.64,'#ce5267' if s%2==0 else '#a74155')+rect(cell*.26,cell*.25,cell*.36,cell*.12,'#ff8890'))
        out.append('</g></g>')
    out.append('</g>')
    # Annual calendar is always present, unmodified; no contribution disappears on collection.
    cal_top=footer+36 if mobile else 477
    cal_cell=7.7 if mobile else 10
    cal_left=32 if mobile else 48
    out.append(label(cal_left,cal_top-10,'ANO COMPLETO / CONTRIBUIÇÕES REAIS',10))
    for day in calendar.days:
        out.append(rect(cal_left+day.week*cal_cell,cal_top+day.weekday*cal_cell,cal_cell-1.5,cal_cell-1.5,PALETTE[day.level],f'data-date="{day.date}" data-count="{day.count}"') .replace('/>',f'><title>{day.date}: {day.count} contribuições</title></rect>'))
    hudx=32 if mobile else 660
    hudy=355 if mobile else 490
    out += [label(hudx,hudy,f'{calendar.total} NO ANO',16,'#f4efe6'),label(hudx,hudy+23,f'{calendar.days[0].date} → {calendar.days[-1].date}',10)]
    out.append('<g class="still">'+label(hudx,hudy+47,f'COLETADO {demo.score(static_i)}',13,'#ed8893')+'</g><g class="moving">')
    for n,value in enumerate([0]+[demo.score(i) for i,_ in demo.items]):
        out.append(f'<g class="score{n}">'+label(hudx,hudy+47,f'COLETADO {value}',13,'#ed8893')+'</g>')
    out += ['</g><g class="moving curtain"><g class="complete">',label(hudx,hudy+67,'RECORTE CONCLUÍDO',10,'#efd7a4'),'</g></g>',label(32 if mobile else 48,height-13,'SNAPSHOT REAL · LOOP 18s · PROTÓTIPO',10),'</svg>']
    result=''.join(out)
    validate_svg(result,calendar,static=static)
    return result

def validate_svg(svg,calendar,*,static=False):
    root=ET.fromstring(svg)
    if len(svg.encode())>350_000:
        raise ValueError('SVG over budget')
    if static and ('@keyframes' in svg or 'animation:' in svg):
        raise ValueError('Static output contains motion')
    for e in root.iter():
        if e.tag.split('}')[-1] in ('script','foreignObject','image'):
            raise ValueError('Forbidden element')
        for k,v in e.attrib.items():
            if k.lower().startswith('on') or (k.endswith('href') and not v.startswith('#')):
                raise ValueError('External or executable resource')
    days=[(e.get('data-date'),int(e.get('data-count'))) for e in root.iter() if e.get('data-date')]
    if days != [(str(d.date),d.count) for d in calendar.days]:
        raise ValueError('Calendar dates/counts changed')
