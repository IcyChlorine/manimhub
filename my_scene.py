from manimlib import *
# 由于_AnimationBuilder不在manimlib默认的import范围中
# 因此必须explicitly import一下
from manimlib.mobject.mobject import _AnimationBuilder

# 注意manimlib在更新boolean_ops之后也有了一个Union，因此import的时候要注意
from typing import Union,List

# 从package内部import的话要采用这样的语法
# 参考https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
from manimhub.constants import *

class StarskyScene(InteractiveScene):
	def add(self, *new_mobjects: Mobject) -> Union[Mobject, List[Mobject]]: 
		# override the add of base class a bit
		# so it returns mobjects being added,
		# which is very handy for syntax like this: m=self.add(Circle())
		super().add(*new_mobjects)
		if len(new_mobjects)==1:
			return new_mobjects[0]
		else:
			return new_mobjects

	def wait(self, time_or_speech: Union[float, str]=1):
		if isinstance(time_or_speech, float) or isinstance(time_or_speech, int):
			time=time_or_speech
		else: 
			time=len(time_or_speech)/CH_PER_SEC
		return super().wait(time)

	def narrate(self, words:str):
		self.wait(words)

	def _compile_animations(self, *args, **kwargs):
		"""
		Each arg can either be an animation, or a mobject method
		followed by that methods arguments (and potentially follow
		by a dict of kwargs for that method).
		This animation list is built by going through the args list,
		and each animation is simply added, but when a mobject method
		s hit, a MoveToTarget animation is built using the args that
		follow up until either another animation is hit, another method
		is hit, or the args list runs out.
		"""
		animations = []
		state = {
			"curr_method": None,
			"last_method": None,
			"method_args": [],
		}

		def compile_method(state):
			print('in compile_method')
			if state["curr_method"] is None:
				return
			mobject = state["curr_method"].__self__
			# if multiple methods is intended for the same mobject
			if state["last_method"] and state["last_method"].__self__ is mobject:
				animations.pop()
				# method should already have target then.
			else:
				mobject.generate_target()
			# handle kwargs for the method, which is passed in in the form of a dictionary.
			if len(state["method_args"]) > 0 and isinstance(state["method_args"][-1], dict):
				method_kwargs = state["method_args"].pop()
			else:
				method_kwargs = {}
			
			# generate animation target by applying method
			state["curr_method"].__func__(
				mobject.target,
				*state["method_args"],
				**method_kwargs
			)
			return MoveToTarget(mobject)
			#animations.append(MoveToTarget(mobject))
			#state["last_method"] = state["curr_method"]
			#state["curr_method"] = None
			#state["method_args"] = []

		for i,arg in enumerate(args):
			# terminate and compile the previous animation, if there's any.
			if state['curr_method'] and \
				(inspect.ismethod(arg) or isinstance(arg, Animation) or isinstance(arg, _AnimationBuilder)):
				anim=compile_method(state)
				animations.append(anim)
				state['last_method'] = state['curr_method']
				state['curr_method'] = None
				state['method_args'] = []
			# invoke new animations.
			# There're three type of cases: 
			# e.g. (m.shift, UP), m.animate.shift(UP), ApplyMethod(m.shift,UP)
			if inspect.ismethod(arg):
				print('new `curr_method`.')
				state["curr_method"] = arg
			elif isinstance(arg, Animation): 
				anim = arg
				animations.append(anim)
			elif isinstance(arg, _AnimationBuilder):
				anim = arg.build()
				animations.append(anim)
			# animation arguments
			elif state["curr_method"]:
				print('appending new arg.')
				state["method_args"].append(arg)
			# error proning
			elif isinstance(arg, Mobject):
				raise Exception("""
					I think you may have invoked a method
					you meant to pass in as a Scene.play argument
				""")
			else:
				raise ValueError("Unknown args passed to StarskyScene.play. WTF?")
		# settle the trailing animation, if there're any.
		if state['curr_method']:
			anim = compile_method(state)
			animations.append(anim)

		return animations

	# 由于装饰器好像不能从父类继承，
	# 因此这里要再定义一下。
	def handle_play_like_call(func):
		@wraps(func)
		def wrapper(self, *args, **kwargs):
			if self.inside_embed:
				self.save_state()
			if self.presenter_mode and self.num_plays == 0:
				self.hold_loop()

			self.update_skipping_status()
			should_write = not self.skip_animations
			if should_write:
				self.file_writer.begin_animation()

			if self.window:
				self.real_animation_start_time = time.time()
				self.virtual_animation_start_time = self.time

			self.refresh_static_mobjects()
			func(self, *args, **kwargs)

			if should_write:
				self.file_writer.end_animation()

			if self.skip_animations and self.window is not None:
				# Show some quick frames along the way
				self.update_frame(dt=0, ignore_skipping=True)

			self.num_plays += 1
		return wrapper

	#def play(self, *args, **kwargs):
	@handle_play_like_call
	def play(self, *play_args, **animation_config):
		if len(play_args) == 0:
			log.warning("Called Scene.play with no animations")
			return
		animations = self._compile_animations(*play_args, **animation_config)
		print(animations)
		self.begin_animations(animations)
		self.progress_through_animations(animations)
		self.finish_animations(animations)