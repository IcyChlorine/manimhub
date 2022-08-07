from manimlib import *

def always_zero(t) -> float:
	return 0

# (t,T,t) animation, very handy for temp emphasize effects
# t时间transition-T时间不动-t时间transition，按比例
def emphasize(t,T,transition_rate_func=linear) -> float:
	T_tot=T+2*t
	t,T=t/T_tot, T/T_tot#归一化
	def wrapped_rate_func(t_):
		ans=None
		if t_<t:
			ans = transition_rate_func(t_/t)
		elif t_<t+T:
			ans = 1
		else:
			ans = transition_rate_func(1-(t_-T-t)/t) 
		return ans

	return wrapped_rate_func

def clamp(t) -> float:#为了bug手动处理一下
	if t<0: return 0
	if t>1: return 1
	else: return t
#前t/(t+T)时间内不动(值为零)，后T/(t+T)时间内为original_rate_func
#便于进行LaggedStart类似的动画
def lagged(t,T=1,original_rate_func=smooth) -> float:
	t,T=t/(t+T),T/(t+T)#归一化
	def wrapped_rate_func(_t):
		if _t<t: return 0
		else: return clip(original_rate_func((_t-t)/T),0,1)
		
	return wrapped_rate_func

# @deprecated as its too complicated
# 为了把几个动画拼起来的时候要用到的rate_func
# 假设mother_rate_func单调递增
def partial(k,n,mother_rate_func=smooth):
	t_start=k/n
	t_end=(k+1)/n
	f_start=mother_rate_func(t_start)
	f_end=mother_rate_func(t_end)
	def wrapped_rate_func(t):
		f=mother_rate_func(t*(t_end-t_start)+t_start)#[0,1]->[t_start, t_end]
		return (f-f_start)/(f_end-f_start)
	return wrapped_rate_func

# rate func plot util
import matplotlib.pyplot as plt
def plot_rate_func(rate_func):
	X=np.linspace(0,1,100)
	Y=[rate_func(x) for x in X]
	plt.plot(X,Y)
	plt.grid()
