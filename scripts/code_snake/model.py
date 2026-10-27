# SPDX-License-Identifier: MIT
# Copyright (c) 2026 PedroCostinha
from dataclasses import dataclass

DURATION = 18
TRAVEL = 14
START = 1

@dataclass(frozen=True)
class Replay:
    route: tuple
    items: tuple
    columns: int
    offset: int

    def time(self, index):
        return START + TRAVEL * (index - 3) / (len(self.route) - 4)

    def score(self, index):
        return sum(day.count for step, day in self.items if step <= index)

    def length(self, index):
        return 4 + sum(step <= index for step, _ in self.items)

def replay(calendar, mobile=False):
    columns = min(16 if mobile else 24, calendar.weeks)
    offset = calendar.weeks - columns
    days = {(d.week - offset, d.weekday): d for d in calendar.days if d.week >= offset}
    # Full rectangular route stays on the grid; missing partial-week days are not items.
    route = tuple((x, y) for x in range(columns) for y in (range(7) if x % 2 == 0 else range(6, -1, -1)))
    candidates = [(i, days[p]) for i, p in enumerate(route) if i >= 12 and p in days and days[p].count]
    items = []
    for i, day in candidates:
        if not items or i - items[-1][0] >= 12:
            items.append((i, day))
        if len(items) == 6:
            break
    return Replay(route, tuple(items), columns, offset)
