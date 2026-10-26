"""Self-contained CSS/SVG arcade card; no runtime script or remote assets."""

from html import escape
import json
import re
import xml.etree.ElementTree as ET

from code_quest.sprites import pixel_text
from .barrel import Demo, DURATION, FINISH, PHASES, POSES, barrel, barrel_boundaries, barrel_rotation, floor_y
from .sprites import sprite_defs

WIDTH, HEIGHT = 1200, 650
BUDGET = 250_000


def rect(x, y, w, h, fill, extra=''):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" {extra}/>'


def text(x, y, value, size=14, fill='#A1A0AB', extra=''):
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{fill}" {extra}>{escape(str(value))}</text>'


def timeline(name, events, prop='opacity', discrete=False):
    frames = ''.join(f'{100*t/DURATION:.5f}%{{{prop}:{value}}}' for t, value in sorted(dict(events).items()))
    return (f'@keyframes {name}{{{frames}}}.{name}{{animation:{name} {DURATION:g}s '
            f'{"steps(1,end)" if discrete else "linear"} infinite}}')


def styles(demo, static):
    base = ('svg{background:#0D0D0F;max-width:100%;height:auto}'
            'text{font-family:ui-monospace,Consolas,monospace}'
            '.moving{display:none}.still{display:inline}.pose{opacity:0}'
            '.scoreframe{opacity:0}.terminal{fill:#EF7774}')
    if static:
        return base
    css = [base, '@media(prefers-reduced-motion:no-preference){'
           '.moving{display:inline}.still{display:none}.terminal{fill:#632A37}'
           f'.cinematic{{animation:curtain {DURATION:g}s linear infinite}}'
           '@keyframes curtain{0%,100%{opacity:0}3%,93%{opacity:1}98%{opacity:0}}']
    samples = demo.samples()
    css.append(timeline('runner', [(t, f'translate({demo.position(t)[0]:.3f}px,{demo.position(t)[1]:.3f}px)')
                                   for t in samples], 'transform'))
    css.append(timeline('facing', [(t, f'scaleX({demo.facing(t)})') for t in samples
                                    if t in (0, DURATION) or demo.facing(t) != demo.facing(max(0,t-1/24))],
                        'transform', True))
    for pose in POSES:
        events, previous = [], None
        for t in samples:
            value = int(demo.pose(t) == pose)
            if previous != value:
                events.append((t, value))
                previous = value
        events.append((DURATION, int(demo.pose(DURATION) == pose)))
        css.append(timeline('pose-'+pose, events, discrete=True))
    for index, phase in enumerate(PHASES):
        times = sorted(barrel_boundaries(phase))
        css.append(timeline(f'barrel{index}', [(t, f'translate({barrel(t,phase)[0]:.3f}px,{barrel(t,phase)[1]:.3f}px)')
                                              for t in times], 'transform'))
        css.append(timeline(f'visible{index}', [(t, int(barrel(t,phase)[2])) for t in times], discrete=True))
        css.append(timeline(f'spin{index}', [(t,f'rotate({barrel_rotation(t,phase):.3f}deg)') for t in times],'transform'))
    for index, stage in enumerate(demo.stages):
        css.append(timeline(f'chip{index}', [(0,1),(stage.collected,0),(DURATION,0)], discrete=True))
    for index in range(6):
        begin = demo.stages[index-1].collected if index else 0
        end = demo.stages[index].collected if index < 5 else DURATION
        css.append(timeline(f'score{index}', [(0,int(index==0)), (begin,1),
                                             (end,int(index==5)), (DURATION,int(index==5))], discrete=True))
    css.append(timeline('complete', [(0,0),(FINISH,1),(DURATION,1)], discrete=True))
    css.append('}@media(prefers-reduced-motion:reduce){*{animation:none!important}'
               '.moving{display:none}.still{display:inline}}')
    return ''.join(css)


