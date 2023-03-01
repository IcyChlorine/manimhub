import pretty_errors
from manimlib import *

# 为了能从父级目录import需要被测试的对象
import sys

__module_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__module_path__)
from manimhub.my_scene import StarskyScene
from manimhub.little_creature import LittleCreature
from manimhub.little_creature import Blink

class TestLittleCreature(StarskyScene):
	def pause(self):
		os.system('pause')
	def setup(s):
		super().setup()

		#s.w=s.add(LittleCreature(mood='plain'))
		s.w=s.add(LittleCreature(mood='plain').shift(UL))
		s.w=s.add(LittleCreature(mood='plain',flipped=True).shift(UR))
		
		s.update_frame()
		s.save_state()

	def reset(self):
		self.restore_state(self.undo_stack[0])
		self.update_frame()
	
	def test_mood(s):
		w=s.w
		while True:
			s.pause()
			s.play(w.animate.change_mood('smile'))
			s.pause()
			s.play(w.animate.change_mood('surprised'))
			s.pause()
			s.play(w.animate.change_mood('happy'))
			s.pause()	
			s.reset()
	def test_eye_contact(s):
		w=s.w
		while True:
			s.pause()
			s.play(w.animate.look(RIGHT))
			s.pause()
			s.play(w.animate.look(UL*10))
			s.pause()
			s.play(w.animate.look_at(ORIGIN))
			s.pause()
			s.play(w.animate.make_eye_contact())

	def test_comprehensive(s):
		w=s.w
		while True:
			s.pause()
			s.play(w.look,RIGHT)
			s.pause()
			s.play(w.animate.change_mood('smile'))
			s.pause()
			s.play(w.animate.shift(RIGHT*3))
			s.pause()
			s.play(w.animate.make_eye_contact())
			s.pause()
			s.play(w.animate.change_mood('surprised'))
			s.pause()
			s.reset()
			
	def test_blink(s):
		w=s.w
		while True:
			s.pause()
			s.play(Blink(w))

	def construct(self) -> None:
		w=self.w

		self.test_mood()
		#self.test_eye_contact()
		#self.test_comprehensive()
		#self.test_blink()

		self.embed()