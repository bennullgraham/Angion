from math import sin, cos, e, pi, hypot, copysign
import sys
import constants
import copy
import json
from random import choice, random, seed, uniform
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

		# while fx == None:
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


class Solution(object):

	def __init__(self):
		self.fitness = 0
		self.total_length = None

	def mutate(self):
		self.length_function.mutate()
		self.radiance_function.mutate()
		self.orientation_function.mutate()
		self.termination_function.mutate()
		return self

	def point_set(self):
		self.total_length = 1
		origin = OriginPoint()
		points = []

		def recurse(base):
			points.append(base)
			if base.depth < constants.RECURSION_LIMIT and not base.terminate(self):
				segments = base.segments(self)
				self.total_length += segments[0].length(self)
				for segment in segments:
					recurse(segment.end(self))
		recurse(origin)
		return points

	def normalised_segment_set(self):
		origin = OriginPoint()

		def recurse(base):
			r = {'x': base.x, 'y': base.y, 'children': []}
			if base.depth < constants.RECURSION_LIMIT and not base.terminate(self):
				for segment in base.segments(self):
					end_point = segment.end(self)
					# segments.append([base.x, base.y, end_point.x, end_point.y])
					r['children'].append(recurse(end_point))
			return r

		segments = recurse(origin)
		return segments

	def solve(self):
		def in_bounds(p):
			if p.x < constants.PLOT_MARGIN or p.x > (constants.PLOT_SIZE - constants.PLOT_MARGIN):
				return False
			if p.y < constants.PLOT_MARGIN or p.y > (constants.PLOT_SIZE - constants.PLOT_MARGIN):
				return False
			return True

		def to_service_grid_bucket(p):
			return (p.x // constants.SERVICE_GRID_SPACING, p.y // constants.SERVICE_GRID_SPACING)

		def service_level(eval_point):
			# return min([hypot(eval_point[0] - p[0], eval_point[1] - p[1]) for p in quantised_point_set]) ** 2
			return min([(eval_point[0] - p[0]) ** 2 + (eval_point[1] - p[1]) ** 2 for p in quantised_point_set])

		point_set = self.point_set()
		valid_point_set = filter(in_bounds, point_set)
		quantised_point_set = set(map(to_service_grid_bucket, valid_point_set))
		eval_set = [(x, y)
			for x in range(constants.PLOT_MARGIN, constants.PLOT_SIZE - constants.PLOT_MARGIN, constants.SERVICE_GRID_SPACING)
			for y in range(constants.PLOT_MARGIN, constants.PLOT_SIZE - constants.PLOT_MARGIN, constants.SERVICE_GRID_SPACING)
		]
		self.service_penalty = float(sum(map(service_level, eval_set)) / len(eval_set))
		self.length_penalty = max(1.0, (self.total_length / len(point_set)))
		self.complexity_penalty = int(max(0, len(point_set))) ** 2
		self.bounds_penalty = max(1, (len(point_set) - len(valid_point_set)) * 100) ** 2
		self.fitness = (self.service_penalty + self.length_penalty + self.complexity_penalty + self.bounds_penalty) ** -1
		return self


class Point(object):
	def __unicode__(self):
		return str(self.x) + ', ' + str(self.y)

	def __init__(self, x, y, depth=0, parent_orientation=0):
		self.x = int(x)
		self.y = int(y)
		self.depth = depth
		self.dist_to_origin = self._dist_to_origin()
		self.parent_orientation = parent_orientation
		self.segment_count = 1 if self.depth % constants.BRANCH_DISTANCE else constants.BRANCH_SEGMENTS

	def _dist_to_origin(self):
		try:
			return min(constants.PLOT_SIZE, hypot(self.x - constants.ORIGIN_X, self.y - constants.ORIGIN_Y), key=abs)
		except OverflowError:
			return sys.float_info.max

	def radiance(self, solution):
		dist = self.dist_to_origin
		return solution.radiance_function.f(dist) % (2 * pi)

	def orientation(self, solution):
		dist = self.dist_to_origin
		delta = solution.orientation_function.f(dist)
		return (self.parent_orientation + delta) % (2 * pi)

	def segments(self, solution):
		orientation = self.orientation(solution)
		radiance = self.radiance(solution)
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
		try:
			dist = self.dist_to_origin
			return solution.termination_function.f(dist) < self.depth
		except OverflowError:
			return True


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
		return abs(solution.length_function.f(dist))

	def end(self, solution):
		x = self.base.x + self.length(solution) * cos(self.angle)
		y = self.base.y + self.length(solution) * sin(self.angle)
		return Point(x, y, self.base.depth + 1, self.angle)


class Plot(object):
	segments = []

	def __init__(self, solution):
		self.solution = solution

	def draw(self, seq):
		# (0,150,255) [0x0096ff] -> (42,22,69) [0x45162a]
		def colour_lookup(ratio, shade=False):
			r = 000 + (ratio * (42 - 000))
			g = 150 + (ratio * (22 - 150))
			b = 255 + (ratio * (69 - 255))
			if shade:
				r /= 3.0
				g /= 3.0
				b /= 3.0
			return "rgb({},{},{})".format(int(r), int(g), int(b))

		im = Image.new('RGBA', (constants.PLOT_SIZE, constants.PLOT_SIZE), (10, 4, 27, 255))
		draw = ImageDraw.Draw(im)
		draw.line((
			(constants.PLOT_MARGIN, constants.PLOT_MARGIN),
			(constants.PLOT_MARGIN, constants.PLOT_SIZE - constants.PLOT_MARGIN),
			(constants.PLOT_SIZE - constants.PLOT_MARGIN, constants.PLOT_SIZE - constants.PLOT_MARGIN),
			(constants.PLOT_SIZE - constants.PLOT_MARGIN, constants.PLOT_MARGIN),
			(constants.PLOT_MARGIN, constants.PLOT_MARGIN)),
			fill="rgb(24,12,54)"
		)
		points = self.solution.point_set()
		# sort by depth so oldest segments are drawn on top
		points.sort(key=lambda p: -p.depth)

		for point in points:
			fill = colour_lookup(float(point.depth) / (points[0].depth + 1), shade=True)
			service_x = (point.x // constants.SERVICE_GRID_SPACING) * constants.SERVICE_GRID_SPACING
			service_y = (point.y // constants.SERVICE_GRID_SPACING) * constants.SERVICE_GRID_SPACING
			draw.rectangle(
				(service_x + 1, service_y + 1, service_x + constants.SERVICE_GRID_SPACING - 1, service_y + constants.SERVICE_GRID_SPACING - 1),
				fill=fill  # "rgb(25,20,37,20)"
			)

		for point in points:
			fill = colour_lookup(float(point.depth) / (points[0].depth + 1))
			for segment in point.segments(self.solution):
				end = segment.end(self.solution)
				if end.x >= 0 and end.y >= 0 and end.x <= constants.PLOT_SIZE and end.y <= constants.PLOT_SIZE:
					draw.line((point.x, point.y, end.x, end.y), fill=fill)
		im.save("out." + str(seq) + ".png", "PNG")


def solve(solution):
	return solution.solve()


def mutate(solution):
	return solution.mutate()


def new_solution():

	def new_baseterm():
		return BaseTerm(choice(BaseTerm.TERM_TYPES), innerMultiplier=uniform(-2, 2), outerMultiplier=uniform(-5, 5))

	s = Solution()
	s.length_function = TermSet(init_terms=[new_baseterm()])
	s.radiance_function = TermSet(init_terms=[new_baseterm()])
	s.orientation_function = TermSet(init_terms=[new_baseterm()])
	s.termination_function = TermSet(init_terms=[new_baseterm()])
	return s

candidates = []
solutions = []
fittest = Solution()
fittest.length_function = TermSet(init_terms=[BaseTerm('CNST', innerMultiplier=3.0, outerMultiplier=3.0), BaseTerm('LINE', innerMultiplier=-0.01, outerMultiplier=0.1)])
fittest.radiance_function = TermSet(init_terms=[BaseTerm('CNST', innerMultiplier=1.0, outerMultiplier=1.5)])
fittest.orientation_function = TermSet(init_terms=[BaseTerm('CNST', innerMultiplier=0.0, outerMultiplier=0.0)])
fittest.termination_function = TermSet(init_terms=[BaseTerm('CNST', innerMultiplier=3.0, outerMultiplier=3.0)])
fittest.solve()

solutions.append(fittest)
last_fit = 0
this_fit = fittest.fitness
high_fit = this_fit
pool = Pool(4)


def cross(s1, s2):
	sn = Solution()
	sn.length_function = copy.deepcopy(s1.length_function) if random() > 0.5 else copy.deepcopy(s2.length_function)
	sn.radiance_function = copy.deepcopy(s1.radiance_function) if random() > 0.5 else copy.deepcopy(s2.radiance_function)
	sn.orientation_function = copy.deepcopy(s1.orientation_function) if random() > 0.5 else copy.deepcopy(s2.orientation_function)
	sn.termination_function = copy.deepcopy(s1.termination_function) if random() > 0.5 else copy.deepcopy(s2.termination_function)
	return sn

for lap in range(1000000):
	candidates = sorted(solutions, key=lambda s: s.fitness)[:3]
	# candidates.extend([new_solution() for n in range(2)])
	# keep and mutate the best few from previous round
	solutions = pool.map(mutate, [copy.deepcopy(c) for c in candidates])

	# keep the best few from previous round unmutated
	# solutions.extend([copy.deepcopy(c) for c in candidates])

	# mix up the functions from the best few from previous round
	solutions.extend([cross(s1, s2) for s1 in candidates for s2 in candidates for n in range(1)])

	solutions = pool.map(solve, solutions)  # compute point-sets and fitnesses
	# solutions.append(fittest)  # keep the best from last round, un-mutated
	fittest = max(solutions, key=lambda s: s.fitness)

	last_fit = this_fit
	this_fit = fittest.fitness
	improvement = 0 if last_fit == 0 else (this_fit / high_fit) - 1

	if this_fit > high_fit or lap == 0:
		high_fit = this_fit
		p = Plot(fittest)
		p.draw(lap)
		f = open('out.{lap}.json'.format(lap=lap), 'w')
		json.dump(fittest.normalised_segment_set(), f)
		f.close()
		print "{lap}: {fitness} ({improvement:+.2%}) from {count} solutions".format(lap=lap, fitness=this_fit, improvement=improvement, count=len(solutions))
		print "       length:      {length_function}".format(length_function=fittest.length_function.__unicode__())
		print "       radiance:    {radiance_function}".format(radiance_function=fittest.radiance_function.__unicode__())
		print "       orientation: {orientation_function}".format(orientation_function=fittest.orientation_function.__unicode__())
		print "       termination: {termination_function}".format(termination_function=fittest.termination_function.__unicode__())
		print "       penalties:   service [{service_penalty:.2}] length [{length_penalty:.2}] complexity [{complexity_penalty}] bounds [{bounds_penalty}]".format(service_penalty=fittest.service_penalty, length_penalty=fittest.length_penalty, complexity_penalty=fittest.complexity_penalty, bounds_penalty=fittest.bounds_penalty)
		print ""
	elif lap % 1000 == 0:
		print "{lap}".format(lap=lap)
