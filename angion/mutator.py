from random import choice
from fractal import Fractal


class Mutator(object):
    def __init__(self):
        self.best = Fractal()
        self.best.fitness = 0

    def mutate(self, (fractals)):
        fractals += [self.best, ]
        sorted(fractals)
        for f in fractals:
            f.length_function.mutate()
            f.radiance_function.mutate()
            f.orientation_function.mutate()
            f.termination_function.mutate()
            rpool = fractals + [f, f, f, f]  # twice as likely to keep own function as get new
            f.length_function = choice(rpool).length_function
            f.radiance_function = choice(rpool).radiance_function
            f.orientation_function = choice(rpool).orientation_function
            f.termination_function = choice(rpool).termination_function

        length = len(fractals) - 2
        return fractals[:length]
