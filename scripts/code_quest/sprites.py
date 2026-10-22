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
            for col, pixel in enumerate(pixels):
                if pixel == '1':
                    commands.append(f'M{index * 6 + col} {row}h1v1h-1z')
    return (f'<g aria-label="{escape(text)}" class="{css}" transform="translate({x:g} {y:g}) scale({scale:g})">'
            f'<path fill="{color}" d="{"".join(commands)}"/></g>')


PALETTE = {'o':'#09090D', 'r':'#E53935', 's':'#A71D2A', 'h':'#FF7770',
           'v':'#E8DAC5', 'w':'#F2F2F2', 'd':'#353542', 'l':'#666675', 'g':'#C9A35D'}
TORSO = [
    '      ooooo     ',
    '     orrrrro    ',
    '    orhrrrrro   ',
    '    orrrrrrro   ',
    '    ossvvvvvo   ',
    '    ovvvvvwvo   ',
    '     ovvvvovo   ',
    '     oovvvoo    ',
    '   oosrrrro     ',
    '  osoddddooo    ',
    '  osodldddlo    ',
    '  osodlddddo    ',
    '   oodddgddo    ',
    '    oddddddo    ',
]
LEGS = {
    'run0':['    oddooddo    ','   oddo  oddo   ','  oddo    oddo  ','  olo      olo  ',' ooowo    oowwo ',' ooooo    ooooo '],
    'run1':['     oddddo     ','      oddo      ','     odddo      ','    oddlo       ','    owwwo       ','    ooooo       '],
    'run2':['    oddooddo    ','   oddo  oddo   ','  oddo    oddo  ','  olo      olo  ',' owwwo    owwoo ',' ooooo    ooooo '],
    'run3':['     oddddo     ','      oddo      ','      odddo     ','       olddo    ','       owwwo    ','       ooooo    '],
    'idle':['    oddooddo    ','    oddooddo    ','    oddooddo    ','    oloooloo    ','   owwwoowwwo   ','   oooooooooo   '],
    'jump':['    odddddo     ','    oddooddo    ','     oo  oddo   ','          olo   ','         owwwo  ','         ooooo  '],
    'fall':['    oddooddo    ','    oddooddo    ','    oddooddo    ','    oloooloo    ','    owwoowwo    ','    oooo oooo   '],
    'land':['    odddddo     ','   oddo oddo    ','   olo   olo    ','  owwwo owwwo   ','  ooooo ooooo   ','                '],
}


def sprite_defs():
    result = []
    for pose in ('idle', 'run0', 'run1', 'run2', 'run3', 'jump', 'fall', 'land', 'collect', 'celebrate'):
        grid = [list(row.ljust(16)) for row in TORSO + LEGS.get(pose, LEGS['idle'])]
        if pose in ('jump', 'collect', 'celebrate'):
            for x, y in ((12, 8), (13, 7), (14, 6), (14, 5)):
                grid[y][x] = 'v' if y < 7 else 'd'
        if pose == 'celebrate':
            for x, y in ((3, 8), (2, 7), (1, 6), (1, 5)):
                grid[y][x] = 'v' if y < 7 else 'd'
        if pose.startswith('run'):
            phase = int(pose[-1])
            for x, y in ((12, 10), (13, 11 if phase % 2 else 9), (14, 12 if phase % 2 else 8)):
                grid[y][x] = 'v' if x == 14 else 'd'
        result.append(f'<g id="sprite-{pose}" transform="translate(-16 -40) scale(2)" shape-rendering="crispEdges">')
        for char, color in PALETTE.items():
            path = []
            for y, row in enumerate(grid):
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
            result.append(f'<path fill="{color}" d="{"".join(path)}"/>')
        result.append('</g>')
    result.append('<g id="coin"><path fill="#8C652A" d="M-3-8H3V-6H6V6H3V8H-3V6H-6V-6H-3Z"/>'
                  '<path fill="#E3BA61" d="M-2-7H2V-5H4V5H2V7H-2V5H-4V-5H-2Z"/>'
                  '<path fill="#FFF0B5" d="M-1-4H1V4H-1Z"/></g>')
    return ''.join(result)
