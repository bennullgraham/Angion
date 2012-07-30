from solution.solution import Solution, BaseTerm, TermSet, Plot
from multiprocessing import Pool
from random import choice, uniform, random
import copy
import json


class Configuration(object):
    ##################
    # Function terms #
    ##################

    # amount to vary terms by if mutating. 0.1 = +/- 10%.
    MUTE_VARIABILITY = 0.01

    # how many terms of a termset to mutate. terms are not limited to a single mutation.
    NUM_MUTE_TERMS = 3

    # 0 -> 1 chance a term will be mutated at all
    MUTE_CHANCE = 0.5

    # maximum terms in a termset
    MAX_TERMS = 3

    # chance to add new terms to a term set
    CREATE_TERM_CHANCE = 0.0007

    # chance to delete a term (multiplied by number of terms)
    DELETE_TERM_CHANCE = 0.0005

    ##################
    # Branching      #
    ##################
    # how many segments has each point?
    BRANCH_SEGMENTS = 2

    # split into BRANCHING_FACTOR segments every BRANCH_DISTANCEth point
    BRANCH_DISTANCE = 5

    # Hard limit at this depth
    RECURSION_LIMIT = 50

    ##################
    # Plotting       #
    ##################
    PLOT_SIZE = 1024
    PLOT_MARGIN = 64
    ORIGIN_X = 512  # PLOT_SIZE / 2.0
    ORIGIN_Y = 512  # PLOT_SIZE / 2.0

    ##################
    # Fitness test   #
    ##################

    # spacing of grid used to check how well-covered the area is.
    SERVICE_GRID_SPACING = 16


class SolutionSet(object):
    def __init__(self):
        self.fittest = None
        self.configuration = Configuration
        self.generation = 0
        initial_solution = Solution(self.configuration)
        initial_solution.length_function = TermSet(init_terms=[BaseTerm('CNST', innerMultiplier=3.0, outerMultiplier=3.0), BaseTerm('LINE', innerMultiplier=-0.01, outerMultiplier=0.1)])
        initial_solution.radiance_function = TermSet(init_terms=[BaseTerm('CNST', innerMultiplier=1.0, outerMultiplier=1.5)])
        initial_solution.orientation_function = TermSet(init_terms=[BaseTerm('CNST', innerMultiplier=0.0, outerMultiplier=0.0)])
        initial_solution.termination_function = TermSet(init_terms=[BaseTerm('CNST', innerMultiplier=3.0, outerMultiplier=3.0)])
        self.solutions = [initial_solution]
        self.pool = Pool(4)
        self.max_fitness_acheived = 0

    def new_solution(self):
        def new_baseterm():
            return BaseTerm(choice(BaseTerm.TERM_TYPES), innerMultiplier=uniform(-2.0, 2.0), outerMultiplier=uniform(-3.0, 3.0))
        s = Solution(self.configuration)
        s.length_function = TermSet(init_terms=[new_baseterm()])
        s.radiance_function = TermSet(init_terms=[new_baseterm()])
        s.orientation_function = TermSet(init_terms=[new_baseterm()])
        s.termination_function = TermSet(init_terms=[new_baseterm()])
        return s

    def evolve(self):
        self.generation = self.generation + 1
        # keep the best few
        candidates = sorted(self.solutions, key=lambda s: s.fitness)[:3]
        # candidates.extend([new_solution() for n in range(2)])
        # keep and mutate the best few from previous round
        self.solutions = self.pool.map(mutate, [copy.deepcopy(c) for c in candidates])
        # keep the best few from previous round unmutated
        # solutions.extend([copy.deepcopy(c) for c in candidates])
        # mix up the functions from the best few from previous round
        self.solutions.extend([self.combine(s1, s2) for s1 in candidates for s2 in candidates for n in range(1)])

    def combine(self, s1, s2):
        sn = Solution(s1)
        sn.length_function = copy.deepcopy(s1.length_function) if random() > 0.5 else copy.deepcopy(s2.length_function)
        sn.radiance_function = copy.deepcopy(s1.radiance_function) if random() > 0.5 else copy.deepcopy(s2.radiance_function)
        sn.orientation_function = copy.deepcopy(s1.orientation_function) if random() > 0.5 else copy.deepcopy(s2.orientation_function)
        sn.termination_function = copy.deepcopy(s1.termination_function) if random() > 0.5 else copy.deepcopy(s2.termination_function)
        return sn

    def solve(self):
        # self.pool.
        self.solutions = map(solve, self.solutions)  # compute point-sets and fitnesses
        self.fittest = max(self.solutions, key=lambda s: s.fitness)

    def describe(self):
        improvement = 0 if self.fittest.fitness == 0 else (self.fittest.fitness / self.max_fitness_acheived) - 1
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

if __name__ == "__main__":
    s = SolutionSet()
    while True:
        s.next_generation()
