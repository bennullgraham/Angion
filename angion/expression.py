import sys
import constants
from random import choice, random, uniform
from math import sin, copysign, e


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
            term_type = choice(BaseTerm.TERM_TYPES)
            bt = BaseTerm(term_type=term_type)
            self.terms.append(bt)

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


class BaseTerm(object):
    TERM_TYPES = (
        # (u'EXP'),
        # (u'POLY'),
        (u'TRIG'),
        (u'LINE'),
        (u'CNST'),
    )

    def __init__(self, term_type, innerMultiplier=1.0, outerMultiplier=1.0):
        self.term_type = term_type
        self.innerMultiplier = innerMultiplier
        self.outerMultiplier = outerMultiplier

    def __unicode__(self):
        if self.term_type == 'EXP':
            f = '{outer:.2}e^({inner:.2}x)'
        elif self.term_type == 'TRIG':
            f = '{outer:.2}sin({inner:.2}x)'
        elif self.term_type == 'POLY':
            f = '{outer:.2}x^{inner:.2}'
        elif self.term_type == 'LINE':
            f = '({outer:.2}*{inner:.2})x'
        elif self.term_type == 'CNST':
            f = '({outer:.2}*{inner:.2})'
        else:
            return "er..."

        return f.format(outer=float(self.outerMultiplier), inner=float(self.innerMultiplier))

    def f(self, x):
        if self.term_type == 'EXP':
            f = lambda i, o, x: o * (x ** i)
        elif self.term_type == 'TRIG':
            f = lambda i, o, x: o * sin(x * i)
        elif self.term_type == 'POLY':
            f = lambda i, o, x: o * e ** (x * i)
        elif self.term_type == 'LINE':
            f = lambda i, o, x: o * i * x
        elif self.term_type == 'CNST':
            f = lambda i, o, x: o * i
        else:
            raise Exception("Term type unknown")

        try:
            fx = f(self.innerMultiplier, self.outerMultiplier, x)
        except OverflowError:
            # return largest float with correct sign
            i_sign = copysign(1, self.innerMultiplier)
            o_sign = copysign(1, self.outerMultiplier)
            x_sign = copysign(1, x)
            fx = copysign(sys.float_info.max, f(i_sign, o_sign, x_sign))
        except ZeroDivisionError:
            fx = 0
        except ValueError:
            fx = 0

        return fx

    def mutate(self):
        self.innerMultiplier += uniform(-constants.MUTE_VARIABILITY, -constants.MUTE_VARIABILITY)
        self.outerMultiplier += uniform(-constants.MUTE_VARIABILITY, -constants.MUTE_VARIABILITY)
        return self
