from manimlib import *

class LittleCreature(SVGMobject):
	CONFIG = {
		'flipped': False,
		'mood': 'plain',
		'looking_dir': OUT
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

		self.look(self.looking_dir)

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
		new_self=LittleCreature(new_mood, flipped=self.flipped, looking_dir=self.looking_dir)
		new_self.look(self.looking_dir)
		new_self.move_to(self)
		new_self.match_height(self)
		self.become(new_self)
		return self

	# Related to eye contact.

	def look(self,dir=OUT):
		dir=dir.copy()
		#计算单位向量
		dir/=np.linalg.norm(dir) 
		self.looking_dir=dir

		dir_xy=dir.copy(); dir_xy[2]=0.0 #平面上的投影
		EYE_MOV_DIS=0.075
		self.eyes[0].move_to(self.eye_anchors[0]).shift(dir_xy*EYE_MOV_DIS)
		self.eyes[1].move_to(self.eye_anchors[1]).shift(dir_xy*EYE_MOV_DIS)
		return self

	def look_at(self, point_or_mobject):
		#计算视线方向
		眉心=(self.eyes[0].get_center()+self.eyes[1].get_center())/2
		if isinstance(point_or_mobject, Mobject):
			mobj=point_or_mobject
			point=mobj.get_center()
		else:
			point=point_or_mobject
		dir=point-眉心
		return self.look(dir)
	
	def make_eye_contact(self):
		return self.look(OUT)

	# used for Blink animation.
	def _blink(self):
		eyes=self.eyes
		eye_bottom_y = eyes.get_bottom()[1]
		eyes.apply_function(
			lambda p: [p[0], eye_bottom_y+(p[1]-eye_bottom_y)/20, p[2]]
		)
		return self

	# Magic overrides that fix things.

	def get_shader_wrapper_list(self):
		# SVGMobject默认会返回两个shader_wrapper, one for fill and one for stroke
		# 导致所有子路径的fill和stroke分别被一块渲染了，上下层的stroke会相交，无法正确显示重叠关系
		# 因此这里重写这一方法，返回所有sub/son的shader_wrapper，这样每个路径就会分开渲染。
		ret=[]
		for sub in self:
			ret+=sub.get_shader_wrapper_list()
		return ret

	def interpolate(self, mobject1: VMobject, mobject2: VMobject, alpha: float, *args, **kwargs):
		ret = super().interpolate(mobject1, mobject2, alpha, *args, **kwargs)
		# interpolate custom attributes correctly.
		self.looking_dir = interpolate(
			mobject1.looking_dir,
			mobject2.looking_dir,
			alpha
		)
		return ret

	def copy(self, deep: bool = False):
		ret = super().copy(deep)
		# remake refs, which is screwed up by the previous super().copy().
		ret._name_parts()
		return ret

class Blink(ApplyMethod):
	CONFIG = {
		# param ref: Fast: 0.2, Medium: 0.3, Slow: 0.4
		'run_time': 0.3,
		'rate_func': there_and_back
	}
	def __init__(self, w: LittleCreature, **kwargs):
		super().__init__(w._blink, **kwargs)
	def finish(self) -> None:
		super().finish()
		self.interpolate(0)