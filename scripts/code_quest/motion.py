"""Deterministic geometry shared by rendering, sprites, coins and tests."""

from dataclasses import dataclass
import math

DURATION = 20.8
START = 1.6
FINISH = 17.2
GRID_X = 116
GRID_Y = 318
GRID_WIDTH = 954
GROUND = 302


@dataclass(frozen=True)
class Platform:
    x: float
    end: float
    y: float
    level: int
    first_week: int


@dataclass(frozen=True)
class Jump:
    x: float
    end: float
    y: float
    end_y: float
    height: float

    def feet(self, x):
        u = (x - self.x) / (self.end - self.x)
        return self.y + (self.end_y - self.y) * u - 4 * self.height * u * (1 - u)


@dataclass(frozen=True)
class Coin:
    x: float
    y: float
    collected: float


class Route:
    def __init__(self, calendar):
        self.pitch = GRID_WIDTH / calendar.weeks
        self.platforms = []
        starts = list(range(0, calendar.weeks, 4))
        if calendar.weeks - starts[-1] < 3:
            starts.pop()
        for w, end_week in zip(starts, starts[1:] + [calendar.weeks]):
            level = max((d.level for d in calendar.days if w <= d.week < end_week), default=0)
            self.platforms.append(Platform(GRID_X + w * self.pitch,
                                          GRID_X + end_week * self.pitch - 5,
                                          GROUND - level * 6, level, w))
        self.left, self.right = 78, 1116
        self.speed = (self.right - self.left) / (FINISH - START)
        self.jumps = []
        first, last = self.platforms[0], self.platforms[-1]
        self.jumps.append(Jump(86, first.x + 22, GROUND, first.y, 32 + abs(GROUND - first.y)))
        for previous, following in zip(self.platforms, self.platforms[1:]):
            # Twenty-two pixels of approach/landing clearance protect the 24px-wide sprite.
            self.jumps.append(Jump(previous.end - 22, following.x + 22, previous.y, following.y,
                                   30 + abs(previous.y - following.y)))
        self.jumps.append(Jump(last.end - 22, 1100, last.y, GROUND, 32 + abs(last.y - GROUND)))
        self.coins = []
        for platform in self.platforms:
            if platform.level >= 3:
                x = (platform.x + platform.end) / 2
                self.coins.append(Coin(x, self.feet_at(x) - 25, self.time_at(x)))

    def time_at(self, x):
        return START + (x - self.left) / self.speed

    def x_at(self, seconds):
        return min(self.right, max(self.left, self.left + (seconds - START) * self.speed))

    def feet_at(self, x):
        for jump in self.jumps:
            if jump.x <= x <= jump.end:
                return jump.feet(x)
        for platform in self.platforms:
            if platform.x <= x <= platform.end:
                return platform.y
        return GROUND

    def pose(self, seconds):
        if seconds < START or seconds >= FINISH:
            return 'celebrate' if 17.65 <= seconds < 20 else 'idle'
        x = self.x_at(seconds)
        for jump in self.jumps:
            if jump.x <= x <= jump.end:
                u = (x - jump.x) / (jump.end - jump.x)
                return 'jump' if u < .48 else 'fall'
            if jump.end < x < jump.end + self.speed * .10:
                return 'land'
        if any(abs(seconds - coin.collected) < .09 for coin in self.coins):
            return 'collect'
        return f'run{int((seconds - START) * 10) % 4}'

    def position(self, seconds):
        x = self.x_at(seconds)
        y = self.feet_at(x)
        if seconds < START:
            y += max(0, 1 - seconds / 1.15) * 44
        if 17.65 <= seconds < 20:
            y -= 5 * max(0, math.sin((seconds - 17.65) * 9))
        return x, y
