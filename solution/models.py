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
		s = sum(map(lambda f: f.f(x), terms))
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
			ttype = choice(('EXP', 'POLY', 'TRIG', 'CNST'))
			if not terms:
				# first term always a constant
				ttype = 'CNST'
			bt = BaseTerm(term_set_id=self.pk, term_type=ttype)
			bt.mutate()
			bt.save()

		# modify some term constants
		if terms:
			while mutate_count < constants.NUM_MUTE_TERMS:
				t = choice(terms)
				t.mutate()
				t.save()
				mutate_count += 1

	def copy(self):
		orig_terms = self.baseterm_set.all()
		ts = TermSet()
		ts.save()
		for orig_term in orig_terms:
			new_term = orig_term.copy(term_set_id=ts.id)
			new_term.save()
		return ts


class BaseTerm(models.Model):
	TERM_TYPES = (
		(u'EXP',  u'Exponential'),
		(u'POLY', u'Polynomial'),
		(u'TRIG', u'Trigonometric'),
		(u'CNST', u'Constant'),
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
		elif self.term_type == 'CNST':
			f = '({:.2}+{:.2})'
		else:
			return super(BaseTerm, self).__unicode__()

		return f.format(self.outerMultiplier, self.innerMultiplier)

	def f(self, x):
		fx = None
		if self.term_type == 'EXP':
			f = lambda i, o, x: o * (x ** i)
		elif self.term_type == 'TRIG':
			f = lambda i, o, x: o * sin(x * i)
		elif self.term_type == 'POLY':
			f = lambda i, o, x: o * e ** (x * i)
		elif self.term_type == 'CNST':
			f = lambda i, o, x: o + i
		else:
			raise Exception("Term type unknown")

		while fx == None:
			try:
				fx = f(self.innerMultiplier, self.outerMultiplier, x)
			except OverflowError:
				print "Overflowed: " + self.__unicode__()
				# do some fuzzing and reduction to try and avoid an overflow
				self.innerMultiplier = (self.innerMultiplier + random()) / constants.OVERFLOW_REDUCTION_DIVISOR
				self.outerMultiplier = (self.outerMultiplier + random()) / constants.OVERFLOW_REDUCTION_DIVISOR
				pass
			except Exception:
				fx = 0
				pass

		# print self.__unicode__() + " = " + str(fx) + ", x = " + str(x)
		return fx

	def mutate(self):
		def scale(x):
			seed()
			vary = (random() - 0.5) * constants.MUTE_VARIABILITY * 2 * max(0.1, abs(x))
			x = x + vary
			if x > -0.1 and x < 0.1:
				x = scale(x)
			return x
		self.innerMultiplier = scale(self.innerMultiplier)
		self.outerMultiplier = scale(self.outerMultiplier)
		return self

	def copy(self, term_set_id):
		c = BaseTerm()
		c.innerMultiplier = self.innerMultiplier
		c.outerMultiplier = self.outerMultiplier
		c.term_type = self.term_type
		c.term_set_id = term_set_id
		return c


class Solution(models.Model):
	# parent = models.OneToOneField('self', null=True)
	length_function = models.OneToOneField(TermSet, related_name='solution_length_function')
	radiance_function = models.OneToOneField(TermSet, related_name='solution_radiance_function')
	orientation_function = models.OneToOneField(TermSet, related_name='solution_orientation_function')
	termination_function = models.OneToOneField(TermSet, related_name='solution_termination_function')

	def prime(self):
		def create_termset():
			ts = TermSet()
			ts.save()
			ts.mutate()
			return ts
		self.length_function = create_termset()
		self.radiance_function = create_termset()
		self.orientation_function = create_termset()
		self.termination_function = create_termset()

	def mutate(self):
		self.length_function.mutate()
		self.radiance_function.mutate()
		self.orientation_function.mutate()
		self.termination_function.mutate()
		return self

	def copy(self):
		s = Solution()
		s.length_function = self.length_function.copy()
		s.radiance_function = self.length_function.copy()
		s.orientation_function = self.length_function.copy()
		s.termination_function = self.length_function.copy()
		return s

	def point_set(self):
		origin = Point(constants.ORIGIN_X, constants.ORIGIN_Y, depth=0)
		points = []

		def recurse(base):
			points.append(base)
			if base.depth < constants.RECURSION_LIMIT and not base.terminate(self):
				for segment in base.segments(self):
					recurse(segment.end(self))
		recurse(origin)
		return points

	def fitness(self):
		def minimum_service_distance(point):
			return min([hypot(point[0] - s.x, point[1] - s.y) for s in point_set], key=abs)

		def point_length(point):
			return sum([segment.length(self) for segment in point.segments(self)])

		eval_set = [(x, y) for x in range(0, constants.PLOT_SIZE, 16) for y in range(0, constants.PLOT_SIZE, 16)]
		point_set = self.point_set()
		service_penalty = sum(map(minimum_service_distance, eval_set))
		length_penalty = (sum(map(point_length, point_set)) / 100) ** 2
		# print "  service: {}, length: {}".format(service_penalty, length_penalty)
		return 1 / (service_penalty + length_penalty)
		

class Point(object):
	def __unicode__(self):
		return str(self.x) + ', ' + str(self.y)

	def __init__(self, x, y, depth=0):
		self.x = x
		self.y = y
		self.depth = depth
		self.dist_to_origin = self._dist_to_origin()

	def _dist_to_origin(self):
		return min(constants.PLOT_SIZE, hypot(self.x - constants.ORIGIN_X, self.y - constants.ORIGIN_Y), key=abs)

	def radiance(self, solution):
		dist = self.dist_to_origin
		return solution.radiance_function.f(dist)

	def orientation(self, solution):
		dist = self.dist_to_origin
		return solution.orientation_function.f(dist)

	def segments(self, solution):
		orientation = self.orientation(solution)
		radiance = self.radiance(solution)
		sweep_begin = orientation - (radiance / 2)
		sweep_step = radiance / (constants.BRANCHING_FACTOR - 1)
		segments = []

		if sweep_step == 0:
			segments.append(Segment(self, orientation))
		else:
			for n in range(0, constants.BRANCHING_FACTOR):
				segments.append(Segment(self, sweep_begin + (sweep_step * n)))
		return segments

	def terminate(self, solution):
		return False
		dist = self.dist_to_origin
		return 1 / solution.termination_function.f(dist) < 0.5


class Segment(object):
	def __init__(self, base, angle):
		self.base = base
		self.angle = angle

	def length(self, solution):
		dist = self.base.dist_to_origin
		return max(0, solution.length_function.f(dist))

	def end(self, solution):
		#bound = lambda x: min(max(0, x), constants.PLOT_SIZE)
		x = self.base.x + self.length(solution) * cos(self.angle)
		y = self.base.y + self.length(solution) * sin(self.angle)
		return Point(x, y, self.base.depth + 1)


class Plot(object):
	segments = []

	def __init__(self, solution):
		self.origin = Point(constants.ORIGIN_X, constants.ORIGIN_Y)
		self.solution = solution

	def draw(self, seq):
		print "Drawing..."
		im = Image.new('RGBA', (constants.PLOT_SIZE, constants.PLOT_SIZE), (30, 30, 30, 255))
		draw = ImageDraw.Draw(im)
		points = self.solution.point_set()
		points.reverse()
		for point in points:
			c = 255 / (point.depth / 2 + 1)
			for segment in point.segments(self.solution):
				end = segment.end(self.solution)
				draw.line((point.x, point.y, end.x, end.y), fill="rgb({r},{g},{b})".format(r=c, g=c, b=c))

		im.save("/home/bgraham/dev_py/angion/out." + str(seq) + ".png", "PNG")
