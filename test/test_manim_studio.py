from tkinter.tix import PopupMenu
from manimlib import *

# 为了能从父级目录import需要被测试的对象
import sys
__module_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__module_path__)
from manimhub.my_scene import StarskyScene,ManimStudio
from manimhub.custom_mobjects import Cross


# 测试ManimStudio的功能
class TestCrossAndCheck(ManimStudio):
	def test_select(self):
		self.axes = self.add(Axes())
		self.select(self.axes)
		
	def test_show_bounding_boxes(self):
		#self.axes = self.add(Axes())
		self.c = self.add(Circle())
		self.show_bounding_box(self.c)

	def test_show_points(self):
		self.c = self.add(Circle())
		self.show_points(self.c, show_index=True)

	def test_show_triangulation(self):
		self.c = self.add(Circle(fill_opacity=1)).shift(LEFT*3).scale(3)
		self.cross = self.add(Cross()).shift(RIGHT*3).scale(3)
		self.update_frame() # seems it needs a bit time to refresh triangulation
		self.show_triangulation(self.c)
		# the data of cross object seem to belong to its sublings
		self.show_triangulation(self.cross.submobjects[0])
	
	def construct(self):
		# The following is mutually exclusive
		# That is to say, one at a time.

		#self.test_select()
		#self.test_show_bounding_boxes()
		#self.test_show_points()
		self.test_show_triangulation()

		#self.embed()
