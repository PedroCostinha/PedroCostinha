"""Deterministic geometry shared by rendering, sprites, coins and tests."""

from dataclasses import dataclass
import math

DURATION = 20.8
START = 1.6
FINISH = 17.2
GRID_X = 116
GRID_Y = 318
GRID_WIDTH = 954
GROUND = 312
SPRITE_HEIGHT = 42
SPRITE_HALF_WIDTH = 17.5
POSES = ('idle', 'accelerate', 'run0', 'run1', 'run2', 'run3', 'run4', 'run5',
         'jump', 'apex', 'fall', 'land', 'collect', 'victory', 'celebrate')


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
    date: str
    level: int


class Route:
    def __init__(self, calendar):
        self.pitch = GRID_WIDTH / calendar.weeks
        self.platforms = []
        starts = list(range(0, calendar.weeks, 6))
        if calendar.weeks - starts[-1] < 3:
            starts.pop()
        for w, end_week in zip(starts, starts[1:] + [calendar.weeks]):
            level = max((d.level for d in calendar.days if w <= d.week < end_week), default=0)
            self.platforms.append(Platform(GRID_X + w * self.pitch,
                                          GRID_X + end_week * self.pitch - 5,
                                          GROUND - level * 4, level, w))
        self.left, self.right = 78, 1116
        self.acceleration = .32
        self.speed = (self.right - self.left) / (FINISH - START - self.acceleration / 2)
        self.jumps = []
        first, last = self.platforms[0], self.platforms[-1]
        self.jumps.append(Jump(86, first.x + 26, GROUND, first.y, 24 + abs(GROUND - first.y)))
        for previous, following in zip(self.platforms, self.platforms[1:]):
            # Clearance includes the complete sprite, including outstretched hands.
            self.jumps.append(Jump(previous.end - 26, following.x + 26, previous.y, following.y,
                                   20 + following.level * 2 + abs(previous.y - following.y)))
        self.jumps.append(Jump(last.end - 26, 1100, last.y, GROUND, 26 + abs(last.y - GROUND)))
        self.coins = []
        for platform in self.platforms:
            if platform.level >= 3:
                # Keep sparse calendars' high-activity days, including days near a jump.
                # Vertical coin placement follows the exact airborne or grounded pose.
                candidates = [d for d in calendar.days if d.level >= 3 and
                              platform.x <= GRID_X + (d.week + .5) * self.pitch <= platform.end]
                if candidates:
                    day = max(candidates, key=lambda d: (d.level, d.count, d.date))
                    x = GRID_X + (day.week + .5) * self.pitch
                    self.coins.append(Coin(x, self.feet_at(x) - 29, self.time_at(x), str(day.date), day.level))

        self.week_times = tuple(self.time_at(GRID_X + (week + .5) * self.pitch)
                                for week in range(calendar.weeks))

    def time_at(self, x):
        distance = max(0, x - self.left)
        ramp_distance = self.speed * self.acceleration / 2
        if distance < ramp_distance:
            return START + math.sqrt(2 * distance * self.acceleration / self.speed)
        return START + distance / self.speed + self.acceleration / 2

    def x_at(self, seconds):
        elapsed = max(0, seconds - START)
        distance = (self.speed * elapsed * elapsed / (2 * self.acceleration)
                    if elapsed < self.acceleration else self.speed * (elapsed - self.acceleration / 2))
        return min(self.right, self.left + distance)

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
            if FINISH <= seconds < 17.65:
                return 'victory'
            return 'celebrate' if 17.65 <= seconds < 20 else 'idle'
        if any(abs(seconds - coin.collected) < .09 for coin in self.coins):
            return 'collect'
        x = self.x_at(seconds)
        for jump in self.jumps:
            if jump.x <= x <= jump.end:
                u = (x - jump.x) / (jump.end - jump.x)
                apex = .5 - (jump.end_y - jump.y) / (8 * jump.height)
                if abs(u - apex) < .10:
                    return 'apex'
                return 'jump' if u < apex else 'fall'
            if jump.end < x < jump.end + self.speed * .10:
                return 'land'
        if seconds < START + self.acceleration:
            return 'accelerate'
        return f'run{int((seconds - START) * 12) % 6}'

    def position(self, seconds):
        x = self.x_at(seconds)
        y = self.feet_at(x)
        if seconds < START:
            y += max(0, 1 - seconds / 1.15) * 44
        if 17.65 <= seconds < 20:
            y -= 5 * max(0, math.sin((seconds - 17.65) * 9))
        return x, y
