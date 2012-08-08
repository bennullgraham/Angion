from math import hypot, sin, cos, pi
from sys import float_info
from config import cfg

# calls to config seem to be slow, so 'cache' these here
branch_every = cfg.getint('Branch', 'every')
branch_segments = cfg.getint('Branch', 'segments')
origin_x = cfg.getint('Fractal', 'origin_x')
origin_y = cfg.getint('Fractal', 'origin_y')


class Point(object):
    def __unicode__(self):
        return str(self.x) + ', ' + str(self.y)

    def __init__(self, x, y, fractal, depth, parent_orientation):
        self.x = int(x)
        self.y = int(y)
        self.fractal = fractal
        self.depth = depth
        self.dist_to_origin = self._dist_to_origin()
        self.parent_orientation = parent_orientation
        self.segment_count = 1 if self.depth % branch_every else branch_segments

    def _dist_to_origin(self):
        try:
            return min(cfg.getint('Plot', 'size'), hypot(self.x - origin_x, self.y - origin_y), key=abs)
        except OverflowError:
            return float_info.max

    def radiance(self):
        dist = self.dist_to_origin
        return self.fractal.radiance_function.f(dist) % (2 * pi)

    def orientation(self):
        dist = self.dist_to_origin
        delta = self.fractal.orientation_function.f(dist)
        return (self.parent_orientation + delta) % (2 * pi)

    def segments(self):
        orientation = self.orientation()
        radiance = self.radiance()
        sweep_begin = orientation - (radiance / 2)
        if self.segment_count == 1:
            sweep_step = 0
        else:
            sweep_step = radiance / (self.segment_count - 1)
        segments = []

        if sweep_step == 0:
            segments.append(Segment(self, orientation))
        else:
            for n in range(0, self.segment_count):
                segments.append(Segment(self, sweep_begin + (sweep_step * n)))
        return segments

    def terminate(self):
        try:
            dist = self.dist_to_origin
            return self.fractal.termination_function.f(dist) < self.depth
        except OverflowError:
            return True


class Segment(object):
    def __init__(self, base, angle):
        self.fractal = base.fractal
        self.base = base
        self.angle = angle

    def length(self):
        dist = self.base.dist_to_origin
        return abs(self.fractal.length_function.f(dist))

    def end(self):
        x = self.base.x + self.length() * cos(self.angle)
        y = self.base.y + self.length() * sin(self.angle)
        return Point(x, y, self.fractal, self.base.depth + 1, self.angle)
