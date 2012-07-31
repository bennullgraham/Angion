import sys
import constants
from random import choice, random, uniform
from math import sin, copysign


class Expression(object):
    def __init__(self, init_terms=[]):
        self.terms = init_terms
        if not self.terms:
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
        if len(self.terms) < constants.MAX_TERMS:
            t = createTerm('Random')
            self.terms.append(t)

    def _delete_term(self):
        t = choice(self.terms)
        self.terms.remove(t)

    def mutate(self):
        mutate_count = 0

        # maybe delete a term
        if self.terms and random() > (1 - (constants.DELETE_TERM_CHANCE * len(self.terms))):
            self._delete_term()

        # potentially create a new term. always do so if there are none.
        if not self.terms or random() > (1 - constants.CREATE_TERM_CHANCE):
            self._add_term()

        # modify some term constants
        if self.terms:
            while mutate_count < constants.NUM_MUTE_TERMS:
                if random() > constants.MUTE_CHANCE:
                    t = choice(self.terms)
                    t.mutate()
                mutate_count += 1


class TermPrototype(object):
    def __init__(self, innerMultiplier=1.0, outerMultiplier=1.0):
        self.innerMultiplier = innerMultiplier
        self.outerMultiplier = outerMultiplier

    def __unicode__(self):
        return self.formatString().format(outer=float(self.outerMultiplier), inner=float(self.innerMultiplier))

    def f(self, x):
        try:
            fx = self._f()(self.innerMultiplier, self.outerMultiplier, x)
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

        return fx

    def mutate(self):
        self.innerMultiplier += uniform(-constants.MUTE_VARIABILITY, -constants.MUTE_VARIABILITY)
        self.outerMultiplier += uniform(-constants.MUTE_VARIABILITY, -constants.MUTE_VARIABILITY)
        return self


class ExponentialTerm(TermPrototype):
    def formatString(self):
        return '{outer:.2}e^({inner:.2}x)'

    def _f(self):
        return lambda i, o, x: o * (x ** i)


class LinearTerm(TermPrototype):
    def formatString(self):
        return '({outer:.2}*{inner:.2})x'

    def _f(self):
        return lambda i, o, x: o * i * x


class TrigonometricTerm(TermPrototype):
    def formatString(self):
        return '{outer:.2}sin({inner:.2}x)'

    def _f(self):
        return lambda i, o, x: o * sin(i * x)


class ConstantTerm(TermPrototype):
    def formatString(self):
        return '{outer:.2}*{inner:.2}'

    def _f(self):
        return lambda i, o, x: o * i


def createTerm(type, innerMultiplier=1.0, outerMultiplier=1.0):
    terms = {
        'Trigonometric': TrigonometricTerm,
        'Linear': LinearTerm,
        'Exponential': ExponentialTerm,
        'Constant': ConstantTerm,
    }
    if type == 'Random':
        type = choice(terms.keys())
    e = terms[type]()
    e.innerMultiplier = innerMultiplier
    e.outerMultiplier = outerMultiplier
    return e
