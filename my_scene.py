from manimlib import *
from manimlib.window import Window
# 由于_AnimationBuilder不在manimlib默认的import范围中
# 因此必须显式导入
from manimlib.mobject.mobject import _AnimationBuilder

import sys
if sys.platform == 'win32':
	import win32gui, win32con
else:
	log.info('OS platform is not windows, some window manipulation based on Win32 API will not work.')

# 注意manimlib在更新boolean_ops之后也有了一个Union，因此import的时候要注意
from typing import Union,Optional,Iterable

# 从package内部import的话要采用这样的语法
# 参考https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
from manimhub.constants import *

class RestartScene(Exception):
	pass

class StarskyScene(Scene):
	def __init__(
		self, 
		window: Optional[Window] = None, 
		window_config: dict = dict(),
		camera_class: type = Camera,
		camera_config: dict = dict(),
		file_writer_config: dict = dict(),
		skip_animations: bool = False,
		always_update_mobjects: bool = False,
		start_at_animation_number: Optional[int] = None,
		end_at_animation_number: Optional[int] = None,
		leave_progress_bars: bool = False,
		preview: bool = True,
		presenter_mode: bool = False,
		show_animation_progress: bool = False,
	):
		self.skip_animations = skip_animations
		self.always_update_mobjects = always_update_mobjects
		self.start_at_animation_number = start_at_animation_number
		self.end_at_animation_number = end_at_animation_number
		self.leave_progress_bars = leave_progress_bars
		self.preview = preview
		self.presenter_mode = presenter_mode
		self.show_animation_progress = show_animation_progress

		self.window_config = {**self.default_window_config, **window_config}
		self.camera_config = {**self.default_camera_config, **camera_config}
		
		self.camera_class = camera_class
		self.file_writer_config = {**self.default_file_writer_config, **file_writer_config}

		if self.preview:
			if window is None: # the first run in a session, create new window
				self.window = Window(scene=self, **self.window_config)
			else:
				self.window = window
				#TODO: fix window's dependence on scene
				window.scene = self

			self.set_window_on_top() # put the window on top by default

			self.camera_config["window"] = self.window

			self.camera_config["ctx"] = self.window.ctx
			self.camera_config["fps"] = 30  # Where's that 30 from?
			# Needed?
			#if 'size' in self.window_config.keys():
			#	self.camera_config["pixel_width"]=self.window_config['size'][0]
			#	self.camera_config["pixel_height"]=self.window_config['size'][1]
			self.undo_stack = []
			self.redo_stack = []
		else:
			self.window = None
		
		# Core state of the scene
		self.camera: Camera = self.camera_class (**self.camera_config)
		self.file_writer = SceneFileWriter(self, **self.file_writer_config)
		self.mobjects: list[Mobject] = [self.camera.frame]
		self.id_to_mobject_map: dict[int, Mobject] = dict()
		self.num_plays: int = 0
		self.time: float = 0
		self.skip_time: float = 0
		self.original_skipping_status: bool = self.skip_animations
		self.checkpoint_states: dict[str, list[tuple[Mobject,Mobject]]] = dict()
		self.undo_stack = []
		self.redo_stack = []
		
		self.frame: CameraFrame = self.camera.frame

		self.render_groups: list[Mobject] = []

		if self.start_at_animation_number is not None:
			self.skip_animations = True
		if self.file_writer.has_progress_display:
			self.show_animation_progress = False

		# Items associated with interaction
		self.mouse_point = Point()
		self.mouse_drag_point = Point()
		self.hold_on_wait = self.presenter_mode
		self.inside_embed = False
		self.quit_interaction = False

		# Much nicer to work with deterministic scenes
		if self.random_seed is not None:
			random.seed(self.random_seed)
			np.random.seed(self.random_seed)

		# always show animation progress
		self.show_animation_progress = True
		
	def set_window_on_top(self, on_top=True):
		if sys.platform != 'win32':
			return self
		if not self.preview:
			log.info("Not in preview mode, no window to be hanbled.")
			return self
		if not hasattr(self.window,'hwnd'):
			all_hwnd = []
			win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd), all_hwnd)
			all_wc_names = [win32gui.GetClassName(hwnd) for hwnd in all_hwnd]
			#wc for window class

			wnd_title = str(self) #see manimlib.window
			hwnd = 0
			for wc_name in all_wc_names:
				hwnd = win32gui.FindWindow(wc_name, wnd_title)
				if hwnd!=0: break
		
			if hwnd==0: 
				log.warning("Can't find hWnd for window. Later window operation is aborted.")
				return self #no window is found, indicating manim is writing to file
			#TODO: is this conclusion reliable?

			self.window.hwnd=hwnd #cache hwnd for potential later usage


		left, top, right, bottom = win32gui.GetWindowRect(self.window.hwnd)

		#use Win32 API to make the mgl window always on top, facilitating further coding.
		win32gui.SetWindowPos(
			self.window.hwnd, 
			win32con.HWND_TOPMOST if on_top else win32con.HWND_NOTOPMOST,
			left, top, right-left, bottom-top, #leave the window pos and size unchanged
			0 #uFlags, which we don't bother here
		)

		return self

	# @Scene.affects_mobject_list
	def add(self, *new_mobjects: Mobject, reorganize=True) -> Union[Mobject,  Iterable[Mobject]]:
		"""
		Mobjects will be displayed, from background to
		foreground in the order with which they are added.
		"""
		if not reorganize: 
			all_sm = self.get_mobject_family_members()
			new_mobjects = list(filter(lambda m: not m in all_sm, new_mobjects))
			if new_mobjects == []: return
			
		self.remove(*new_mobjects)
		self.mobjects += new_mobjects
		self.id_to_mobject_map.update({
			id(sm): sm
			for m in new_mobjects
			for sm in m.get_family()
		})

		# Return the mobjects being added.
		# so handy that I add it here. (starsky)
		if len(new_mobjects)==1: return new_mobjects[0]
		else: return new_mobjects

	# @legacy
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
				state["curr_method"] = arg
			elif isinstance(arg, Animation): 
				anim = arg
				animations.append(anim)
			elif isinstance(arg, _AnimationBuilder):
				anim = arg.build()
				animations.append(anim)
			# animation arguments
			elif state["curr_method"]:
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

		for animation in animations:
			animation.update_config(**kwargs)

		return animations

	'''
	@handle_play_like_call
	def play(self, *play_args, **animation_config):
		if len(play_args) == 0:
			log.warning("Called Scene.play with no animations")
			return
		animations = self._compile_animations(*play_args, **animation_config)
		#print(animations)
		self.begin_animations(animations, reorganize_mobjects = animation_config.get('reorganize_mobjects',True))
		self.progress_through_animations(animations)
		self.finish_animations(animations)
	'''

	def begin_animations(self, animations: Iterable[Animation], reorganize = True) -> None:
		for animation in animations:
			animation.begin()
			# Anything animated that's not already in the
			# scene gets added to the scene.  Note, for
			# animated mobjects that are in the family of
			# those on screen, this can result in a restructuring
			# of the scene.mobjects list, which is usually desired.
			self.add(animation.mobject, reorganize = reorganize)

	#一些小小的魔改
	def wait(self, duration_or_speech: Union[float, str]=1):
		self.pre_play()
		if isinstance(duration_or_speech, float) or isinstance(duration_or_speech, int):
			duration=duration_or_speech
		else: 
			duration=len(duration_or_speech)/CH_PER_SEC

		stop_condition=None
		time_progression = self.get_wait_time_progression(duration, stop_condition)
		last_t = 0
		for t in time_progression:
			dt = t - last_t
			last_t = t
			self.update_frame(dt)
			self.emit_frame()

		self.post_play()
		return self

	def narrate(self, words:str):
		self.wait(words)

	def _should_restart(self):
		if hasattr(self,'_src_file_updated') and self._src_file_updated:
			return True
		return False

	def update_frame(self, dt: float = 0, ignore_skipping: bool = False) -> None:
		if self._should_restart(): 
			raise RestartScene()
			
		return super().update_frame(dt, ignore_skipping)

	def run(self) -> int:
		self.virtual_animation_start_time: float = 0
		self.real_animation_start_time: float = time.time()
		self.file_writer.begin()

		self.setup()
		try:
			self.construct()
			self.interact()
		except EndScene:
			return END_SCENE
		except RestartScene:
			return RESTART_SCENE
		except KeyboardInterrupt:
			# Get rid keyboard interupt symbols
			print("", end="\r")
			self.file_writer.ended_with_interrupt = True
		self.tear_down()

