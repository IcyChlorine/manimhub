from typing import Iterable, Tuple

from manimlib import *

from manimhub.constants import *
from manimhub.custom_rate_func import *

# alias
Create = ShowCreation
class Popup(GrowFromCenter):
	def __init__(self, mobject: Mobject, **kwargs):
		super().__init__(mobject, **kwargs)
		self.update_rate_info(rate_func=braking_end)

# Transform adds extra points to src. mobj. so it has same #points as tgt. mobj.
# before interpolating when animation.
# But these extra points are NOT cleaned up when animation is finished.
# So I write this CleanTransform tnat cleans up extra points when finished.
# 
# This is useful when compliated VMobjects are transformed into simple ones or complex ones,
# making things clearer and rendering faster.
#
# Not sure (not tested) about its compatibility.
# Suggestion: use it for VMobjects only, when you know its necessary.
class CleanTransform(Transform):
	def finish(self) -> None:
		super().finish()
		for m1,m2 in zip(self.mobject.get_family(),self.target_mobject.get_family()):
			l1=len(m1.get_points())
			l2=len(m2.get_points())
			if l1>l2:
				m1.set_points(m2.get_points())

# Only coarsely tested. May have bugs.
class TransformByIndexMap(AnimationGroup):
	transform_class = CleanTransform
	def __init__(self, 
			mobject: Mobject,
       		target_mobject: Mobject,
			keys: Iterable, values: Iterable,
			transform_class: Transform,
	 		**kwargs
		):
		self.transform_class = transform_class
		super().__init__(mobject, **kwargs)

		assert(len(keys)==len(values))
		l1,l2=len(mobject),len(target_mobject)
		# TODO: assert indexes in keys and values 1)in range of l1&l2, 2)not conflicted 3)ordered
		assert(True) #suppose they're satisfied here
		
		M1=mobject;M2=target_mobject
		if isinstance(M1,VMobject) and isinstance(M2,VMobject):
			self.group_class = VGroup 
		else:
			self.group_class = Group

		animations = self._compile_animations(mobject,target_mobject,keys,values)
		super().__init__(*animations, **kwargs)

	def _compile_animations(self, M1, M2, keys, values):
		animations=[]
		# convert a bit
		for i in range(len(keys)):
			if isinstance(keys[i],int): keys[i]=(keys[i],)
			if isinstance(values[i],int): values[i]=(values[i],)
		keys:   Tuple[Tuple[int]]
		values: Tuple[Tuple[int]]

		# compile		
		T=self.transform_class
		if len(keys)==0: return T(M1,M2)

		m1,m2=None,None
		start_key = range(0,keys[0][0])
		start_value = range(0,values[0][0])
		animations.append(self._get_animation(M1,M2,start_key,start_value))

		for i in range(len(keys)):
			key,value = keys[i],values[i]
			animations.append(self._get_animation(M1,M2,key,value))

			# 自动补上当中的部分
			if i==len(keys)-1: continue
			#not last
			key_next, value_next = keys[i+1],values[i+1]
			intermediate_key = range(key[-1]+1,key_next[0])
			intermediate_value = range(value[-1]+1,value_next[0])
			animations.append(self._get_animation(M1,M2,intermediate_key,intermediate_value))

		end_key = range(keys[-1][-1]+1,len(M1))
		end_value = range(values[-1][-1]+1,len(M2))
		animations.append(self._get_animation(M1,M2,end_key,end_value))

		return animations

	def _get_animation(self, M1,M2,key,value):
		G=self.group_class
		T=self.transform_class
		
		if len(key)>0: m1=G(*[M1[k] for k in key])
		else: m1=None
		if len(value)>0: m2=G(*[M2[v] for v in value])
		else: m2=None

		if len(key)==0 and len(value)==0: return None
		elif len(key)==0:   return FadeIn(m2)
		elif len(value)==0: return FadeOut(m1)
		else: return T(m1,m2)

	# not used!
	# a bit subtle. 
	# 如想debug或修改，建议开个notebook实际运行、试试看。
	def _parse_index_map(index_map):
		ans=[]
		for X,Y in index_map:
			S=[]
			while X>10: S.append(X%10);X=X//10
			S.append(X)
			X=tuple(S[::-1]) if len(S)>1 else S[0]
			S=[]
			while Y>10: S.append(Y%10);Y=Y//10
			S.append(Y)
			Y=tuple(S[::-1]) if len(S)>1 else S[0]
			ans.append((X,Y))
		return ans
