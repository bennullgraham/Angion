from math import pi
from geometry import Point
from config import cfg
from PIL import Image, ImageDraw


class Fractal(object):

    def __init__(self):
        self.fitness = 0
        self.total_length = None

    def mutate(self):
        self.length_function.mutate()
        self.radiance_function.mutate()
        self.orientation_function.mutate()
        self.termination_function.mutate()
        return self

    def point_set(self, every=1):
        self.total_length = 1
        origin = OriginPoint(self)
        points = []
        depth_limit = cfg.getint('Fractal', 'recursion_limit')

        def recurse(base):
            if base.depth % every == 0:
                points.append(base)
            if base.depth < depth_limit and not base.terminate():
                segments = base.segments()
                self.total_length += segments[0].length()
                for segment in segments:
                    recurse(segment.end())
        recurse(origin)
        return points

    def normalised_segment_set(self):
        origin = OriginPoint(self)
        depth_limit = cfg.getint('Fractal', 'recursion_limit')

        def recurse(base):
            r = {'x': base.x, 'y': base.y, 'children': []}
            if base.depth < depth_limit and not base.terminate():
                for segment in base.segments():
                    end_point = segment.end()
                    r['children'].append(recurse(end_point))
            return r

        segments = recurse(origin)
        return segments

    def solve(self):
        margin = cfg.getint('Plot', 'margin')
        size = cfg.getint('Plot', 'size')
        spacing = cfg.getint('FitnessTest', 'service_grid_spacing')

        def in_bounds(p):
            if p.x < margin or p.x > (size - margin):
                return False
            if p.y < margin or p.y > (size - margin):
                return False
            return True

        def service_level(eval_point):
            return min([(eval_point[0] - p.x) ** 2 + (eval_point[1] - p.y) ** 2 for p in valid_point_set])

        point_set = self.point_set(1)
        valid_point_set = filter(in_bounds, point_set)

        eval_set = [(x, y)
            for x in range(margin, size - margin, spacing)
            for y in range(margin, size - margin, spacing)
        ]
        self.service_penalty = float(sum(map(service_level, eval_set)) / len(eval_set))
        self.length_penalty = 1.0  # max(1.0, (self.total_length / len(point_set)))
        self.complexity_penalty = 1.0  # int(max(0, len(point_set))) ** 2
        self.bounds_penalty = max(1, (len(point_set) - len(valid_point_set)) * 100) ** 2
        self.fitness = 1.0 / (self.service_penalty + self.length_penalty + self.complexity_penalty + self.bounds_penalty)

        return self


class OriginPoint(Point):

    def __init__(self, fractal):
        self.fractal = fractal
        self.x = cfg.getfloat('Fractal', 'origin_x')
        self.y = cfg.getfloat('Fractal', 'origin_y')
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

    def __init__(self, fractal):
        self.fractal = fractal

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

        im = Image.new('RGBA', (cfg.getint('Plot', 'size'), cfg.getint('Plot', 'size')), (10, 4, 27, 255))
        draw = ImageDraw.Draw(im)
        draw.line((
            (cfg.getint('Plot', 'margin'), cfg.getint('Plot', 'margin')),
            (cfg.getint('Plot', 'margin'), cfg.getint('Plot', 'size') - cfg.getint('Plot', 'margin')),
            (cfg.getint('Plot', 'size') - cfg.getint('Plot', 'margin'), cfg.getint('Plot', 'size') - cfg.getint('Plot', 'margin')),
            (cfg.getint('Plot', 'size') - cfg.getint('Plot', 'margin'), cfg.getint('Plot', 'margin')),
            (cfg.getint('Plot', 'margin'), cfg.getint('Plot', 'margin'))),
            fill="rgb(24,12,54)"
        )
        points = self.fractal.point_set()
        # sort by depth so oldest segments are drawn on top
        points.sort(key=lambda p: -p.depth)

        # for point in points:
        #     fill = colour_lookup(float(point.depth) / (points[0].depth + 1), shade=True)
        #     service_x = (point.x // constants.SERVICE_GRID_SPACING) * constants.SERVICE_GRID_SPACING
        #     service_y = (point.y // constants.SERVICE_GRID_SPACING) * constants.SERVICE_GRID_SPACING
        #     draw.rectangle(
        #         (service_x + 1, service_y + 1, service_x + constants.SERVICE_GRID_SPACING - 1, service_y + constants.SERVICE_GRID_SPACING - 1),
        #         fill=fill  # "rgb(25,20,37,20)"
        #     )

        for point in points:
            fill = colour_lookup(float(point.depth) / (points[0].depth + 1))
            for segment in point.segments():
                end = segment.end()
                if end.x >= 0 and end.y >= 0 and end.x <= cfg.get('Plot', 'size') and end.y <= cfg.get('Plot', 'size'):
                    draw.line((point.x, point.y, end.x, end.y), fill=fill)
        im.save("output/out." + str(seq) + ".png", "PNG")
