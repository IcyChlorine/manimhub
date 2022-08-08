from manimlib import *

# 为了能从父级目录import需要被测试的对象
import sys
__module_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__module_path__)
from manimhub.my_scene import StarskyScene
from manimhub.custom_animation import *

class TestPopup(StarskyScene):
	def pause(self):
		os.system('pause')
	def reset_scene(self):
		self.restore_state(self.undo_stack[0]);self.update_frame()
	def construct(self) -> None:
		self.save_state()
		c=Circle()
		while True:
			self.play(Popup(c))
			self.pause()
			self.reset_scene()
			self.pause()

