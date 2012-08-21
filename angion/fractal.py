from math import pi
from geometry import Point
from config import cfg
from expression import Expression
from string import join


class Fractal(object):

    def __init__(self):
        self.fitness = 0
        self.total_length = None

        self.length_function = Expression()
        self.radiance_function = Expression()
        self.orientation_function = Expression()
        self.termination_function = Expression()

        self.functions = {
            'len': self.length_function,
            'rad': self.radiance_function,
            'orn': self.orientation_function,
            'trm': self.termination_function
        }

    def __cmp__(self, other):
        return cmp(self.fitness, other.fitness)

    def __unicode__(self):
        f = self.functions
        expressions = map(lambda k: "%s: %s" % (k, f[k].__unicode__().ljust(14)[:14]), f.keys())
        expressions += ("fitness: " + str(self.fitness),)
        return join(expressions, "  |  ")

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


def to_dict(f_obj):
    def functions_as_dict(f_obj):
        return dict(
            [(k, terms_as_dict(v)) for k, v in f_obj.functions.iteritems()]
        )

    def terms_as_dict(func_obj):
        return {
            'terms': [
                {
                    'type': t.__class__.__name__,
                    'inner': t.innerMultiplier,
                    'outer': t.outerMultiplier,
                } for t in func_obj.terms
            ]
        }

    return {
        'fitness': f_obj.fitness,
        'functions': functions_as_dict(f_obj),
    }


def from_dict(d):
    import expression

    def as_terms(terms_dict):
        return [expression.createTerm(t['type'][:-4], t['inner'], t['outer']) for t in terms_dict]

    f = Fractal()
    f.fitness = d['fitness']
    for k in f.functions.keys():
        f.functions[k] = expression.Expression()
        f.functions[k].terms = as_terms(d['functions'][k]['terms'])

    return f
