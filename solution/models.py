from django.db import models
from termset.models import TermSet
from math import hypot, cos, sin
from termset import constants


class Solution(models.Model):
	parent = models.ForeignKey('self', null=True)
	length_termset = models.ForeignKey(TermSet)
	radiance_termset = models.ForeignKey(TermSet)
	orientation_termset = models.ForeignKey(TermSet)


class Point(object):
	def __unicode__(self):
		return self.x + ', ' + self.y

	def __init__(self, x, y):
		self.x = x
		self.y = y

	def dist_to_origin(self):
		return hypot(self.x, self.y)

	def radiance(self):
		dist = self.dist_to_origin()
		return Solution.radiance_termset.f(dist)

	def orientation(self):
		dist = self.dist_to_origin
		return Solution.orientation_termset.f(dist)

	def segments(self):
		orientation = self.orientation()
		radiance = self.radiance()
		radiance_begin = orientation - (radiance / 2)
		radiance_end = orientation + (radiance / 2)
		step = radiance / (constants.BRANCHING_FACTOR - 1)
		segments = []

		for angle in range(radiance_begin, radiance_end, step):
			segments.add(Segment(self, angle))
		return segments


class Segment(object):
	def __init__(self, base, angle):
		self.base = base
		self.angle = angle
	
	def length(self):
		dist = self.base.dist_to_origin()
		return Solution.length_termset.f(dist)

	def end(self):
		x = self.base.x + self.length() * cos(self.angle)
		y = self.base.y + self.length() * sin(self.angle)
		return Point(x, y)


class Plot(object):
	segments = []

	def __init__(self):
		self.origin = Point(0, 0)
		for segment in self.origin.segments():
			print segment.end()
