from math import sin, cos, pi, hypot
from geometry import Point
import Config
import sys
import constants
from PIL import Image, ImageDraw


class Solution(object):

    def __init__(self):
        self.fitness = 0
        self.total_length = None

    def mutate(self):
        self.length_function.mutate()
        self.radiance_function.mutate()
        self.orientation_function.mutate()
        self.termination_function.mutate()
        return self

    def point_set(self):
        self.total_length = 1
        origin = OriginPoint(self)
        points = []

        def recurse(base):
            points.append(base)
            if base.depth < Config.get('Fractal', 'recursion_limit') and not base.terminate():
                segments = base.segments()
                self.total_length += segments[0].length()
                for segment in segments:
                    recurse(segment.end())
        recurse(origin)
        return points

    def normalised_segment_set(self):
        origin = OriginPoint()

        def recurse(base):
            r = {'x': base.x, 'y': base.y, 'children': []}
            if base.depth < Config.get('Fractal', 'recursion_limit') and not base.terminate(self):
                for segment in base.segments(self):
                    end_point = segment.end(self)
                    r['children'].append(recurse(end_point))
            return r

        segments = recurse(origin)
        return segments

    def solve(self):
        def in_bounds(p):
            if p.x < Config.get('Plot', 'margin') or p.x > (Config.get('Plot', 'size') - Config.get('Plot', 'margin')):
                return False
            if p.y < Config.get('Plot', 'margin') or p.y > (Config.get('Plot', 'size') - Config.get('Plot', 'margin')):
                return False
            return True

        def to_service_grid_bucket(p):
            return (p.x // Config.get('FitnessTest', 'service_grid_spacing'), p.y // Config.get('FitnessTest', 'service_grid_spacing'))

        def service_level(eval_point):
            return min([(eval_point[0] - p[0]) ** 2 + (eval_point[1] - p[1]) ** 2 for p in quantised_point_set])

        point_set = self.point_set()
        valid_point_set = filter(in_bounds, point_set)
        quantised_point_set = set(map(to_service_grid_bucket, valid_point_set))
        eval_set = [(x, y)
            for x in range(Config.get('Plot', 'margin'), Config.get('Plot', 'size') - Config.get('Plot', 'margin'), Config.get('FitnessTest', 'service_grid_spacing'))
            for y in range(Config.get('Plot', 'margin'), Config.get('Plot', 'size') - Config.get('Plot', 'margin'), Config.get('FitnessTest', 'service_grid_spacing'))
        ]
        self.service_penalty = float(sum(map(service_level, eval_set)) / len(eval_set))
        self.length_penalty = max(1.0, (self.total_length / len(point_set)))
        self.complexity_penalty = int(max(0, len(point_set))) ** 2
        self.bounds_penalty = max(1, (len(point_set) - len(valid_point_set)) * 100) ** 2
        self.fitness = (self.service_penalty + self.length_penalty + self.complexity_penalty + self.bounds_penalty) ** -1
        return self

        
class OriginPoint(Point):

    def __init__(self, solution):
        self.solution = solution
        self.configuration = solution.configuration
        self.x = Config.get('Fractal', 'origin_x')
        self.y = Config.get('Fractal', 'origin_y')
        self.depth = 0
        self.dist_to_origin = 0
        self.parent_orientation = 0
        self.segment_count = 4

    def radiance(self):
        return 2 * pi

    def orientation(self):
        return 0


class Plot(object):
    segments = []

    def __init__(self, solution):
        self.solution = solution

    def draw(self, seq):
        # (0,150,255) [0x0096ff] -> (42,22,69) [0x45162a]
        def colour_lookup(ratio, shade=False):
            r = 000 + (ratio * (42 - 000))
            g = 150 + (ratio * (22 - 150))
            b = 255 + (ratio * (69 - 255))
            if shade:
                r /= 3.0
                g /= 3.0
                b /= 3.0
            return "rgb({},{},{})".format(int(r), int(g), int(b))

        im = Image.new('RGBA', (Config.get('Plot', 'size'), Config.get('Plot', 'size')), (10, 4, 27, 255))
        draw = ImageDraw.Draw(im)
        draw.line((
            (Config.get('Plot', 'margin'), Config.get('Plot', 'margin')),
            (Config.get('Plot', 'margin'), Config.get('Plot', 'size') - Config.get('Plot', 'margin')),
            (Config.get('Plot', 'size') - Config.get('Plot', 'margin'), Config.get('Plot', 'size') - Config.get('Plot', 'margin')),
            (Config.get('Plot', 'size') - Config.get('Plot', 'margin'), Config.get('Plot', 'margin')),
            (Config.get('Plot', 'margin'), Config.get('Plot', 'margin'))),
            fill="rgb(24,12,54)"
        )
        points = self.solution.point_set()
        # sort by depth so oldest segments are drawn on top
        points.sort(key=lambda p: -p.depth)

        for point in points:
            fill = colour_lookup(float(point.depth) / (points[0].depth + 1), shade=True)
            service_x = (point.x // constants.SERVICE_GRID_SPACING) * constants.SERVICE_GRID_SPACING
            service_y = (point.y // constants.SERVICE_GRID_SPACING) * constants.SERVICE_GRID_SPACING
            draw.rectangle(
                (service_x + 1, service_y + 1, service_x + constants.SERVICE_GRID_SPACING - 1, service_y + constants.SERVICE_GRID_SPACING - 1),
                fill=fill  # "rgb(25,20,37,20)"
            )

        for point in points:
            fill = colour_lookup(float(point.depth) / (points[0].depth + 1))
            for segment in point.segments(self.solution):
                end = segment.end(self.solution)
                if end.x >= 0 and end.y >= 0 and end.x <= Config.get('Plot', 'size') and end.y <= Config.get('Plot', 'size'):
                    draw.line((point.x, point.y, end.x, end.y), fill=fill)
        im.save("out." + str(seq) + ".png", "PNG")
