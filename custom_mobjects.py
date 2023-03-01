from manimlib import *

from manimhub.constants import *

class Check(SVGMobject):
	def __init__(self, **kwargs):
		super().__init__('assets/check.svg', **kwargs)
		self.set_stroke(width=0)

class Cross(SVGMobject):
	def __init__(self, **kwargs):
		super().__init__('assets/cross.svg', **kwargs)
		self.set_stroke(width=0)

# 用于遮挡后面mobj的幕布
# 用的时候请注意mobj图层顺序——Curtain类本身不保证遮挡关系。
class Curtain(Rectangle):
	def __init__(self, 
	    left = -FRAME_WIDTH /2,
		right= +FRAME_WIDTH /2,
		up   = +FRAME_HEIGHT/2,
		down = -FRAME_HEIGHT/2,
		scale_factor = 1.0,
		**kwargs
	):
		self.left = left *scale_factor
		self.right= right*scale_factor
		self.up   = up   *scale_factor
		self.down = down *scale_factor

		super().__init__(
			self.right-self.left, self.up-self.down,
			fill_opacity = 1,
			fill_color = BG_COLOR,
			stroke_width = 0,
			stroke_opacity = 0,
			**kwargs
		)
		self._put_into_place()

	def _put_into_place(self):
		self.next_to(RIGHT*self.left, RIGHT, buff=0, coor_mask = np.array([1,0,0]))
		self.next_to(  UP *self.down,   UP , buff=0, coor_mask = np.array([0,1,0]))

	def set_left(self, left):
		if isinstance(left, np.ndarray): left=left[0]
		self.left=left
		self.rescale_to_fit(self.right-self.left, dim=0, stretch=True)
		self._put_into_place()
		return self
	def set_right(self, right):
		if isinstance(right, np.ndarray): right=right[0]
		self.right=right
		self.rescale_to_fit(self.right-self.left, dim=0, stretch=True)
		self._put_into_place()
		return self
	def set_up(self, up):
		if isinstance(up, np.ndarray): up=up[1]
		self.up=up
		self.rescale_to_fit(self.up-self.down, dim=1, stretch=True)
		self._put_into_place()
		return self
	def set_down(self, down):
		if isinstance(down, np.ndarray): down=down[1]
		self.down=down
		self.rescale_to_fit(self.up-self.down, dim=1, stretch=True)
		self._put_into_place()
		return self