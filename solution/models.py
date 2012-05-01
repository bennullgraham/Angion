from math import sin, cos, e, pi, hypot, copysign, log
import sys
import constants
from random import choice, random, seed
from PIL import Image, ImageDraw
from multiprocessing import Pool


class TermSet(object):
	def __init__(self, terms=[]):
		self.terms = terms
		if not self.terms:
			self._add_term()

	def __unicode__(self):
		from string import join
		return join(map(lambda s: str(s), self.terms), ' + ')

	def f(self, x):
		return sum(map(lambda f: f.f(x), self.terms))

	def _add_term(self):
		seed()
		term_type = choice(BaseTerm.TERM_TYPES)
		bt = BaseTerm(term_type=term_type)
		self.terms.append(bt)

	def _delete_term(self):
		t = choice(self.terms)
		self.terms.remove(t)

	def mutate(self):
		mutate_count = 0

		# maybe delete a term
		if self.terms and random() > (1 - constants.DELETE_TERM_CHANCE):
			self._delete_term()

		# potentially create a new term. always do so if there are none.
		if not self.terms or random() > (1 - constants.CREATE_TERM_CHANCE):
			self._add_term()

		# modify some term constants
		if self.terms:
			while mutate_count < constants.NUM_MUTE_TERMS:
				if random() > 0.5:
					t = choice(self.terms)
					t.mutate()
				mutate_count += 1

	def copy(self):
		ts = TermSet(self.terms[:])
		return ts


class BaseTerm(object):
	TERM_TYPES = (
		(u'EXP'),
		(u'POLY'),
		(u'TRIG'),
		(u'CNST'),
	)

	def __init__(self, term_type, innerMultiplier=1, outerMultiplier=1):
		self.term_type = term_type
		self.innerMultiplier = innerMultiplier
		self.outerMultiplier = outerMultiplier

	def __unicode__(self):
		if self.term_type == 'EXP':
			f = '{outer:.2}.e^({inner:.2}x)'
		elif self.term_type == 'TRIG':
			f = '{outer:.2}.sin({inner:.2}x)'
		elif self.term_type == 'POLY':
			f = '{outer:.2}.x^{inner:.2}'
		elif self.term_type == 'CNST':
			f = '({outer:.2}+{inner:.2})'
		else:
			return "er..."

		return f.format(outer=self.outerMultiplier, inner=self.innerMultiplier)

	def f(self, x):
		fx = None
		if self.term_type == 'EXP':
			f = lambda i, o, x: o * (x ** i)
		elif self.term_type == 'TRIG':
			f = lambda i, o, x: o * sin(x * i)
		elif self.term_type == 'POLY':
			f = lambda i, o, x: o * e ** (x * i)
		elif self.term_type == 'CNST':
			f = lambda i, o, x: o * i
		else:
			raise Exception("Term type unknown")

		while fx == None:
			try:
				fx = f(self.innerMultiplier, self.outerMultiplier, x)
			except OverflowError:
				# return largest float with correct sign
				i_sign = copysign(1, self.innerMultiplier)
				o_sign = copysign(1, self.innerMultiplier)
				fx = copysign(sys.float_info.max, f(i_sign, o_sign, x))
				pass
			except ZeroDivisionError:
				fx = 0
				pass

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

	def copy(self):
		bt = BaseTerm(
			term_type=self.term_type,
			innerMultiplier=self.innerMultiplier,
			outerMultiplier=self.outerMultiplier
		)
		return bt


class Solution(object):
	def prime(self):
		def create_termset():
			ts = TermSet()
			ts.mutate()
			return ts
		self.fitness = 0
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

	def solve(self):
		def minimum_service_distance(point):
			try:
				return min([hypot(point[0] - s.x, point[1] - s.y) for s in point_set], key=abs)
			except OverflowError:
				return sys.float_info.max

		def point_length(point):
			try:
				return sum([segment.length(self) for segment in point.segments(self)])
			except OverflowError:
				return sys.float_info.max

		eval_set = [(x, y) for x in range(0, constants.PLOT_SIZE, 32) for y in range(0, constants.PLOT_SIZE, 32)]
		point_set = self.point_set()
		service_penalty = sum(map(minimum_service_distance, eval_set))
		length_penalty = (sum(map(point_length, point_set)) / 10)
		# print "  service: {}, length: {}".format(service_penalty, length_penalty)
		self.fitness = 1 / (service_penalty + length_penalty)
		return self
		

