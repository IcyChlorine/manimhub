from tkinter.tix import PopupMenu
from manimlib import *

# 为了能从父级目录import需要被测试的对象
import sys
__module_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__module_path__)
from manimhub.my_scene import StarskyScene
from manimhub.custom_mobjects import Check,Cross
from manimhub.custom_animation import Popup


# 测试Scene的play函数
class TestCrossAndCheck(StarskyScene):
	def pause(self):
		os.system('pause')

	def reset_scene(self):
		self.restore_state(self.undo_stack[0]);self.update_frame()

	def setup(self):
		ret = super().setup()
		self.save_state()

		self.update_frame()
		self.check, self.cross = Check(), Cross()
		self.check.shift( LEFT*2)
		self.cross.shift(RIGHT*2)
		
		return ret
	def construct(self) -> None:
		while True:
			self.pause()
			self.play(Popup(self.check))
			self.pause()
			self.play(Popup(self.cross))
			self.pause()
			self.reset_scene()