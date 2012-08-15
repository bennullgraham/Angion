from random import random, choice
from fractal import Fractal
from copy import deepcopy


class Mutator(object):
    def __init__(self):
        self.best = Fractal()
        self.best.fitness = 0

    def biased_choice(self, f, fractals):
            r = random()
            if r < 0.5:
                return self.best  # 50% chance to return best
            if r < 0.75:
                return f  # 25% chance to return self
            if r < 1.0:
                return choice(fractals)  # 25% chance to return random fractal from current pool

    def mutate(self, fractals):

        # print [str(f.fitness) for f in fractals]
        fractals += [self.best, ]
        for f in fractals:
            f.length_function.mutate()
            f.radiance_function.mutate()
            f.orientation_function.mutate()
            f.termination_function.mutate()
            f.length_function = deepcopy(self.biased_choice(f, fractals).length_function)
            f.radiance_function = deepcopy(self.biased_choice(f, fractals).radiance_function)
            f.orientation_function = deepcopy(self.biased_choice(f, fractals).orientation_function)
            f.termination_function = deepcopy(self.biased_choice(f, fractals).termination_function)

        fractals = sorted(fractals, reverse=True)
        length = len(fractals) - 2
        if fractals[0].fitness > self.best.fitness:
            self.best = deepcopy(fractals[0])

        return fractals[:length]
