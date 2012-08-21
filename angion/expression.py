import sys
from random import choice, random, uniform, seed
from math import sin, copysign, e
from config import cfg

seed()


class Expression(object):
    def __init__(self):
        self.terms = []
        self._add_term()

    def __unicode__(self):
        from string import join
        return join(map(lambda s: s.__unicode__(), self.terms), ' + ')

    def f(self, x):
        f = sum(map(lambda f: f.f(x), self.terms))
        if f > sys.float_info.max:
            return sys.float_info.max
        elif f < -sys.float_info.max:
            return -sys.float_info.max
        else:
            return f

    def _add_term(self):
        if len(self.terms) < cfg.getint('Function', 'maximum_terms'):
            t = createTerm('Random')
            self.terms.append(t)

    def _delete_term(self):
        t = choice(self.terms)
        self.terms.remove(t)

    def mutate(self):
        mutate_count = 0

        # maybe delete a term
        if self.terms and random() > (1 - (cfg.getfloat('Function', 'term_deletion_chance') * len(self.terms))):
            self._delete_term()

        # potentially create a new term. always do so if there are none.
        if not self.terms or random() > (1 - cfg.getfloat('Function', 'term_creation_chance')):
            self._add_term()

        # modify some term constants
        if self.terms:
            while mutate_count < cfg.getint('Mutator', 'number_of_terms'):
                if random() > cfg.getfloat('Mutator', 'probability'):
                    t = choice(self.terms)
                    t.mutate()
                mutate_count += 1


class TermPrototype(object):

    minimum = -cfg.getint('Function', 'maximum_magnitude')
    maximum = cfg.getint('Function', 'maximum_magnitude')

    def __init__(self, innerMultiplier=1.0, outerMultiplier=1.0):
        self.innerMultiplier = innerMultiplier
        self.outerMultiplier = outerMultiplier

    def __unicode__(self):
        return self.formatString.format(outer=float(self.outerMultiplier), inner=float(self.innerMultiplier))

    def f(self, x):
        try:
            fx = self._f(self.innerMultiplier, self.outerMultiplier, x)
        except OverflowError:
            # return largest float with correct sign
            i_sign = copysign(1, self.innerMultiplier)
            o_sign = copysign(1, self.outerMultiplier)
            x_sign = copysign(1, x)
            fx = copysign(sys.float_info.max, self._f(i_sign, o_sign, x_sign))
        except ZeroDivisionError:
            fx = 0
        except ValueError:
            fx = 0

        return sorted((TermPrototype.minimum, fx, TermPrototype.maximum))[1]

    def mutate(self):
        variability = cfg.getfloat('Mutator', 'variability')

        def nonzero_variation():
            while True:
                v = uniform(-variability, variability)
                if v != 0:
                    return v

        self.innerMultiplier += nonzero_variation()
        self.outerMultiplier += nonzero_variation()
        return self


class ExponentialTerm(TermPrototype):
    # raising e to distance-to-originth power quickly explodes.
    # we scale distance-to-origin by the size of the plot.
    distScale = (1.0 / cfg.getint('Plot', 'size'))
    formatString = '{outer:.2}e^({inner:.2}x)'
    _f = lambda self, i, o, x: o * (e ** (x * i * ExponentialTerm.distScale))


class LinearTerm(TermPrototype):
    formatString = '({outer:.2}*{inner:.2})x'
    _f = lambda self, i, o, x: o * i * x


class TrigonometricTerm(TermPrototype):
    formatString = '{outer:.2}sin({inner:.2}x)'
    _f = lambda self, i, o, x: o * sin(i * x)


class ConstantTerm(TermPrototype):
    formatString = '{outer:.2}+{inner:.2}'
    _f = lambda self, i, o, x: o + i


def createTerm(term_type, innerMultiplier=1.0, outerMultiplier=1.0):
    terms = {
        'Trigonometric': TrigonometricTerm,
        'Linear': LinearTerm,
        'Exponential': ExponentialTerm,
        'Constant': ConstantTerm,
    }
    if term_type == 'Random':
        term_type = choice(terms.keys())
    e = terms[term_type]()
    e.innerMultiplier = innerMultiplier
    e.outerMultiplier = outerMultiplier
    return e
