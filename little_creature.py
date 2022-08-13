from manimlib import *

class LittleCreature(SVGMobject):
	CONFIG = {
		'flipped': False,
		'mood': 'plain'
	}
	def __init__(self, mood='plain', flipped=False, **kwargs):
		super().__init__(f'LittleCreature_{mood}.svg', **kwargs)
		
		self._name_parts()

		# set styles
		self.set_fill(color=GREY_A)
		self.eyes.set_fill(BLACK)
		#self.mouth.set_fill(BLACK)

		self.set_stroke(color=BLACK)
		self.body.set_stroke(width=6)
		self.hands.set_stroke(width=4)
		self.mouth.set_stroke(width=4)
		self.eyes.set_stroke(width=0)

		self.eye_anchors.set_opacity(0)

		# 由于SVGMobject的初始化中会调用一次flip，
		# screwing up the flipped attribute
		# 因此这里得重设一次
		self.flipped=False
		if flipped: self.flip()
	def _name_parts(self):
		self.body=self[0]
		self.mouth=self[1]
		self.eyes=self[2:4]
		self.eye_anchors=self[4:6]
		self.hands=self[6:8]

	def flip(self, axis: np.ndarray = UP, **kwargs):
		self.flipped=not self.flipped
		return super().flip(axis, **kwargs)

	def set_color(self, color, recurse=False):
		self.body.set_fill(color=color)
		self.hands.set_fill(color=color)
		return self

	def change_mood(self, new_mood):
		new_self=LittleCreature(new_mood, flipped=self.flipped)
		new_self.move_to(self)
		new_self.match_height(self)
		self.become(new_self)
		return self

	# some little magic.
	def get_shader_wrapper_list(self):
		# SVGMobject默认会返回两个shader_wrapper, one for fill and one for stroke
		# 导致所有子路径的fill和stroke分别被一块渲染了，上下层的stroke会相交，无法正确显示重叠关系
		# 因此这里重写这一方法，返回所有sub/son的shader_wrapper，这样每个路径就会分开渲染。
		ret=[]
		for sub in self:
			ret+=sub.get_shader_wrapper_list()
		return ret

		
