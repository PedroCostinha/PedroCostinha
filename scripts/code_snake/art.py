# SPDX-License-Identifier: LicenseRef-Arcade-Art-Reserved
# Copyright (c) 2026 PedroCostinha. All rights reserved.
PALETTE = ('#191a20', '#28232d', '#642b3b', '#aa3d51', '#ed6572')
HEAD = (
    '............', '....rr......', '....rr......', '..llllllll..',
    '.lrrrrrrrrs.', '.rrddddddrr.', '.rrdvvdvvrr.', '.rrdvvdvvrr.',
    '.rrddddddrr.', '..rrrrrrrr..', '...ssrrss...', '............',
)
COLORS = {'r': '#c84c60', 'l': '#ff8890', 's': '#642b3b', 'd': '#191a20', 'v': '#f4efe6'}

def head():
    return ''.join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{COLORS[p]}"/>'
                   for y, row in enumerate(HEAD) for x, p in enumerate(row) if p != '.')
