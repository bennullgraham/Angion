from math import hypot, sin, cos, pi
from sys import float_info
import Config


class Point(object):
    def __unicode__(self):
        return str(self.x) + ', ' + str(self.y)

    def __init__(self, x, y, solution, depth, parent_orientation):
        self.x = int(x)
        self.y = int(y)
        self.solution = solution
        self.configuration = solution.configuration
        self.depth = depth
        self.dist_to_origin = self._dist_to_origin()
        self.parent_orientation = parent_orientation
        self.segment_count = 1 if self.depth % Config.get('Branch', 'every') else Config.get('Branch', 'segments')

    def _dist_to_origin(self):
        try:
            return min(Config.get('Plot', 'size'), hypot(self.x - Config.get('Fractal', 'origin_x'), self.y - Config.get('Fractal', 'origin_y')), key=abs)
        except OverflowError:
            return float_info.max

    def radiance(self):
        dist = self.dist_to_origin
        return self.solution.radiance_function.f(dist) % (2 * pi)

    def orientation(self):
        dist = self.dist_to_origin
        delta = self.solution.orientation_function.f(dist)
        return (self.parent_orientation + delta) % (2 * pi)

    def segments(self):
        orientation = self.orientation()
        radiance = self.radiance()
        sweep_begin = orientation - (radiance / 2)
        sweep_step = radiance / (self.segment_count)
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
            return self.solution.termination_function.f(dist) < self.depth
        except OverflowError:
            return True


class Segment(object):
    def __init__(self, base, angle):
        self.solution = base.solution
        self.base = base
        self.angle = angle

    def length(self):
        dist = self.base.dist_to_origin
        return abs(self.solution.length_function.f(dist))

    def end(self):
        x = self.base.x + self.length() * cos(self.angle)
        y = self.base.y + self.length() * sin(self.angle)
        return Point(x, y, self.solution, self.base.depth + 1, self.angle)