def platforms():
    out = []
    # Structural background, subdued enough to keep the route readable.
    out.append(rect(808,194,5,382,'#201B24'))
    for x in (112, 360, 608):
        out.append(rect(x, 194, 5, 382, '#201B24'))
        out.append(f'<path d="M{x} 238l248 84m-248 0l248 84m-248 0l248 84" stroke="#201B24" fill="none"/>')
    for floor in range(5):
        # The ladder opens a 34px hatch in the destination platform. Feet on
        # either side remain supported; the runner steps off the ladder onto it.
        hatch = (760 if floor % 2 else 160) if floor else None
        spans = [(100, hatch-17), (hatch+17,820)] if hatch else [(100,820)]
        out.append(f'<g data-platform="{floor}">')
        for a,b in spans:
            y1,y2 = floor_y(floor,a),floor_y(floor,b)
            out.append(f'<path d="M{a} {y1:g}L{b} {y2:g}v10L{a} {y1+10:g}z" fill="#52222F"/>')
            out.append(f'<path d="M{a} {y1:g}L{b} {y2:g}" stroke="#EC5D65" stroke-width="3"/>')
            for x in range(int(a)+8,int(b)-4,24):
                out.append(rect(x, floor_y(floor,x)+4, 8, 2, '#9B3F4C'))
        out.append('</g>')
        if floor < 4:
            x = 760 if floor % 2 == 0 else 160
            top,bottom = floor_y(floor+1,x),floor_y(floor,x)
            out.append(f'<g data-ladder="{floor}" fill="#99818E">')
            out.extend((rect(x-13,top-4,3,bottom-top+4,'#99818E'),
                        rect(x+10,top-4,3,bottom-top+4,'#99818E')))
            for y in range(round(top)+3,round(bottom),10):
                out.append(rect(x-10,y,20,2,'#A17C89'))
            out.append('</g>')
        out.append(text(62, floor_y(floor,100)+5, f'{floor+1:02}', 12, '#806573'))
    return ''.join(out)


def render(calendar, *, static=False):
    demo = Demo(calendar)
    first, last = calendar.days[0].date, calendar.days[-1].date
    active = sum(d.count > 0 for d in calendar.days)
    metadata = dict(game='barrel-quest', version=1, login='PedroCostinha', source=calendar.source,
                    first=str(first), last=str(last), total=calendar.total, active_days=active)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
           f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">',
           '<title id="title">Barrel Quest — ARCADE COLLECTION</title>',
           f'<desc id="description">Ember-7, robô original, sobe cinco rampas e quatro escadas, '
           f'salta barris e recolhe pontos de cinco trechos cronológicos do calendário real de PedroCostinha. '
           f'{first} a {last}: {calendar.total} contribuições, {active} dias ativos. '
           + ('Versão estática, placar final.' if static else
              'Demonstração automática de 32 segundos, reinício com fade; movimento reduzido mostra o placar final.')
           + ' Pontos são contribuições agregadas; não representam novos commits.</desc>',
           f'<metadata>{escape(json.dumps(metadata, sort_keys=True))}</metadata>',
           '<defs>', sprite_defs(), '</defs><style>', styles(demo, static), '</style>',
           rect(.5,.5,1199,649,'#0D0D0F','rx="16" stroke="#33242E"'),
           rect(32,32,4,79,'#ED5A62'),
           pixel_text('ARCADE COLLECTION',54,32,1.5,'#A98B98'),
           pixel_text('BARREL QUEST',52,57,4.0,'#F0E9ED'),
           text(54,110,'EMBER-7 / INDUSTRIAL ASCENT',13,'#EB767D'),
           text(1146,47,'01 / ORIGINAL ARCADE',13,'#B09AA5','text-anchor="end"'),
           text(1146,77,'DEMO / PROTOTYPE',12,'#A1A0AB','text-anchor="end"'),
           rect(32,130,1136,1,'#30232D'),
           text(54,147,'SUBA. DESVIE. ENTREGUE.',13,'#AE939E'),
           text(848,147,'5 PISOS',12,'#AE939E','text-anchor="end"'),
           rect(46,155,816,432,'#131017','rx="8" stroke="#32212D"'),
           rect(888,155,266,432,'#151117','rx="8" stroke="#3E2734"')]
    # Original dispenser and delivery station; no franchise character silhouettes.
    out.extend([rect(783,183,44,21,'#4C2736'),rect(789,187,32,9,'#9A4653'),
                rect(792,196,26,7,'#22202A'), text(774,171,'CHUTE',10,'#9B7D8C'), platforms()])
    for index,stage in enumerate(demo.stages):
        x,y = stage.terminal_x,floor_y(index,stage.terminal_x)
        out.append(f'<g data-stage="{index}" data-first="{stage.days[0].date}" '
                   f'data-last="{stage.days[-1].date}" data-points="{stage.points}" '
                   f'data-collected="{stage.collected:.6f}">')
        out.extend([rect(x-10,y-22,20,20,'#24202A'),rect(x-7,y-19,14,8,'#632A37','class="terminal"'),
                    rect(x-4,y-8,8,2,'#AE7E90'),'</g>'])
        if stage.points:
            out.append(f'<g class="moving cinematic"><g class="chip{index}">')
            out.append(f'<path d="M{x-5:g} {y-32:g}h10v8h-10z" fill="#ECC58A"/>')
            out.append('</g></g>')
    out.append('<g class="moving cinematic">')
    for index,_ in enumerate(PHASES):
        out.append(f'<g class="barrel{index}"><g class="visible{index}"><g class="spin{index}">'
                   '<use href="#barrel"/></g></g></g>')
    out.append('<g class="runner"><g class="facing">')
    for pose in POSES:
        out.append(f'<g class="pose pose-{pose}"><use href="#ember-{pose}"/></g>')
    out.append('</g></g></g>')
    out.append(f'<g class="still" transform="translate(760 {floor_y(4,760):g})"><use href="#ember-victory"/></g>')
    out.extend([text(910,208,'DELIVERY SCORE',13,'#B999A9'),
                '<g class="moving cinematic">'])
    for index in range(6):
        score = sum(s.points for s in demo.stages[:index])
        out.append(text(910,254,f'{score:06}',36,'#F1E8EC',f'class="scoreframe score{index}" data-score="{score}"'))
    out.extend(['</g>',text(910,254,f'{calendar.total:06}',36,'#F1E8EC','class="still"'),
                text(910,280,'1 CONTRIBUICAO = 1 PONTO',11,'#D9939F'),
                rect(910,300,222,1,'#3A2732'),
                text(910,327,f'{active} DIAS ATIVOS',16,'#D5BDC9'),
                text(910,353,'CARGA POR TRECHO',12,'#A58B99')])
    for index,stage in enumerate(demo.stages):
        y=381+index*31
        out.extend([text(910,y,f'{index+1:02}',12,'#D9939F'),
                    rect(944,y-10,100,7,'#2C202A'),
                    rect(944,y-10,100*stage.points/max(1,calendar.total),7,'#C74B5C'),
                    text(1132,y,stage.points,14,'#E9DCE4','text-anchor="end"')])
    out.extend([text(910,560,'DADOS REAIS / GITHUB',11,'#A58B99'),
                # Separate nodes prevent the completion timeline from replacing
                # the cinematic fade through the CSS animation shorthand.
                '<g class="moving cinematic"><g class="complete">',
                rect(315,180,280,33,'#231923','rx="3" stroke="#82404F"'),
                text(455,202,'ENTREGAS CONCLUIDAS',15,'#F0C38E','text-anchor="middle"'),'</g></g>',
                text(54,612,f'{first} / {last}',14,'#B8A2AF'),
                text(1146,612,calendar.source,12,'#A58B99','text-anchor="end"'),
                text(54,635,'Original pixel art / Pontuacao baseada no snapshot de contribuicoes.',12,'#887481'),
                '</svg>'])
    svg = ''.join(out)
    validate_svg(svg,calendar)
    return svg


