import pretty_errors
from manimlib import *

# 为了能从父级目录import需要被测试的对象
import sys
__module_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__module_path__)
from manimhub.my_scene import StarskyScene
from manimhub.little_creature import LittleCreature

class TestLittleCreature(StarskyScene):
	def pause(self):
		os.system('pause')
	def setup(s):
		super().setup()

		#s.w=s.add(LittleCreature(mood='plain'))
		#s.w=s.add(LittleCreature(mood='plain').shift(UL))
		s.w=s.add(LittleCreature(mood='plain',flipped=True).shift(UL))

		s.save_state()
		
	def reset(self):
		self.restore_state(self.undo_stack[0])
		self.update_frame()
	
	def test_mood(s):
		w=s.w
		while True:
			s.pause()
			s.play(w.change_mood,'smile')
			s.pause()
			s.play(w.change_mood,'surprised')
			s.pause()
			s.play(w.change_mood,'happy')
			s.pause()	
			s.reset()

	def construct(self) -> None:
		w=self.w
		self.embed()

