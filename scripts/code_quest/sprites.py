"""Original pixel explorer and a tiny, self-contained 5×7 vector alphabet."""

from html import escape

GLYPHS = {
    'A':'01110/10001/10001/11111/10001/10001/10001',
    'B':'11110/10001/10001/11110/10001/10001/11110',
    'C':'01111/10000/10000/10000/10000/10000/01111',
    'D':'11110/10001/10001/10001/10001/10001/11110',
    'E':'11111/10000/10000/11110/10000/10000/11111',
    'F':'11111/10000/10000/11110/10000/10000/10000',
    'G':'01111/10000/10000/10111/10001/10001/01111',
    'H':'10001/10001/10001/11111/10001/10001/10001',
    'I':'11111/00100/00100/00100/00100/00100/11111',
    'J':'00111/00010/00010/00010/10010/10010/01100',
    'K':'10001/10010/10100/11000/10100/10010/10001',
    'L':'10000/10000/10000/10000/10000/10000/11111',
    'M':'10001/11011/10101/10101/10001/10001/10001',
    'N':'10001/11001/10101/10011/10001/10001/10001',
    'O':'01110/10001/10001/10001/10001/10001/01110',
    'P':'11110/10001/10001/11110/10000/10000/10000',
    'Q':'01110/10001/10001/10001/10101/10010/01101',
    'R':'11110/10001/10001/11110/10100/10010/10001',
    'S':'01111/10000/10000/01110/00001/00001/11110',
    'T':'11111/00100/00100/00100/00100/00100/00100',
    'U':'10001/10001/10001/10001/10001/10001/01110',
    'V':'10001/10001/10001/10001/10001/01010/00100',
    'W':'10001/10001/10001/10101/10101/10101/01010',
    'X':'10001/10001/01010/00100/01010/10001/10001',
    'Y':'10001/10001/01010/00100/00100/00100/00100',
    'Z':'11111/00001/00010/00100/01000/10000/11111',
    '0':'01110/10001/10011/10101/11001/10001/01110',
    '1':'00100/01100/00100/00100/00100/00100/01110',
    '2':'01110/10001/00001/00010/00100/01000/11111',
    '3':'11110/00001/00001/01110/00001/00001/11110',
    '4':'00010/00110/01010/10010/11111/00010/00010',
    '5':'11111/10000/10000/11110/00001/00001/11110',
    '6':'01110/10000/10000/11110/10001/10001/01110',
    '7':'11111/00001/00010/00100/01000/01000/01000',
    '8':'01110/10001/10001/01110/10001/10001/01110',
    '9':'01110/10001/10001/01111/00001/00001/01110',
    '!':'00100/00100/00100/00100/00100/00000/00100',
    '-':'00000/00000/00000/11111/00000/00000/00000',
    '/':'00001/00001/00010/00100/01000/10000/10000',
    '.':'00000/00000/00000/00000/00000/00110/00110',
    ':':'00000/00100/00100/00000/00100/00100/00000',
}


def pixel_text(text, x, y, scale=1, color='#F2F2F2', css='', anchor='start'):
    width = max(0, len(text) * 6 - 1) * scale
    if anchor == 'end':
        x -= width
    if anchor == 'middle':
        x -= width / 2
    commands = []
    for index, char in enumerate(text.upper()):
        for row, pixels in enumerate(GLYPHS.get(char, '').split('/')):
            col = 0
            while col < len(pixels):
                if pixels[col] != '1':
                    col += 1
                    continue
                end = col + 1
                while end < len(pixels) and pixels[end] == '1':
                    end += 1
                width = end-col
                commands.append(f'M{index * 6 + col} {row}h{width}v1h-{width}z')
                col = end
    return (f'<g aria-label="{escape(text)}" class="{css}" transform="translate({x:g} {y:g}) scale({scale:g})">'
            f'<path fill="{color}" d="{"".join(commands)}"/></g>')


# 20 x 24 source pixels, enlarged to 35 x 42 SVG units. No commercial sprites.
from .motion import POSES, SPRITE_HEIGHT

SPRITE_SCALE = 1.75
PALETTE = {'o':'#09090D', 'r':'#D94A4A', 's':'#96313E', 'h':'#FF8276',
           'v':'#EAC8A5', 'k':'#B78473', 'w':'#E6EDF3', 'd':'#252631',
           'l':'#484B60', 'b':'#15151E', 'g':'#D4AB60', 't':'#888C9F'}
