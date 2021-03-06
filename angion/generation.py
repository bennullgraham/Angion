from config import cfg
from solution import Solution, Plot
from expression import Expression, createTerm
from multiprocessing import Pool
from random import uniform, random
import copy
import json


class Generation(object):
    def __init__(self):
        self.fittest = None

        self.generation = 0
        initial_solution = Solution()
        initial_solution.length_function = Expression(init_terms=[createTerm('Constant', innerMultiplier=3.0, outerMultiplier=3.0)])
        initial_solution.radiance_function = Expression(init_terms=[createTerm('Constant', innerMultiplier=1.0, outerMultiplier=1.5)])
        initial_solution.orientation_function = Expression(init_terms=[createTerm('Constant', innerMultiplier=-0.1, outerMultiplier=0.1)])
        initial_solution.termination_function = Expression(init_terms=[createTerm('Constant', innerMultiplier=3.0, outerMultiplier=3.0)])

        self.solutions = [initial_solution]
        workers = cfg.getint('FitnessTest', 'workers')
        if workers > 1:
            print "Evaluating using {workers} worker threads".format(workers=workers)
            self.map = Pool(processes=workers).map_async
        else:
            self.map = map
        self.max_fitness_acheived = 0

    def new_solution(self):
        def random_term():
            return createTerm('Random', innerMultiplier=uniform(-2.0, 2.0), outerMultiplier=uniform(-3.0, 3.0))
        s = Solution()
        s.length_function = Expression(init_terms=[random_term()])
        s.radiance_function = Expression(init_terms=[random_term()])
        s.orientation_function = Expression(init_terms=[random_term()])
        s.termination_function = Expression(init_terms=[random_term()])
        return s

    def evolve(self):
        self.generation = self.generation + 1
        # keep the best few
        candidates = sorted(self.solutions, key=lambda s: s.fitness)[:3]
        # keep and mutate the best few from previous round
        self.solutions = self.map(mutate, [copy.deepcopy(c) for c in candidates])  # .get(100)
        # keep the best few from previous round unmutated
        # solutions.extend([copy.deepcopy(c) for c in candidates])
        # mix up the functions from the best few from previous round
        self.solutions.extend([self.combine(s1, s2) for s1 in candidates for s2 in candidates for n in range(1)])

    def combine(self, s1, s2):
        sn = Solution()
        sn.length_function = copy.deepcopy(s1.length_function) if random() > 0.5 else copy.deepcopy(s2.length_function)
        sn.radiance_function = copy.deepcopy(s1.radiance_function) if random() > 0.5 else copy.deepcopy(s2.radiance_function)
        sn.orientation_function = copy.deepcopy(s1.orientation_function) if random() > 0.5 else copy.deepcopy(s2.orientation_function)
        sn.termination_function = copy.deepcopy(s1.termination_function) if random() > 0.5 else copy.deepcopy(s2.termination_function)
        return sn

    def solve(self):
        self.solutions = self.map(solve, self.solutions)  # .get(100)  # compute point-sets and fitnesses
        self.fittest = max(self.solutions, key=lambda s: s.fitness)

    def describe(self):
        improvement = 0 if self.max_fitness_acheived == 0 else (self.fittest.fitness / self.max_fitness_acheived) - 1
        if self.fittest.fitness > self.max_fitness_acheived or self.generation == 0:
            self.max_fitness_acheived = self.fittest.fitness
            p = Plot(self.fittest)
            p.draw(self.generation)
            f = open('output/out.{lap}.json'.format(lap=self.generation), 'w')
            json.dump(self.fittest.normalised_segment_set(), f)
            f.close()
            print "{lap}: {fitness} ({improvement:+.2%}) from {count} solutions".format(lap=self.generation, fitness=self.fittest.fitness, improvement=improvement, count=len(self.solutions))
            print "       length:      {length_function}".format(length_function=self.fittest.length_function.__unicode__())
            print "       radiance:    {radiance_function}".format(radiance_function=self.fittest.radiance_function.__unicode__())
            print "       orientation: {orientation_function}".format(orientation_function=self.fittest.orientation_function.__unicode__())
            print "       termination: {termination_function}".format(termination_function=self.fittest.termination_function.__unicode__())
            print "       penalties:   service [{service_penalty:.2}] length [{length_penalty:.2}] complexity [{complexity_penalty}] bounds [{bounds_penalty}]".format(service_penalty=self.fittest.service_penalty, length_penalty=self.fittest.length_penalty, complexity_penalty=self.fittest.complexity_penalty, bounds_penalty=self.fittest.bounds_penalty)
            print ""
        elif self.generation % 1000 == 0:
            print "{lap}".format(lap=self.generation)

    def next_generation(self):
        self.evolve()
        self.solve()
        self.describe()


def solve(solution):
    return solution.solve()


def mutate(solution):
    return solution.mutate()
