from manimlib import *

from manimhub.constants import *
from manimhub.custom_rate_func import *

class Popup(GrowFromCenter):
	CONFIG = {
		'rate_func': braking_end,
		'clip_alpha': False
	}