# for test and prototyping
class EmptyEmbeddedScene(StarskyScene):
	def construct(self) -> None:
		self.embed()

class SelectionBox(SurroundingRectangle):
	def surround(self, mobject, **kwargs):
		buff=MED_SMALL_BUFF
		self.move_to(mobject)
		for dim in [0,1]:
			length = mobject.length_over_dim(dim)
			self.rescale_to_fit(length+buff,dim,stretch=True)
		return self

# current issue: can't effectively align characters
# as there're up and down antenne of different chars(e.g. h g)
# NOTE: this is intended to be used as mobj labels in ManimStudio
#       below - at least currently.
ascii_cache=[] # empty stuff at beginning
class AsciiText(VGroup):
	'''By restricting content to ASCII characters, we can cache the chars
	and allow for a quick and dirty usage.'''
	def __init__(self, text):
		super().__init__()
		for c in text:
			if not ord(c)<128: raise ValueError("Only ASCII characters are allowed!")
		global ascii_cache
		if len(ascii_cache)==0: #generate cache
			ascii_cache = [
				(Text(chr(c), font_size=25) if  32<=c<=127 else None) # 有一些控制字符无法渲染
				for c in range(128)
			]
		for c in text:
			self.add(ascii_cache[ord(c)].copy())
			self.submobjects

		self.arrange(RIGHT, buff=0.03)
		

