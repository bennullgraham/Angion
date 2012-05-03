from math import sin, cos, e, pi, hypot, copysign
import sys
import constants
import copy
from random import choice, random, seed
from PIL import Image, ImageDraw
from multiprocessing import Pool
seed()


class TermSet(object):
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
				t = choice(self.terms)
				t.mutate()
				mutate_count += 1


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

		return f.format(outer=float(self.outerMultiplier), inner=float(self.innerMultiplier))

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
			if x == 0:
				return random() - 0.5
			vary = (random() - 0.5) * constants.MUTE_VARIABILITY * 2 * abs(x)
			x = x + vary
			if x > 100:
				x = 100
			elif x < -100:
				x = -100
			return x
		self.innerMultiplier = scale(self.innerMultiplier)
		self.outerMultiplier = scale(self.outerMultiplier)
		return self


class Solution(object):
	def prime(self):
		def create_termset():
			seed()
			ts = TermSet()
			r = copy.deepcopy(ts)
			r.mutate()
			return r

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

	def point_set(self):
		origin = OriginPoint()
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
				return min([(point[0] - s.x) ** 2 + (point[1] - s.y) ** 2 for s in point_set], key=abs)
			except OverflowError:
				return sys.float_info.max

		def point_length(point):
			try:
				return sum([segment.length(self) for segment in point.segments(self)])
			except OverflowError:
				return sys.float_info.max

		def bounds_penalty(point):
			if point.x < constants.PLOT_MARGIN or point.x > (constants.PLOT_SIZE - constants.PLOT_MARGIN):
				return 10000
			if point.y < constants.PLOT_MARGIN or point.y > (constants.PLOT_SIZE - constants.PLOT_MARGIN):
				return 10000
			return 0

		eval_set = [(x, y) for x in range(constants.PLOT_MARGIN, constants.PLOT_SIZE - constants.PLOT_MARGIN, 16) for y in range(constants.PLOT_MARGIN, constants.PLOT_SIZE - constants.PLOT_MARGIN, 16)]
		point_set = self.point_set()

		service_penalty = sum(map(minimum_service_distance, eval_set)) ** 0.5
		length_penalty = sum(map(point_length, point_set)) ** 0.5
		bounds_penalty = sum(map(bounds_penalty, point_set))

		# print "  service: {}, length: {}".format(service_penalty, length_penalty)
		self.fitness = 1 / (service_penalty + length_penalty + bounds_penalty)
		return self


class Point(object):
	def __unicode__(self):
		return str(self.x) + ', ' + str(self.y)

	def __init__(self, x, y, depth=0, parent_orientation=0):
		self.x = x
		self.y = y
		self.depth = depth
		self.dist_to_origin = self._dist_to_origin()
		self.parent_orientation = parent_orientation
		self.segment_count = constants.BRANCHING_FACTOR

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
		return solution.radiance_function.f(dist)  # % pi  # -90 --> +90

	def orientation(self, solution):
		dist = self.dist_to_origin
		delta = solution.orientation_function.f(dist)  # % (pi * 2 / 8)) - ((pi * 2 / 8) / 2)  # -22.5 --> +22.5
		return self.parent_orientation + delta

	def segments(self, solution):
		orientation = self.orientation(solution) % (2 * pi)
		radiance = self.radiance(solution) % (2 * pi)
		sweep_begin = orientation - (radiance / 2)
		sweep_step = radiance / (self.segment_count)
		segments = []

		if sweep_step == 0:
			segments.append(Segment(self, orientation))
		else:
			for n in range(0, self.segment_count):
				segments.append(Segment(self, sweep_begin + (sweep_step * n)))
		return segments

	def terminate(self, solution):
		return False
		dist = self.dist_to_origin
		return 1 / solution.termination_function.f(dist) < 0.5


class OriginPoint(Point):

	def __init__(self):
		self.x = constants.ORIGIN_X
		self.y = constants.ORIGIN_Y
		self.depth = 0
		self.dist_to_origin = 0
		self.parent_orientation = 0
		self.segment_count = 4

	def radiance(self, solution):
		return 2 * pi

	def orientation(self, solution):
		return 0


