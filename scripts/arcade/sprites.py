"""Ember-7: original 16x20 pixel courier robot, drawn with simple pixel blocks."""

from .barrel import POSES

PALETTE = {'s': '#411E2B', 'r': '#D94954', 'l': '#FA7777', 'v': '#EDF1ED',
           'd': '#222631', 'g': '#9095A7', 'a': '#E6B976'}


def sprite_grid(pose):
    if pose not in POSES:
        raise ValueError('Unknown Ember-7 pose')
    grid = [['.' for _ in range(16)] for _ in range(20)]

    def block(x, y, w, h, color):
        for row in range(y, y+h):
            for col in range(x, x+w):
                grid[row][col] = color

    block(7, 0, 1, 2, 'g')
    block(7, 0, 2, 1, 'a')
    block(4, 2, 8, 6, 's')
    block(5, 2, 6, 1, 'l')
    block(4, 3, 8, 3, 'r')
    block(6, 4, 6, 2, 'd')
    block(8, 4, 3, 1, 'v')
    block(6, 7, 4, 2, 'g')
    block(4, 9, 8, 6, 's')
    block(5, 9, 6, 5, 'r')
    block(6, 10, 3, 2, 'v')
    block(6, 12, 3, 1, 'l')
    block(3, 10, 2, 4, 'g')  # backpack hinge
    block(2, 10, 2, 4, 'd')
    phase = int(pose[-1]) if pose[-1].isdigit() else 0
    if pose.startswith('climb'):
        block(3, 6+phase*4, 2, 6, 'g')
        block(11, 10-phase*4, 2, 6, 'g')
        block(5, 15, 2, 3+phase, 'g')
        block(9, 15, 2, 4-phase, 'g')
        block(4, 17+phase, 4, 1, 'v')
        block(8, 18-phase, 4, 1, 'v')
    elif pose == 'jump':
        block(11, 7, 2, 5, 'g')
        block(12, 6, 2, 2, 'v')
        block(4, 15, 3, 2, 'g')
        block(3, 16, 3, 2, 'v')
        block(9, 15, 3, 2, 'g')
        block(10, 16, 3, 2, 'v')
    else:
        stride = (0, 2, 0, -2)[phase] if pose.startswith('run') else (1 if phase else 0)
        arm_y = 9 if pose == 'victory' else (10+phase%3 if pose.startswith('run') else 11)
        block(11, arm_y, 2, 4, 'g')
        if pose == 'victory':
            block(12, 6, 2, 4, 'g')
            block(12, 5, 2, 2, 'v')
        block(5-stride, 15, 3, 3, 'g')
        block(9+stride, 15, 2, 3, 'g')
        block(4-stride, 18, 4, 2, 'v')
        block(9+stride, 18, 4, 2, 'v')
    return grid


def sprite_defs():
    out = []
    for pose in POSES:
        grid = sprite_grid(pose)
        out.append(f'<g id="ember-{pose}" shape-rendering="crispEdges">')
        for color, fill in PALETTE.items():
            path = []
            for y, row in enumerate(grid):
                for x, pixel in enumerate(row):
                    if pixel == color:
                        path.append(f'M{2*x-16} {2*y-40}h2v2h-2z')
            out.append(f'<path fill="{fill}" d="{"".join(path)}"/>')
        out.append('</g>')
    out.append('<g id="barrel" shape-rendering="crispEdges">'
               '<path fill="#401D29" d="M-6-9H6v2h3V7H6v2H-6V7h-3V-7h3z"/>'
               '<path fill="#B45356" d="M-5-7H5V7H-5z"/>'
               '<path fill="#ED9290" d="M-8-5H8v2H-8zM-8 3H8v2H-8z"/>'
               '<path fill="#512736" d="M-2-7h2V7h-2zM3-7h2V7H3z"/></g>')
    return ''.join(out)