class Point(object):
	def __unicode__(self):
		return str(self.x) + ', ' + str(self.y)

	def __init__(self, x, y, depth=0):
		self.x = x
		self.y = y
		self.depth = depth
		self.dist_to_origin = self._dist_to_origin()

	def _dist_to_origin(self):
		try:
			return min(constants.PLOT_SIZE, hypot(self.x - constants.ORIGIN_X, self.y - constants.ORIGIN_Y), key=abs)
		except OverflowError:
			return constants.PLOT_SIZE
			pass
		except e:
			raise e

	def radiance(self, solution):
		dist = self.dist_to_origin
		return solution.radiance_function.f(dist) % (2 * pi)

	def orientation(self, solution):
		dist = self.dist_to_origin
		return solution.orientation_function.f(dist) % (2 * pi)

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
		length = max(0, solution.length_function.f(dist))
		return log(length + 1) * 10

	def end(self, solution):
		# bound = lambda x: min(max(0, x), constants.PLOT_SIZE)
		x = self.base.x + self.length(solution) * cos(self.angle)
		y = self.base.y + self.length(solution) * sin(self.angle)
		return Point(x, y, self.base.depth + 1)


class Plot(object):
	segments = []

	def __init__(self, solution):
		self.origin = Point(constants.ORIGIN_X, constants.ORIGIN_Y)
		self.solution = solution

	def draw(self, seq):
		im = Image.new('RGBA', (constants.PLOT_SIZE, constants.PLOT_SIZE), (30, 30, 30, 255))
		draw = ImageDraw.Draw(im)
		points = self.solution.point_set()
		points.reverse()
		for point in points:
			c = 255 - (point.depth * 32)
			for segment in point.segments(self.solution):
				end = segment.end(self.solution)
				draw.line((point.x, point.y, end.x, end.y), fill="rgb({r},{g},{b})".format(r=c, g=c, b=c))

		im.save("/home/bgraham/dev_py/angion/out." + str(seq) + ".png", "PNG")


def solve(solution):
	return solution.solve()


def new_solution():
	s = Solution()
	s.prime()
	return s

candidates = []
solutions = []
fittest = new_solution()
solutions.append(fittest)
last_fit = 0
this_fit = 0
pool = Pool(8)


def cross(s1, s2):
	sn = Solution()
	sn.length_function = s1.length_function if random() > 0.5 else s2.length_function
	sn.radiance_function = s1.radiance_function if random() > 0.5 else s2.radiance_function
	sn.orientation_function = s1.orientation_function if random() > 0.5 else s2.orientation_function
	sn.termination_function = s1.termination_function if random() > 0.5 else s2.termination_function
	return sn

for lap in range(100):
	candidates = sorted(solutions, key=lambda s: s.fitness)[:2]
	solutions.extend(candidates)  # keep the best few from previous round
	solutions.extend([cross(s1, s2) for s1 in candidates for s2 in candidates])  # mix up the best few from previous round
	solutions.extend([new_solution() for n in range(2)])  # add some fresh solutions

	solutions = map(lambda s: s.mutate(), solutions)  # stir
	solutions = pool.map(solve, solutions)  # compute point-sets and fitnesses

	solutions.append(fittest)  # keep the best from last round, un-mutated
	fittest = max(solutions, key=lambda s: s.fitness)

	last_fit = this_fit
	this_fit = fittest.fitness
	improvement = 0 if last_fit == 0 else (this_fit / last_fit) - 1

	print "fitness = {fitness} ({improvement:+.2%})".format(lap=lap, fitness=this_fit, improvement=improvement)

	p = Plot(fittest)
	p.draw(lap)
