from manimlib import *
from typing import Callable

# 为了能从父级目录import需要被测试的对象
import sys
__module_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__module_path__)
from manimhub.my_scene import StarskyScene

sys.path.append(os.getcwd())
from data_axes import *

class TestDataAxis(StarskyScene):
	def pause(self):
		os.system('pause')
	def reset_scene(self):
		self.restore_state(self.undo_stack[0]);self.update_frame()
	def test_static(self) -> None:
		axis1 = DataAxis()
		axis2 = DataAxis(range = [-8,8,1], length=2)
		axis3 = DataAxis(unit_size = 0.5, tick_length=0.05, include_tip = True)
		# TODO:test numbers
		axis1.shift(UP*2)
		axis3.shift(DOWN*2)

		self.add(axis1, axis2, axis3)
	def test_direction(self) -> None:
		axis1 = DataAxis(direction = VERTICAL, length=FRAME_HEIGHT-2)
		axis2 = DataAxis(
			direction = VERTICAL, 
			include_numbers=True, include_tip=True, 
			length=4
		)
		axis2.shift(RIGHT)
		self.add(axis1, axis2)
	def test_direction2(self) -> None:
		axis_h = DataAxis(include_tip = True, include_numbers=True)
		axis_v = DataAxis(include_tip = True, direction=VERTICAL, length=FRAME_HEIGHT-2, include_numbers=True)

		self.add(axis_h)
		self.wait(0.5)
		self.play(Transform(axis_h, axis_v))

	def test_animate(self) -> None:
		axis = DataAxis(
			range = [-4,4,1],
			width = 2,
			include_ticks = True,
			include_tip = True,
			include_numbers = True
		)
		circ = Circle(radius = axis.unit_size)
		circ.add_updater(lambda m: m.move_to(axis.n2p(0)).set_width(axis.unit_size*2))
		self.add(axis, circ)
		self.wait(0.5)
		self.play(ApplyMethod(axis.scale, 5, run_time=2, rate_func=smooth, recursive=True))
		self.play(axis.animate.shift(UP*2), recursive=True)
		self.play(axis.animate.shift(DOWN*4), recursive=True)
		self.play(axis.animate.shift(UP*2))
		self.add()

	def test_dynamic_range(self) -> None:
		axis = DataAxis(
			range = [-4,4,1],
			length = 2,
			include_ticks = True,
			include_tip = True,
			include_numbers = True
		)
		circ = Circle(radius = axis.unit_size)
		circ.add_updater(lambda m: m.move_to(axis.n2p(0)).set_width(axis.unit_size*2))
		self.add(axis, circ)
		self.wait(0.5)
		self.play(ApplyMethod(axis.scale, 5, run_time=2, rate_func=smooth, recursive=True))

		self.play(axis.animate.set_range(-3,5), recursive=True)
		self.play(axis.animate.set_range(-5,3), recursive=True)
		self.play(axis.animate.set_range(-1,1), recursive=True)

		self.play(axis.animate.shift(DL), recursive=True)
		self.play(axis.animate.shift(UR), recursive=True)
	
	def test_copy(self):
		axis = DataAxis(
			include_ticks = True,
			include_tip = True,
			include_numbers = True
		)
		self.add(axis)
		axis2 = axis.copy().shift(DOWN)
		self.play(TransformFromCopy(axis, axis2))

		# make sure that axis and its copy are not 'entangled'.
		self.play(
			ApplyMethod(axis2.scale, 1.2, 
			run_time=2, rate_func=smooth, recursive=True)
		)
		self.play(axis2.animate.set_range(-3,5), recursive=True)
	
	def construct(self) -> None:
		#self.test_static()
		#self.test_direction()
		#self.test_direction2()
		#self.test_animate()
		self.test_dynamic_range()
		#self.test_copy()
		

class TestDataAxes(StarskyScene):
	def pause(self):
		os.system('pause')
	def reset_scene(self):
		self.restore_state(self.undo_stack[0]);self.update_frame()
	def test_axis1(self) -> None:
		axis = self.add(DataAxis(include_numbers=True, formatter = lambda x: x+1912))
		axis: DataAxis
		self.axis = axis

	def test_axis_animate(self):
		axis = self.axis
		self.play(ApplyMethod(axis.set_range, 0,8, recursive=False))
		self.play(ApplyMethod(axis.set_range, 90,98, recursive=False))

	def test_axis2(self) -> None:
		decimal_number_config = {
			"num_decimal_places": 2,
			"font_size": 36
		}
		axis = self.add(DataAxis(include_numbers=True, decimal_number_config = decimal_number_config))
		axis: DataAxis
		self.play(axis.set_range, 5,10.5)
		self.play(axis.set_range, 9.5,10.5, run_time=3)


	def test_axes(self) -> None:
		axes = DataAxes(axis_align_towards_zero=True, x_range=[-4,4])
		self.add(axes)
		#axes.add_axis_labels()
		self.play(axes.animate.set_range('x',[-2,6]), recursive=True)
		self.play(axes.animate.set_all_ranges([-8,0],[-8,-2]), recursive=True)
		self.play(axes.animate.set_all_ranges([-4,4],[-3,3]), recursive=True)
		#TODO: 更完善的测试用例

		#self.play(axes.shift, RIGHT, recursive=True)
	def test_axes_2(self):
		xmax = 3; wh_ratio = 3/3; width=6
		axis_config = {
			'x_range': [-xmax,xmax], 
			'include_tip': True
		}
		axis = DataAxis(**axis_config)#.to_edge(LEFT, buff=1)
		axis_copy = axis.copy().shift(DOWN)

		dot = Dot().add_updater(lambda m: m.move_to(axis_copy.n2p(0)))
		self.add(axis, axis_copy, dot)
		self.wait(0.5)
		self.play(axis.animate.shift(RIGHT))

	def test_plot(self) -> None:
		axes = self.add(DataAxes())
		axes: DataAxes
		#axes.add_axis_labels()
		axes.plot(lambda x: x**2, [-1,1])
		axes.scatter([0,1,2],[0,1,3])

		self.play(axes.x_axis.set_range,-2,2,recursive=True)
		self.play(axes.x_axis.set_range,0,4,recursive=True)
		self.play(axes.x_axis.set_range,3,8,recursive=True)

		self.play(axes.x_axis.set_range,0,4,
				axes.y_axis.set_range,-2,4, recursive=True)


	def construct(self) -> None:
		self.test_test1()
		#self.test_axis2()
		#self.test_axes()
		#self.test_axes_2()
		#self.test_plot()


		#self.embed()