# ManimStudio is an interactive scene that helps dev and debugging.
# Currently supported functionality:
#  - select (via ↑↓←→ keys)
#  - show boundingbox
#  - show points [VMobject only]
#  - show triangulation (preview ver.) [VMobject only]
#  - show info label during operation above
# Note: 
#  - Except select, the latter operations don't support keypress interaction, 
#      and are supposed to be accessed in embed()
#  - ManimStudio override update_frame() for its own reason, so it doesn't 
#      support manim_shell usage currently.
class ManimStudio(Scene):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		# meta objects 是用来编辑操作的，例如对对象的标签、选择框等等
		self.meta_objects=[]

		self.info_labels=[]#info label plays a role of reference list
		self.bboxes=[] #bounding boxes vis
		self.points=[] #points vis
		self.triangulations=[] #traingulation vis

		self.sel_mobject=None
		self.sel_box=SelectionBox(Dot())
		self.select(None)
		self.meta_objects.append(self.sel_box)

		log.info("ManimStudio alpha ver. Keys for selection have been registered, \
			press ↑↓←→ to select between the hierachy of mobjects.")

	# Select related

	def select(self, mobj: Optional[Mobject], fade_when_desel=True, show_info_label=True):
		if mobj:
			assert(isinstance(mobj, Mobject))
		try: 
			assert(mobj==None or mobj in self.get_mobject_family_members())
		except AssertionError:
			raise ValueError('You must select a mobject in the scene!')
		self.sel_mobject=mobj
		if mobj is not None:
			self.sel_box.surround(mobj)
			self.sel_box.clear_updaters()
			self.sel_box.add_updater(lambda m: m.surround(mobj,stretch=True))
			self.sel_box.set_style(stroke_opacity=1)

			self.clear_info_labels()
			self.show_info(mobj)
		else:
			self.sel_box.surround(Dot(),stretch=True)
			self.clear_info_labels()
			if fade_when_desel: self.sel_box.set_style(stroke_opacity=0)
		return self
	
	def _get_proper_parent_in_scene(self,mobj: Mobject) -> Union[Scene,Mobject]:
		if mobj is None: raise ValueError()

		if mobj in self.mobjects: return self
		parents=mobj.parents
		parents=[M for M in parents if M in self.get_mobject_family_members()]
		return parents[0]

	def select_up(self):
		if self.mobjects is None: return self
		if self.sel_mobject is None: 
			self.select(self.mobjects[0])
			return self

		parent=self._get_proper_parent_in_scene(self.sel_mobject)
		if parent is self: return self#到顶了
		self.select(parent)
		return self
	def select_down(self):
		if self.sel_mobject is None: 
			return self
		if len(self.sel_mobject.submobjects)==0:
			return self
		for sub in self.sel_mobject:
			if sub in self.get_mobject_family_members():
				self.select(sub);break
		return self
	def select_previous(self):
		if self.sel_mobject is None:
			return self

		parent=self._get_proper_parent_in_scene(self.sel_mobject)
		if parent is self: 
			idx=self.mobjects.index(self.sel_mobject)
			if idx!=0:
				self.select(self.mobjects[idx-1])
		else:
			idx=parent.submobjects.index(self.sel_mobject)
			if idx!=0:
				self.select(parent.submobjects[idx-1])
		return self
	def select_next(self):
		if self.sel_mobject is None:
			return self

		parent=self._get_proper_parent_in_scene(self.sel_mobject)
		if parent is self: 
			idx=self.mobjects.index(self.sel_mobject)
			if idx<len(self.mobjects)-1:
				self.select(self.mobjects[idx+1])
		else:
			idx=parent.submobjects.index(self.sel_mobject)
			if idx<len(parent.submobjects)-1:
				self.select(parent.submobjects[idx+1])
		return self

	def on_key_press(self, symbol: int, modifiers: int) -> None:
		#super().on_key_press(symbol, modifiers)
		#print(symbol, modifiers)
		char = chr(symbol)
		if char == 'q':
			self.quit_interaction = True
		if symbol == ARROW_SYMBOLS[0]: 
			self.select_previous()
		if symbol == ARROW_SYMBOLS[1]: 
			self.select_up()
		if symbol == ARROW_SYMBOLS[2]: 
			self.select_next()
		if symbol == ARROW_SYMBOLS[3]: 
			self.select_down()

	def show_info(self, mobj: Mobject):
		if hasattr(mobj,'_info_label_cache'):
			info_label=mobj._info_label_cache
		else:
			#sth like 'manimlib.mobject.number_line.NumberLine'
			description=str(type(mobj))
		
			description=re.match(r".*'(.*)'.*",description).group(1)
			#simplify the description a bit
			description= description\
				.replace('manimlib.mobject.','')\
				.replace('object.','')

			same_type_mobjs=[m for m in self.get_mobject_family_members() if type(m)==type(mobj)]
			description+=' #'+str(same_type_mobjs.index(mobj))	

			info_label=AsciiText(description)
			info_label.next_to(mobj,UP,SMALL_BUFF)
			info_label.align_to(mobj,LEFT)
			info_label.shift_onto_screen()
			def pos_constraint(m: Mobject):
				m.next_to(mobj,UP,SMALL_BUFF)
				m.align_to(mobj,LEFT)
				m.shift_onto_screen()

			info_label.add_updater(pos_constraint)

		self.meta_objects.append(info_label)
		self.info_labels.append(info_label)
		mobj._info_label_cache=info_label
	def clear_info_labels(self):
		for label in self.info_labels:
			self.meta_objects.remove(label)
			del label
		self.info_labels=[]

	def show_bounding_box(self, mobj: Mobject):
		bbox_arr=mobj.data['bounding_box']
		corners_dl=bbox_arr[0]
		corners_ur=bbox_arr[2]
		center=bbox_arr[1]
		X_MASK=np.array([1.,0.,0.])
		Y_MASK=np.array([0.,1.,0.])
		corners_dr=corners_dl*Y_MASK+corners_ur*X_MASK
		corners_ul=corners_dl*X_MASK+corners_ur*Y_MASK

		bbox_vis=Polygon(corners_dl,corners_dr,corners_ur,corners_ul,color='#777777')
		bbox_vis.add(Dot(center,color='#AAAAAA'))

		self.bboxes.append(bbox_vis)
		self.meta_objects.append(bbox_vis)

	show_bbox=show_bounding_box # function alias

	def clear_boundingx_boxes(self):
		for bbox in self.bboxes:
			self.meta_objects.remove(bbox)
			del bbox
		self.bboxes=[]

	clear_bboxes=clear_boundingx_boxes

	# Show points (bazier anchor and handles actually) of VMobject

	def show_points(self, mobj: VMobject, show_index=False, **dot_kwargs):
		assert(isinstance(mobj,VMobject))
		
		dot_kwargs.setdefault('radius', 0.03)
		dot_kwargs.setdefault('color' , WHITE)

		points_vis=VGroup(*[Dot(d,**dot_kwargs) for d in mobj.data['points']])

		if show_index:
			for i,d in enumerate(mobj.data['points']):
				label=Integer(i,color=RED).set_height(0.2)\
					.next_to(points_vis[i],UP,buff=0.02)
				if i%3==0:
					label.next_to(points_vis[i],RIGHT,buff=0.02)
				points_vis[i].add(label)
		self.points.append(points_vis)
		self.meta_objects.append(points_vis)

		log.info(f"{len(mobj.data['points'])} points showed in total.")

	def clear_points(self):
		for g in self.points:
			self.meta_objects.remove(g)
			del g
		self.points=[]

	# Show triangulation for VMobject (still in experiment, not done)
	def show_triangulation(self, mobj: VMobject):
		log.warning("show_triangulation(..) is still in dev and may have unexpected results. Be aware.")
		assert(isinstance(mobj,	VMobject))

		tri_vis=VGroup()
		points=mobj.data['points']
		tri=mobj.triangulation
		ntri=len(mobj.triangulation)//3
		MyTriangle=Polygon
		for t in range(ntri):
			tri_vis.add(MyTriangle(
				points[tri[3*t]],
				points[tri[3*t+1]],
				points[tri[3*t+2]],
				stroke_width=2
			))
		self.triangulations.append(tri_vis)
		self.meta_objects.append(tri_vis)

	def clear_triangulations(self):
		for tri in self.triangulations:
			self.meta_objects.remove(tri)
			del tri
		self.triangulations=[]

	# Override update_frame so that meta_objects can be rendered.
	# remenber that meta_objects are mobjects that shows the info
	# of mobjects, hence they belong to "studio", not the "scene".
	#
	# Not checking _should_update here, so it doesn't support 
	# hot reload yet.
	def update_frame(self, dt=0, ignore_skipping=False):
		self.increment_time(dt)
		self.update_mobjects(dt)
		if self.skip_animations and not ignore_skipping:
			return

		if self.window:
			self.window.clear()
		self.camera.clear()
		self.camera.capture(*self.mobjects, *self.meta_objects)

		if self.window:
			self.window.swap_buffers()
			vt = self.time - self.virtual_animation_start_time
			rt = time.time() - self.real_animation_start_time
			if rt < vt:
				self.update_frame(0)

	# Override update_mobjects(...) to update meta_objects properly
	def update_mobjects(self, dt):
		for mobject in self.mobjects:
			mobject.update(dt)
		for object in self.meta_objects:
			object.update(dt)

	