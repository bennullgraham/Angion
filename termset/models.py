from django.db import models
from math import sin, e
from termset import constants
from random import choice, random, seed
from decimal import *
from solution import Solution


class TermSet(models.Model):
	solution = models.ForeignKey(Solution)

	def __unicode__(self):
		terms = self.baseterm_set.all()
		return reduce(lambda a, b: str(a) + ' + ' + str(b), terms)

	def f(self, x):
		terms = self.baseterm_set.all()
		return reduce(lambda a, b: a.f(x) + b.f(x), terms)

	def mutate(self):
		mutate_count = 0
		terms = self.baseterm_set.all()

		# maybe create a term
		if random() > (1 - constants.CREATE_TERM_CHANCE):
			bt = BaseTerm(term_set_id=self.pk, term_type=choice(('EXP', 'POLY', 'TRIG')))
			bt.save()

		# maybe delete a term
		if random() > (1 - constants.DELETE_TERM_CHANCE):
			bt = choice(self.baseterm_set.all()).delete()

		# modify some term constants
		while mutate_count < constants.NUM_MUTE_TERMS:
			t = choice(terms)
			t.mutate()
			mutate_count += 1


class BaseTerm(models.Model):
	TERM_TYPES = (
		(u'EXP',  u'Exponential'),
		(u'POLY', u'Polynomial'),
		(u'TRIG', u'Trigonometric'),
	)
	outerMultiplier = models.DecimalField(max_digits=5, decimal_places=3, default=0)
	innerMultiplier = models.DecimalField(max_digits=5, decimal_places=3, default=0)
	term_type = models.CharField(max_length=8, choices=TERM_TYPES)
	term_set = models.ForeignKey(TermSet)

	def __unicode__(self):
		if self.term_type == 'EXP':
			return str(self.outerMultiplier) + 'e^(' + str(self.innerMultiplier) + 'x)'
		elif self.term_type == 'TRIG':
			return str(self.outerMultiplier) + 'sin(' + str(self.innerMultiplier) + 'x)'
		elif self.term_type == 'POLY':
			return str(self.outerMultiplier) + 'x^' + str(self.innerMultiplier)
		else:
			return super(BaseTerm, self).__unicode__()

	def f(self, x):
		if self.term_type == 'EXP':
			return self.outerMultiplier * (x ^ self.innerMultiplier)
		elif self.term_type == 'TRIG':
			return self.outerMultiplier * sin(x * self.innerMultiplier)
		elif self.term_type == 'POLY':
			return self.outerMultiplier * (Decimal(e) ^ (x * self.innerMultiplier))
		else:
			raise Exception("Term type unknown")

	def mutate(self):
		def scale(x):
			seed()
			getcontext().prec = 2
			vary = Decimal(random() - 0.5) * constants.MUTE_VARIABILITY * 2 * max(Decimal(0.1), abs(x))
			x = x + vary
			return x
			
		self.innerMultiplier = scale(self.innerMultiplier)
		self.outerMultiplier = scale(self.outerMultiplier)
		self.save()