TORSO = (
    '       oooooo',
    '      orhhhrrro',
    '     orrrrrrrrro',
    '     osrrrrrrrrro',
    '     ossssrrrrrrro',
    '      okvvvvvooo',
    '      ovvvvwvvo',
    '      okvvvovvo',
    '       okvvvvo',
    '      oossssoo',
    '     osrdldddlo',
    '     osodlddddo',
    '      oodlgdddo',
    '       odddddo',
    '       olggglo',
    '       obbbbbo',
)
LEGS = {
    'idle': ('       oddoddo','       oddoddo','       oldodlo','       oddoddo',
             '       obbodbo','      otwwotwwo','      oooo oooo','      oooo oooo'),
    'run0': ('      oddooddo','     oddo  oddo','    oldo    odlo','   oddo      oddo',
             '  obbo        obbo',' otwwo        otwwo',' ooooo        ooooo',' ooooo        ooooo'),
    'run1': ('       oddddo','      oddooddo','     oldo  oddo','    oddo    oddo',
             '   obbo    obbo','  otwwo   otwwo','  ooooo   ooooo','          ooooo'),
    'run2': ('       oddddo','       oddoddo','        oldoddo','       oddo obbo',
             '      obbo otwwo','     otwwo ooooo','     ooooo','     ooooo'),
    'run3': ('      oddooddo','     oddo  oddo','    oldo    odlo','   oddo      oddo',
             '  obbo        obbo',' otwwwo       otwwo',' oooooo       ooooo',' oooooo       ooooo'),
    'run4': ('       oddddo','      oddooddo','      oddo  oldo','     oddo    oddo',
             '     obbo     obbo','    otwwo    otwwo','    ooooo    ooooo','    ooooo'),
    'run5': ('       oddddo','      oddoddo','     oddodlo','    obbo oddo',
             '   otwwo  obbo','   ooooo otwwo','         ooooo','         ooooo'),
    'jump': ('       odddddo','      oddoodddo','     oddo  odddo','     obbo   oldo',
             '     otwwo  obbo','     ooooo otwwo','           ooooo','           ooooo'),
    'apex': ('      oddddddo','     oddooodddo','    oddo   odddo','    obbo    obbo',
             '    otwwo   otwwo','    ooooo   ooooo','            ooooo','            ooooo'),
    'fall': ('       oddoddo','       oldodlo','       oddoddo','       oddoddo',
             '      obbo obbo','     otwwo otwwo','     ooooo ooooo','     ooooo ooooo'),
    'land': ('      odddddddo','     oldo   odlo','     obbo   obbo','    otwwo   otwwo',
             '    ooooo   ooooo','    ooooo   ooooo'),
}


def sprite_grid(pose):
    legs = LEGS.get(pose, LEGS['idle'])
    torso = list(TORSO)
    if pose in ('accelerate', 'run1', 'run2', 'run4', 'run5'):
        torso = [' ' + row for row in torso]
    if pose == 'land':
        torso = ['',''] + torso
    grid = [list(row.ljust(20)) for row in torso + list(legs)]
    if len(grid) != 24 or any(len(row) != 20 for row in grid):
        raise ValueError('Sprite must fit its 20 x 24 source grid')
    # Articulated arms swing in opposition to the legs; gloves have dark outlines.
    phase = int(pose[-1]) if pose.startswith('run') else 0
    if pose.startswith('run') or pose == 'accelerate':
        arms = ([(5,11),(4,12),(3,13),(14,10),(15,9),(16,9)] if phase < 3 else
                [(5,10),(4,9),(3,9),(14,11),(15,12),(16,13)])
    elif pose in ('jump','apex','collect','victory','celebrate'):
        arms = [(14,10),(15,9),(16,8),(16,7),(16,6)]
        if pose in ('apex','victory','celebrate'):
            arms += [(5,10),(4,9),(3,8),(3,7),(3,6)]
    else:
        arms = [(5,11),(5,12),(5,13),(14,11),(14,12),(14,13)]
    for i,(x,y) in enumerate(arms):
        for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
            if grid[y+dy][x+dx] == ' ':
                grid[y+dy][x+dx] = 'o'
        grid[y][x] = 'v' if i in (2,5,len(arms)-1) else 'l'
    return grid


def sprite_defs():
    result = []
    for pose in POSES:
        grid = sprite_grid(pose)
        result.append(f'<g id="sprite-{pose}" transform="translate(-17.5 -{SPRITE_HEIGHT}) scale({SPRITE_SCALE})" shape-rendering="crispEdges">')
        for char, color in PALETTE.items():
            path = []
            for y,row in enumerate(grid):
                x = 0
                while x < len(row):
                    if row[x] != char:
                        x += 1
                        continue
                    end = x + 1
                    while end < len(row) and row[end] == char:
                        end += 1
                    path.append(f'M{x} {y}h{end-x}v1h{x-end}z')
                    x = end
            if path:
                result.append(f'<path fill="{color}" d="{"".join(path)}"/>')
        result.append('</g>')
    result.append('<g id="coin" shape-rendering="crispEdges">'
                  '<path fill="#6A4328" d="M-3-9H3V-7H6V7H3V9H-3V7H-6V-7H-3Z"/>'
                  '<path fill="#D4A347" d="M-3-8H3V-6H5V6H3V8H-3V6H-5V-6H-3Z"/>'
                  '<path fill="#F5D57C" d="M-2-7H2V-5H3V5H2V7H-2V5H-3V-5H-2Z"/>'
                  '<path fill="#AF7933" d="M0-4H2V4H0ZM-2 4H0V6H-2Z"/>'
                  '<path fill="#FFF0BF" d="M-2-5H0V2H-2ZM-3-6H0V-5H-3Z"/></g>')
    return ''.join(result)