def validate_svg(svg, calendar):
    if len(svg.encode('utf-8')) > BUDGET:
        raise ValueError('Arcade SVG exceeds 250 kB budget')
    if '<!DOCTYPE' in svg.upper() or '<!ENTITY' in svg.upper():
        raise ValueError('XML declarations are not allowed')
    root = ET.fromstring(svg)
    if root.tag != '{http://www.w3.org/2000/svg}svg' or root.get('viewBox') != f'0 0 {WIDTH} {HEIGHT}':
        raise ValueError('Invalid SVG root or dimensions')
    allowed = {'svg','title','desc','metadata','defs','g','path','rect','text','use','style'}
    ids = [e.get('id') for e in root.iter() if e.get('id')]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate SVG IDs')
    for element in root.iter():
        if element.tag.split('}')[-1] not in allowed:
            raise ValueError('Unsupported SVG element')
        for key,value in element.attrib.items():
            name = key.split('}')[-1].lower()
            if name.startswith('on') or name == 'style':
                raise ValueError('Inline handlers/styles are not permitted')
            if name == 'href' and (not value.startswith('#') or value[1:] not in ids):
                raise ValueError('External or broken SVG reference')
    if re.search(r'url\s*\(|@import|@font-face|https?:|data:', svg, re.I):
        # Namespace is the sole URL allowed; all drawings use local <use> refs.
        stripped = svg.replace('xmlns="http://www.w3.org/2000/svg"','')
        if re.search(r'url\s*\(|@import|@font-face|https?:|data:', stripped, re.I):
            raise ValueError('External SVG resources are not permitted')
    demo = Demo(calendar)
    stages = [e for e in root.iter() if e.get('data-stage') is not None]
    expected = [(str(s.floor),str(s.days[0].date),str(s.days[-1].date),str(s.points),f'{s.collected:.6f}') for s in demo.stages]
    actual = [(e.get('data-stage'),e.get('data-first'),e.get('data-last'),e.get('data-points'),e.get('data-collected')) for e in stages]
    if actual != expected:
        raise ValueError('Stage data differs from real calendar')
    metadata = json.loads(root.find('{http://www.w3.org/2000/svg}metadata').text)
    expected_metadata = dict(game='barrel-quest',version=1,login='PedroCostinha',source=calendar.source,
                             first=str(calendar.days[0].date),last=str(calendar.days[-1].date),
                             total=calendar.total,active_days=sum(d.count>0 for d in calendar.days))
    if metadata != expected_metadata:
        raise ValueError('SVG provenance differs from real calendar')
