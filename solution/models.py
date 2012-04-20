from django.db import models
from math import sin, cos, e, hypot
from solution import constants
from random import choice, random, seed
from PIL import Image, ImageDraw


class TermSet(models.Model):
	def __unicode__(self):
		from string import join
		terms = self.baseterm_set.all()
		return join(map(lambda s: str(s), terms), ' + ')

	def f(self, x):
		terms = self.baseterm_set.all()
		s = sum((map(lambda a: a.f(x), terms)))
		return s

	def mutate(self):
		mutate_count = 0
		terms = self.baseterm_set.all()

		# maybe delete a term
		if terms and random() > (1 - constants.DELETE_TERM_CHANCE):
			choice(self.baseterm_set.all()).delete()

		# potentially create a new term. always do so if there are none.
		if not terms or random() > (1 - constants.CREATE_TERM_CHANCE):
			seed()
			bt = BaseTerm(term_set_id=self.pk, term_type=choice(('EXP', 'POLY', 'TRIG')))
			bt.mutate()
			bt.save()

		# modify some term constants
		if terms:
			while mutate_count < constants.NUM_MUTE_TERMS:
				t = choice(terms)
				t.mutate()
				t.save()
				mutate_count += 1


class BaseTerm(models.Model):
	TERM_TYPES = (
		(u'EXP',  u'Exponential'),
		(u'POLY', u'Polynomial'),
		(u'TRIG', u'Trigonometric'),
	)
	outerMultiplier = models.FloatField(default=1.0)
	innerMultiplier = models.FloatField(default=1.0)
	term_type = models.CharField(max_length=8, choices=TERM_TYPES)
	term_set = models.ForeignKey(TermSet)

	def __unicode__(self):
		if self.term_type == 'EXP':
			f = '{:.2}.e^({:.2}x)'
		elif self.term_type == 'TRIG':
			f = '{:.2}.sin({:.2}x)'
		elif self.term_type == 'POLY':
			f = '{:.2}.x^{:.2}'
		else:
			return super(BaseTerm, self).__unicode__()

		return f.format(self.outerMultiplier, self.innerMultiplier)

	def f(self, x):
		# x = x
		if self.term_type == 'EXP':
			f = self.outerMultiplier * (x ** self.innerMultiplier)
		elif self.term_type == 'TRIG':
			f = self.outerMultiplier * sin(x * self.innerMultiplier)
		elif self.term_type == 'POLY':
			f = self.outerMultiplier * (e ** (x * self.innerMultiplier))
		else:
			raise Exception("Term type unknown")

		# we are definitely going to generate infinities
		if f > 1e100:
			return 1e100
		elif f < -1e100:
			return -1e100
		else:
			return f

	def mutate(self):
		def scale(x):
			seed()
			vary = (random() - 0.5) * constants.MUTE_VARIABILITY * 2 * max(0.1, abs(x))
			x = x + vary
			return x
		self.innerMultiplier = scale(self.innerMultiplier)
		self.outerMultiplier = scale(self.outerMultiplier)


class Solution(models.Model):
	# parent = models.OneToOneField('self', null=True)
	length_function = models.OneToOneField(TermSet, related_name='solution_length_function')
	radiance_function = models.OneToOneField(TermSet, related_name='solution_radiance_function')
	orientation_function = models.OneToOneField(TermSet, related_name='solution_orientation_function')
	termination_function = models.OneToOneField(TermSet, related_name='solution_termination_function')

	def __init__(self, *args, **kwargs):
		super(Solution, self).__init__(*args, **kwargs)

		def create_termset():
			ts = TermSet()
			ts.save()
			ts.mutate()
			return ts
		self.length_function = create_termset()
		self.radiance_function = create_termset()
		self.orientation_function = create_termset()
		self.termination_function = create_termset()
		self.plot = Plot(self)

	def mutate(self):
		self.length_function.mutate()
		self.radiance_function.mutate()
		self.orientation_function.mutate()
		self.termination_function.mutate()

# from django.db.models.signals import post_save
# from signals import create_initial_data
# post_save.connect(create_initial_data, sender=Foo)


class Point(object):
	def __unicode__(self):
		return str(self.x) + ', ' + str(self.y)

	def __init__(self, x, y):
		self.x = x
		self.y = y

	def dist_to_origin(self):
		return hypot(self.x, self.y)

	def radiance(self, solution):
		dist = self.dist_to_origin()
		return solution.radiance_function.f(dist)

	def orientation(self, solution):
		dist = self.dist_to_origin()
		return solution.orientation_function.f(dist)

	def segments(self, solution):
		orientation = self.orientation(solution)
		radiance = self.radiance(solution)
		radiance_begin = orientation - (radiance / 2)
		# radiance_end = orientation + (radiance / 2)
		step = radiance / (constants.BRANCHING_FACTOR - 1)
		segments = []

		if step == 0:
			segments.append(Segment(self, orientation))
		else:
			for n in range(0, constants.BRANCHING_FACTOR):
				segments.append(Segment(self, radiance_begin + (step * n)))
			# for angle in range(radiance_begin, radiance_end, step):
			# 	segments.append(Segment(self, angle))
		return segments


class Segment(object):
	def __init__(self, base, angle):
		self.base = base
		self.angle = angle

	def length(self, solution):
		dist = self.base.dist_to_origin()
		return solution.length_function.f(dist)

	def end(self, solution):
		x = self.base.x + self.length(solution) * cos(self.angle)
		y = self.base.y + self.length(solution) * sin(self.angle)
		return Point(x, y)


class Plot(object):
	segments = []

	def __init__(self, solution):
		self.origin = Point(64, 64)
		self.solution = solution

	def draw(self, seq):
		im = Image.new('RGBA', (128, 128), (30, 30, 30, 255))
		draw = ImageDraw.Draw(im)
		for segment in self.origin.segments(self.solution):
			end = segment.end(self.solution)
			draw.line(((self.origin.x, self.origin.y), (end.x, end.y)))
			print 'from ' + self.origin.__unicode__() + ' to ' + end.__unicode__()
			for segment2 in end.segments(self.solution):
				end2 = segment2.end(self.solution)
				draw.line(((end.x, end.y), (end2.x, end2.y)))
				print ' from ' + end.__unicode__() + ' to ' + end2.__unicode__()
				for segment3 in end2.segments(self.solution):
					end3 = segment3.end(self.solution)
					draw.line(((end2.x, end2.y), (end3.x, end3.y)))
					print '  from ' + end2.__unicode__() + ' to ' + end3.__unicode__()
		im.save("out.png." + str(seq), "PNG")