class Segment(object):
	def __init__(self, base, angle):
		self.base = base
		self.angle = angle

	def length(self, solution):
		dist = self.base.dist_to_origin
		#try:
		return abs(solution.length_function.f(dist))
		#except OverflowError:
		#	return sys.float_info.max
		#	pass

	def end(self, solution):
		# bound = lambda x: min(max(0, x), constants.PLOT_SIZE)
		try:
			x = self.base.x + self.length(solution) * cos(self.angle)
			y = self.base.y + self.length(solution) * sin(self.angle)
			return Point(x, y, self.base.depth + 1, self.angle)
		except ValueError:
			print "valueerror"
			print self.length(solution)
			print self.angle
		except e:
			raise e


class Plot(object):
	segments = []

	def __init__(self, solution):
		self.solution = solution

	def draw(self, seq):
		im = Image.new('RGBA', (constants.PLOT_SIZE, constants.PLOT_SIZE), (30, 30, 30, 255))
		draw = ImageDraw.Draw(im)
		draw.line((
			(constants.PLOT_MARGIN, constants.PLOT_MARGIN),
			(constants.PLOT_MARGIN, constants.PLOT_SIZE - constants.PLOT_MARGIN),
			(constants.PLOT_SIZE - constants.PLOT_MARGIN, constants.PLOT_SIZE - constants.PLOT_MARGIN),
			(constants.PLOT_SIZE - constants.PLOT_MARGIN, constants.PLOT_MARGIN),
			(constants.PLOT_MARGIN, constants.PLOT_MARGIN)),
			fill="rgb(0,0,0)"
		)
		points = self.solution.point_set()
		points.reverse()
		for point in points:
			c = 255 - (200 * point.depth) / constants.RECURSION_LIMIT
			for segment in point.segments(self.solution):
				end = segment.end(self.solution)
				draw.line((point.x, point.y, end.x, end.y), fill="rgb({r},{g},{b})".format(r=c, g=c, b=c))

		im.save("out." + str(seq) + ".png", "PNG")


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
	sn.length_function = copy.deepcopy(s1.length_function) if random() > 0.5 else copy.deepcopy(s2.length_function)
	sn.radiance_function = copy.deepcopy(s1.radiance_function) if random() > 0.5 else copy.deepcopy(s2.radiance_function)
	sn.orientation_function = copy.deepcopy(s1.orientation_function) if random() > 0.5 else copy.deepcopy(s2.orientation_function)
	sn.termination_function = copy.deepcopy(s1.termination_function) if random() > 0.5 else copy.deepcopy(s2.termination_function)
	return sn

for lap in range(100000):
	candidates = sorted(solutions, key=lambda s: s.fitness)[:3]
	solutions = candidates[:]  # keep the best few from previous round
	solutions = map(lambda s: s.mutate(), solutions)  # stir
	solutions.extend([cross(s1, s2) for s1 in candidates for s2 in candidates])  # mix up the best few from previous round
	solutions.append(new_solution())  # add a fresh solution

	solutions = pool.map(solve, solutions)  # compute point-sets and fitnesses

	solutions.append(fittest)  # keep the best from last round, un-mutated
	fittest = max(solutions, key=lambda s: s.fitness)

	last_fit = this_fit
	this_fit = fittest.fitness
	improvement = 0 if last_fit == 0 else (this_fit / last_fit) - 1

	if last_fit != this_fit or lap == 0:
		p = Plot(fittest)
		p.draw(lap)
		print "{lap}: {fitness} ({improvement:+.2%})".format(lap=lap, fitness=this_fit, improvement=improvement)
		print "       length:      {length_function}".format(length_function=fittest.length_function.__unicode__())
		print "       radiance:    {radiance_function}".format(radiance_function=fittest.radiance_function.__unicode__())
		print "       orientation: {orientation_function}".format(orientation_function=fittest.orientation_function.__unicode__())
		print ""
	elif lap % 1000 == 0:
		print "{lap}".format(lap=lap)