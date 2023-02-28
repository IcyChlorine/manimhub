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

	#def flip(self, **kwargs):
		#for sub in self:
		#	sub.reverse_points()
		#super().flip()
		#self.rotate(TAU / 2, UP, **kwargs)
		#self.flipped=not self.flipped
		#return self
	def flip(self, axis: np.ndarray = UP, **kwargs):
		self.flipped=not self.flipped
		return super().flip(axis, **kwargs)

	def set_color(self, color, recurse=False):
		self.body.set_fill(color=color)
		self.hands.set_fill(color=color)
		return self

	def change_mood(self, new_mood):
		new_self=LittleCreature(new_mood, flipped=self.flipped)
		#new_self.move_to(self)
		#new_self.match_height(self)
		#new_self.match_style(self)
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

		
# 与之前的PiCreature保持动画接口兼容的代码。
class _LittleCreature_compatible(SVGMobject):
	def __init__(self, mood='plain', flipped=False, looking_dir=OUT, **kwargs):
		super().__init__(f'LittleCreature_{mood}.svg', **kwargs)
		
		self._name_parts()
		self._init_styles()

		self.flipped=False
		if flipped: self.flip()
		self.look(looking_dir)


	def _init_styles(self):
		self.set_fill(color=GREY_A)
		self.eyes.set_fill(BLACK)
		#self.mouth.set_fill(BLACK)

		self.set_stroke(color=BLACK)
		self.body.set_stroke(width=6)
		self.hands.set_stroke(width=4)
		self.mouth.set_stroke(width=4)
		self.eyes.set_stroke(width=0)

		self.eye_anchors.set_opacity(0)

	def _name_parts(self):
		self.body=self[0]
		self.mouth=self[1]
		self.eyes=self[2:4]
		self.eye_anchors=self[4:6]
		self.hands=self[6:8]

	def flip(self, **kwargs):
		#for sub in self:
		#	sub.reverse_points()
		super().flip()
		#self.rotate(TAU / 2, UP, **kwargs)
		self.flipped=not self.flipped
		return self
	
	def set_color(self, color, recurse=False):
		self.body.set_fill(color=color)
		self.hands.set_fill(color=color)
		return self

	def change_mood(self, new_mood):
		new_self=_LittleCreature_compatible(new_mood, flipped=self.flipped)
		new_self.move_to(self)
		new_self.match_height(self)
		new_self.match_style(self)
		new_self.look(self.looking_dir)
		self.become(new_self)
		return self

	#alias for compatibility
	def change_mode(self, new_mode):
		return self.change_mood(new_mode)

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

	def blink(self):
		eyes=self.eyes
		eye_bottom_y = eyes.get_bottom()[1]
		eyes.apply_function(
			lambda p: [p[0], eye_bottom_y+(p[1]-eye_bottom_y)/20, p[2]]
		)
		return self

	#for compatibility.
	def get_extra_symbol(self):#only for the '!' in surprised mode NOW
		if hasattr(self,'extra_symbol'): return self.extra_symbol
		#else
		extra_symbol=SVGMobject('LittleCreature_surprised_symbol.svg')
		extra_symbol.scale(0.25).set_color(RED)\
			.next_to(self,UR)\
			.shift(LEFT*0.6+DOWN*0.3)#在手动微调的道路上越走越远了orz

		extra_symbol.scale(1.2)#接着微调...这是为小人调整的
		extra_symbol.set_stroke(width=2,color=BLACK)

		#如果小pi本身被scale过了，那这个scale也要相应调整，不然比例就不对了
		self.extra_symbol=extra_symbol
		return extra_symbol
	def get_rid_of_extra_symbol(self):
		#if self.extra_symbol: 
		#otherwise, AttributeError will be raised automatically.
		extra_symbol=self.extra_symbol
		del self.extra_symbol
		return extra_symbol

	#for compatibility.
	def make_eye_contact(self):
		return self.look(OUT)

	#some little magic.
	def get_shader_wrapper_list(self):
		# The story is here:
		# SVGMobject默认会返回两个shader_wrapper, one for fill and one for stroke
		# 结果就是所有子路径的fill和stroke都被一起渲染了，上下层的stroke会相交，无法正确显示重叠关系
		# 因此这里重写这一方法，返回所有sub/son的shader_wrapper，这样每个路径就会分开渲染。
		ret=[]
		for sub in self:
			ret+=sub.get_shader_wrapper_list()
		return ret

	#another little magic.
	def copy(self):
		# 为什么需要重写这个方法？
		# 原因：creature里有引用（诸如self.mouth）
		# 而父一级的copy(Mobject.copy())会 
		#  1.copy submobjects 2.copy根据引用指向的mobject -> 导致这些mobj被copy两次，从而引发问题。
		# 重写之后保证copy一次，并在copy的同时正确redirect引用。

		# 代码由Mobject.copy修改而来。感觉这里面好像有很多问题，我还不知道怎么修改。
		parents = self.parents
		self.parents = []
		copy_mobject = copy.copy(self)
		self.parents = parents

		copy_mobject.data = dict(self.data)
		for key in self.data:
			copy_mobject.data[key] = self.data[key].copy()

		# TODO, are uniforms ever numpy arrays?
		copy_mobject.uniforms = dict(self.uniforms)

		copy_mobject.submobjects = []
		copy_mobject.add(*[sm.copy() for sm in self.submobjects])
		copy_mobject.match_updaters(self)

		copy_mobject.needs_new_bounding_box = self.needs_new_bounding_box

		# Make sure any mobject or numpy array attributes are copied
		for attr, value in list(self.__dict__.items()):
			if isinstance(value, np.ndarray):
				setattr(copy_mobject, attr, value.copy())
			if isinstance(value, ShaderWrapper):
				setattr(copy_mobject, attr, value.copy())

		#redirect references correctly
		copy_mobject._name_parts()
		return copy_mobject