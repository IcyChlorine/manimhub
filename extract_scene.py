import copy
import inspect
import os,sys
import importlib

from manimlib.config import get_custom_config
from manimlib.logger import log
from manimlib.scene.interactive_scene import InteractiveScene
from manimlib.scene.scene import Scene
from manimlib.mobject.geometry import Circle, Rectangle

class BlankScene(InteractiveScene):
	def construct(self):
		exec(get_custom_config()["universal_import_line"])
		self.embed()

class DefaultPlayground(Scene):
	def construct(self):
		r,c=self.add(Rectangle(),Circle())
		exec(get_custom_config()["universal_import_line"])  
		print('Available locals: r-Rectangle, c-Circle.')
		self.embed()

def is_child_scene(obj, module):
	if not inspect.isclass(obj):
		return False
	if not issubclass(obj, Scene):
		return False
	if obj == Scene:
		return False
	if not obj.__module__.startswith(module.__name__):
		return False
	return True

def get_scene_config(config):
	return dict([
		(key, config[key])
		for key in [
			"window_config",
			"camera_config",
			"file_writer_config",
			"skip_animations",
			"start_at_animation_number",
			"end_at_animation_number",
			"leave_progress_bars",
			"show_animation_progress",
			"preview",
			"presenter_mode",
		]
	])

def compute_total_frames(scene_class, scene_config):
	"""
	When a scene is being written to file, a copy of the scene is run with
	skip_animations set to true so as to count how many frames it will require.
	This allows for a total progress bar on rendering, and also allows runtime
	errors to be exposed preemptively for long running scenes. The final frame
	is saved by default, so that one can more quickly check that the last frame
	looks as expected.
	"""
	pre_config = copy.deepcopy(scene_config)
	pre_config["file_writer_config"]["write_to_movie"] = False
	pre_config["file_writer_config"]["save_last_frame"] = True
	pre_config["file_writer_config"]["quiet"] = True
	pre_config["skip_animations"] = True
	pre_scene = scene_class(**pre_config)
	pre_scene.run()
	total_time = pre_scene.time - pre_scene.skip_time
	return int(total_time * scene_config["camera_config"]["fps"])

def get_module(filename):
	"Get module from the given filename by import"
	if filename is None:
		return None

	module_name = filename.replace(os.sep, ".").replace(".py", "")
	spec = importlib.util.spec_from_file_location(module_name, filename)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module

def get_scenes_to_render(scene_classes, scene_config, config):
	if config["write_all"]:
		return [sc(**scene_config) for sc in scene_classes]

	result = []
	for scene_name in config["scene_names"]:
		found = False
		for scene_class in scene_classes:
			if scene_class.__name__ == scene_name:
				fw_config = scene_config["file_writer_config"]
				if fw_config["write_to_movie"]:
					fw_config["total_frames"] = compute_total_frames(scene_class, scene_config)
				scene = scene_class(**scene_config)
				result.append(scene)
				found = True
				break
		if not found and (scene_name != ""):
			log.error(f"No scene named {scene_name} found")
	if result:
		return result

	# another case
	result=[]
	if len(scene_classes) == 1:
		scene_classes = [scene_classes[0]]
	else:
		log.error(f"There're multiple scenes in the file. Plz specify one!")
		raise Exception()
	for scene_class in scene_classes:
		fw_config = scene_config["file_writer_config"]
		if fw_config["write_to_movie"]:
			fw_config["total_frames"] = compute_total_frames(scene_class, scene_config)
		scene = scene_class(**scene_config)
		result.append(scene)
	return result


def get_scene_class(scene_class_candidates, config):
	'''Get the scene class required from scene_class_candidates
	according to config['scene_names']. Only the first scene class 
	required is processed, the rest are ignored.

	IF scene class is specified in config['scene_names'] BUT not
	found in scene_class_candidates, an error will be raised.
	IF there're only ONE scene class in scene_class_candidates
	and NO s.c. is specified in config['scene_names'], this s.c. 
	will be returned as a default result.

	All write-to-file related config are ignored, for the time being.

	Modified from get_scenes_to_render(..) by StarSky.
	'''
	#if config["write_all"]: #ignore config about write
	#	return [sc(**scene_config) for sc in scene_classes]

	if len(config['scene_names'])>0:
		scene_name = config["scene_names"][0] # get only one scene and ignore other ones
		for scene_class in scene_class_candidates:
			if scene_class.__name__ == scene_name:
				return scene_class
		log.error(f"No scene named {scene_name} found")
		raise Exception()
		
	# no scene_name is specified in config['scene_names']
	elif len(scene_class_candidates) == 1:
		return scene_class_candidates[0]
	else:
		log.error(f"There're multiple scenes in the file. Plz specify one!")
		raise Exception()


def get_scene_classes_from_module(module):
	if hasattr(module, "SCENES_IN_ORDER"):
		return module.SCENES_IN_ORDER
	else:
		return [
			member[1]
			for member in inspect.getmembers(
				module,
				lambda x: is_child_scene(x, module)
			)
		]


def main(config):
	module = config["module"]
	scene_config = get_scene_config(config)
	if module is None:
		return [DefaultPlayground(**scene_config)]

	all_scene_classes_in_module = get_scene_classes_from_module(module)
	scene_class = get_scene_class(all_scene_classes_in_module, scene_config, config)
	return scene_class
