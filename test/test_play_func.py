from manimlib import *

# 为了能从父级目录import需要被测试的对象
import sys
__module_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__module_path__)
from manimhub.my_scene import StarskyScene


# 测试Scene的play函数
class TestPlayFunc(StarskyScene):
	def reset_scene(self):
		os.system('pause')
		self.restore_state(self.undo_stack[0]);self.update_frame()
		os.system('pause')

	def construct(self) -> None:
		c1=Circle(color=RED).shift(LEFT*3)
		c2=Circle(color=WHITE)
		c3=Circle(color=BLUE).shift(RIGHT*3)
		r2=Square(color=WHITE).move_to(c2)
		self.add(c1,c2,c3)
		self.save_state()

		# test single
		self.play(c1.shift,UP)
		self.reset_scene()
		self.play(c1.animate.shift(UP))
		self.reset_scene()
		self.play(ApplyMethod(c1.shift,UP))
		self.reset_scene()

		# test simutaneous animations of different types
		self.play(ApplyMethod(c1.shift,UP),c2.animate.shift(UP),c3.shift,UP)
		self.reset_scene()
		self.play(c1.shift,UP,c2.animate.shift(UP),ApplyMethod(c3.shift,UP))
		self.reset_scene()

		self.play(c1.set_color,TEAL, Transform(c2,r2))