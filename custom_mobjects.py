from manimlib import *

from manimhub.constants import *

class Check(SVGMobject):
	def __init__(self, **kwargs):
		super().__init__('check.svg', **kwargs)
		self.set_stroke(width=0)

class Cross(SVGMobject):
	def __init__(self, **kwargs):
		super().__init__('cross.svg', **kwargs)
		self.set_stroke(width=0)