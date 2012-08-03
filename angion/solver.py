from config import cfg


def solve(fractal):
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

    point_set = fractal.point_set(1)
    valid_point_set = filter(in_bounds, point_set)

    eval_set = [(x, y)
        for x in range(margin, size - margin, spacing)
        for y in range(margin, size - margin, spacing)
    ]
    fractal.service_penalty = float(sum(map(service_level, eval_set)) / len(eval_set))
    fractal.length_penalty = 1.0  # max(1.0, (fractal.total_length / len(point_set)))
    fractal.complexity_penalty = 1.0  # int(max(0, len(point_set))) ** 2
    fractal.bounds_penalty = max(1, (len(point_set) - len(valid_point_set)) * 100) ** 2
    fractal.fitness = 1.0 / (fractal.service_penalty + fractal.length_penalty + fractal.complexity_penalty + fractal.bounds_penalty)

    return fractal
