from math import sin, cos, e, pi, hypot, copysign
import sys
import constants
from random import choice, random, seed, uniform
from PIL import Image, ImageDraw
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

	def __init__(self, configuration):
		self.configuration = configuration
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
		origin = OriginPoint(self)
		points = []

		def recurse(base):
			points.append(base)
			if base.depth < self.configuration.RECURSION_LIMIT and not base.terminate():
				segments = base.segments()
				self.total_length += segments[0].length()
				for segment in segments:
					recurse(segment.end())
		recurse(origin)
		return points

	def normalised_segment_set(self):
		origin = OriginPoint()

		def recurse(base):
			r = {'x': base.x, 'y': base.y, 'children': []}
			if base.depth < self.configuration.RECURSION_LIMIT and not base.terminate(self):
				for segment in base.segments(self):
					end_point = segment.end(self)
					# segments.append([base.x, base.y, end_point.x, end_point.y])
					r['children'].append(recurse(end_point))
			return r

		segments = recurse(origin)
		return segments

	def solve(self):
		def in_bounds(p):
			if p.x < self.configuration.PLOT_MARGIN or p.x > (self.configuration.PLOT_SIZE - self.configuration.PLOT_MARGIN):
				return False
			if p.y < self.configuration.PLOT_MARGIN or p.y > (self.configuration.PLOT_SIZE - self.configuration.PLOT_MARGIN):
				return False
			return True

		def to_service_grid_bucket(p):
			return (p.x // self.configuration.SERVICE_GRID_SPACING, p.y // self.configuration.SERVICE_GRID_SPACING)

		def service_level(eval_point):
			# return min([hypot(eval_point[0] - p[0], eval_point[1] - p[1]) for p in quantised_point_set]) ** 2
			return min([(eval_point[0] - p[0]) ** 2 + (eval_point[1] - p[1]) ** 2 for p in quantised_point_set])

		point_set = self.point_set()
		valid_point_set = filter(in_bounds, point_set)
		quantised_point_set = set(map(to_service_grid_bucket, valid_point_set))
		eval_set = [(x, y)
			for x in range(self.configuration.PLOT_MARGIN, self.configuration.PLOT_SIZE - self.configuration.PLOT_MARGIN, self.configuration.SERVICE_GRID_SPACING)
			for y in range(self.configuration.PLOT_MARGIN, self.configuration.PLOT_SIZE - self.configuration.PLOT_MARGIN, self.configuration.SERVICE_GRID_SPACING)
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

	def __init__(self, x, y, solution, depth, parent_orientation):
		self.x = int(x)
		self.y = int(y)
		self.solution = solution
		self.configuration = solution.configuration
		self.depth = depth
		self.dist_to_origin = self._dist_to_origin()
		self.parent_orientation = parent_orientation
		self.segment_count = 1 if self.depth % self.configuration.BRANCH_DISTANCE else self.configuration.BRANCH_SEGMENTS

	def _dist_to_origin(self):
		try:
			return min(self.configuration.PLOT_SIZE, hypot(self.x - self.configuration.ORIGIN_X, self.y - self.configuration.ORIGIN_Y), key=abs)
		except OverflowError:
			return sys.float_info.max

	def radiance(self):
		dist = self.dist_to_origin
		return self.solution.radiance_function.f(dist) % (2 * pi)

	def orientation(self):
		dist = self.dist_to_origin
		delta = self.solution.orientation_function.f(dist)
		return (self.parent_orientation + delta) % (2 * pi)

	def segments(self):
		orientation = self.orientation()
		radiance = self.radiance()
		sweep_begin = orientation - (radiance / 2)
		sweep_step = radiance / (self.segment_count)
		segments = []

		if sweep_step == 0:
			segments.append(Segment(self, orientation))
		else:
			for n in range(0, self.segment_count):
				segments.append(Segment(self, sweep_begin + (sweep_step * n)))
		return segments

	def terminate(self):
		try:
			dist = self.dist_to_origin
			return self.solution.termination_function.f(dist) < self.depth
		except OverflowError:
			return True


class OriginPoint(Point):

	def __init__(self, solution):
		self.solution = solution
		self.configuration = solution.configuration
		self.x = self.configuration.ORIGIN_X
		self.y = self.configuration.ORIGIN_Y
		self.depth = 0
		self.dist_to_origin = 0
		self.parent_orientation = 0
		self.segment_count = 4

	def radiance(self):
		return 2 * pi

	def orientation(self):
		return 0


class Segment(object):
	def __init__(self, base, angle):
		self.solution = base.solution
		self.base = base
		self.angle = angle

	def length(self):
		dist = self.base.dist_to_origin
		return abs(self.solution.length_function.f(dist))

	def end(self):
		x = self.base.x + self.length() * cos(self.angle)
		y = self.base.y + self.length() * sin(self.angle)
		return Point(x, y, self.solution, self.base.depth + 1, self.angle)


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
