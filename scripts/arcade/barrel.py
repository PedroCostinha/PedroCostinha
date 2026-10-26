"""Deterministic authored demo, geometry and exact contribution-based scoring."""

from dataclasses import dataclass

START = 1.0
TRAVEL = 4.4
CLIMB = 1.5
DURATION = 32.0
FINISH = START + 5 * TRAVEL + 4 * CLIMB
# Authored phase offsets keep all five meetings away from ladders/hatches.
# Geometry tests verify the entire replay, including climbing and service resets.
PHASES = (0.0, 10.8, 22.4)
POSES = ('idle', 'walk0', 'walk1', 'run0', 'run1', 'run2', 'run3',
         'jump', 'climb0', 'climb1', 'victory')


def floor_y(floor, x):
    """Feet contact on alternating 18px inclines, within x=100..820."""
    u = (x - 100) / 720
    return 548 - 84 * floor + 18 * (1 - u if floor % 2 == 0 else u)


@dataclass(frozen=True)
class Stage:
    floor: int
    begin: float
    end: float
    left: float
    right: float
    days: tuple

    @property
    def points(self):
        return sum(d.count for d in self.days)

    @property
    def collected(self):
        return self.begin + TRAVEL * .9

    @property
    def terminal_x(self):
        return self.left + .9 * (self.right - self.left)


def barrel(t, phase=0):
    """A barrel rolls downhill and drops at alternating outer platform edges.

    A hidden service interval after leaving the bottom resets it at the chute.
    The cinematic fade masks the global loop; no SMIL or JS is needed.
    """
    elapsed = (t - START + phase) % DURATION
    for floor in range(4, -1, -1):
        begin = (4 - floor) * (TRAVEL + CLIMB)
        a, b = (800, 120) if floor % 2 == 0 else (120, 800)
        if begin <= elapsed <= begin + TRAVEL:
            x = a + (b - a) * (elapsed - begin) / TRAVEL
            return x, floor_y(floor, x) - 9, True, floor
        if floor and begin + TRAVEL < elapsed < begin + TRAVEL + CLIMB:
            u = (elapsed - begin - TRAVEL) / CLIMB
            y = floor_y(floor, b) + (floor_y(floor - 1, b) - floor_y(floor, b)) * u
            return b, y - 9, True, None
    return 120, floor_y(0, 120) - 9, False, None


def barrel_boundaries(phase):
    result = {0.0, DURATION}
    for cycle in range(-1, 3):
        for index in range(5):
            for offset in (0, TRAVEL, TRAVEL + CLIMB):
                t = START - phase + cycle * DURATION + index * (TRAVEL + CLIMB) + offset
                if 0 < t < DURATION:
                    # A tiny boundary on either side keeps hidden resets discrete.
                    result.update((max(0, t - .0001), t, min(DURATION, t + .0001)))
    return result


def barrel_rotation(t, phase):
    elapsed = (t-START+phase) % DURATION
    distance = 0
    for index in range(5):
        fraction = min(1,max(0,(elapsed-index*(TRAVEL+CLIMB))/TRAVEL))
        distance += (-680 if index%2 == 0 else 680)*fraction
    return distance/9*180/3.141592653589793


class Demo:
    def __init__(self, calendar):
        self.calendar = calendar
        self.stages = tuple(Stage(i, START + i * (TRAVEL + CLIMB),
                                  START + i * (TRAVEL + CLIMB) + TRAVEL,
                                  160 if i % 2 == 0 else 760,
                                  760 if i % 2 == 0 else 160,
                                  calendar.days[len(calendar.days)*i//5:len(calendar.days)*(i+1)//5])
                            for i in range(5))
        # Solve meetings between straight rolling and running segments. Jumps
        # are centered on actual barrel encounters, never random decoration.
        self.jumps = []
        for stage in self.stages:
            for phase in PHASES:
                for cycle in range(-1, 3):
                    begin = START - phase + cycle * DURATION + (4-stage.floor) * (TRAVEL+CLIMB)
                    low, high = max(stage.begin, begin), min(stage.end, begin+TRAVEL)
                    if low >= high:
                        continue
                    a, b = (800, 120) if stage.floor % 2 == 0 else (120, 800)
                    runner_speed = (stage.right-stage.left)/TRAVEL
                    barrel_speed = (b-a)/TRAVEL
                    t = (a - barrel_speed*begin - stage.left + runner_speed*stage.begin) / (runner_speed-barrel_speed)
                    if low < t < high:
                        self.jumps.append((t-.45, t+.45, stage.floor))
        self.jumps.sort()

    def ground_position(self, t):
        if t <= START:
            return 160, floor_y(0, 160), 0, False
        for stage in self.stages:
            if t <= stage.end:
                u = (t-stage.begin)/TRAVEL
                x = stage.left + (stage.right-stage.left)*u
                return x, floor_y(stage.floor, x), stage.floor, False
            if stage.floor < 4 and t < stage.end+CLIMB:
                u = (t-stage.end)/CLIMB
                x = stage.right
                y = floor_y(stage.floor, x)*(1-u) + floor_y(stage.floor+1, x)*u
                return x, y, stage.floor, True
        return 760, floor_y(4, 760), 4, False

    def position(self, t):
        x, y, floor, climbing = self.ground_position(t)
        if not climbing:
            for begin, end, index in self.jumps:
                if index == floor and begin < t < end:
                    u = (t-begin)/(end-begin)
                    y -= 28 * 4 * u * (1-u)
        return x, y

    def pose(self, t):
        if t <= START:
            return 'idle'
        if t >= FINISH:
            return 'victory'
        _, _, floor, climbing = self.ground_position(t)
        if climbing:
            return f'climb{int(t*6)%2}'
        if any(begin < t < end for begin, end, index in self.jumps if index == floor):
            return 'jump'
        if t < self.stages[floor].begin + .65:
            return f'walk{int(t*5)%2}'
        return f'run{int(t*9)%4}'

    def facing(self, t):
        return -1 if self.ground_position(t)[2] % 2 else 1

    def score(self, t):
        return sum(s.points for s in self.stages if t >= s.collected)

    def samples(self):
        events = {0.0, START, FINISH, DURATION}
        events.update(i/24 for i in range(int(DURATION*24)+1))
        for s in self.stages:
            events.update((s.begin, s.begin+.65, s.end, s.collected))
        for begin, end, _ in self.jumps:
            events.update((begin, (begin+end)/2, end))
        return sorted(events)
