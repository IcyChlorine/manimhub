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

# Debug 用
class PointsTracker(VGroup):
	def __init__(self, mobj: VMobject):
		super().__init__()
		# VMobject to track
		self.mobj=mobj
		def updater(m: PointsTracker):
			m.clear()
			for sub in m.mobj.get_family():
				for P in sub.data['points']:
					m.add(Dot(P,radius=0.02,color=YELLOW))
			return m
		self.add_updater(updater)

# 由于PointsTracker可视化很慢，因此建议渲染至文件再观察
class TestCleanTransform(StarskyScene):
	def pause(self):
		os.system('pause')
	def construct(self) -> None:
		tex1 = self.add(Tex( '\\pi').scale(12))
		tex2 =          Tex('i\\pi').scale(12)
		tex1.match_style(Circle())
		tex2.match_style(Circle())

		points = self.add(PointsTracker(tex1))
		points_num=Integer(len(points))
		points_num.add_updater(lambda m: m.set_value(len(points)))
		self.add(points_num.align_on_border(UL))

		T = CleanTransform
		self.wait()
		self.play(T(tex1,tex2,run_time=5))
		self.wait()

# Just a coarse test now
# only one case, which is complicated though, is tested.
# Other cases and edge cases are not tested yet.
# TODO: A more thorough test
class TestTransformByIndexMap(StarskyScene):
	def setup(self):
		super().setup()
		fml1=MTex(r'e^{  r }=\lim_{n\to\infty}\left(1+\frac{  r }{n}\right)=-1',isolate=['r',       'e','n'])
		fml2=MTex(r'e^{i\pi}=\lim_{n\to\infty}\left(1+\frac{i\pi}{n}\right)=-1',isolate=['i','\\pi','e','n'])
		fml1.set_color_by_tex_to_color_map({'r':RED,               'e':BLUE, 'n':YELLOW})
		fml2.set_color_by_tex_to_color_map({'i':PURPLE,'\\pi':RED, 'e':BLUE, 'n':YELLOW})
		self.add(fml1)

		self.fml1,self.fml2=fml1,fml2
		self.save_state()
		self.update_frame()
		
	def pause(self):
		os.system('pause')
	def reset_scene(self):
		self.restore_state(self.undo_stack[0]);self.update_frame()
	def construct(self) -> None:
		#self.test_points_num()
		#return

		#self.find_index(self.fml2)				
		#return

		fml1,fml2=self.fml1,self.fml2
		while True:
			self.pause()

			# coarse transform
			#self.play(T(fml1,fml2,run_time=3))

			#对拍用
			'''T=Transform
			G=VGroup
			self.play(
				T(fml1[0],fml2[0]),
				T(fml1[1:2],fml2[1:3]),
				T(fml1[2:12],fml2[3:13]),
				T(fml1[12:13],fml2[13:15]),
				T(fml1[13:],fml2[15:]),
				run_time=3
			)
			'''

			T=TransformByIndexMap
			self.play(T(
				fml1,fml2,
				[1,12],
				[(1,2),(13,14)],
			))

			self.pause()
			self.reset_scene()
		self.embed()
	def find_index(self,m):
		self.clear()
		self.add(m)
		self.add(index_labels(m))
		self.update_frame()
		self.pause()

	def test_points_num(self) -> None:
		# suppose fml1 ==> e^r =lim_{n→∞}(1+ r/n)^n=-1
		#         fml2 ==> e^iπ=lim_{n→∞}(1+iπ/n)^n=-1
		# see below for experiment results.
		fml1,fml2=self.fml1,self.fml2

		num_points=0
		for m in self.mobjects:
			for sub in m.get_family():
				num_points+=len(sub.get_points())
		print('before transform, #points = '+str(num_points))
		# before transform: #points = 2528

		T=CleanTransform
		self.play(T(fml1,fml2,run_time=1))

		num_points=0
		for m in self.mobjects:
			for sub in m.get_family():
				num_points+=len(sub.get_points())
		print('after transform, #points = '+str(num_points))
		# after transform: #points = 
		# 3083 for Transform
		# 2885 for CleanTransform
