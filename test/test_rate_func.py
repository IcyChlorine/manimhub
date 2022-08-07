from manimlib import *

# 为了能从父级目录import需要被测试的对象
import sys
__module_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__module_path__)
from manimhub.custom_rate_func import *

def visualize_partial():
	f=partial(0,3,smooth)
	X=np.linspace(0,1,100)
	Y=[f(x) for x in X]
	plt.plot(X/3,Y)
	f=partial(1,3,smooth)
	Y=[f(x) for x in X]
	plt.plot(X/3+1/3,Y)
	f=partial(2,3,smooth)
	Y=[f(x) for x in X]
	plt.plot(X/3+2/3,Y)

	plt.xlim(left=0,right=1)
	plt.ylim(bottom=0,top=1)
	plt.grid()
	plt.show()

def visualize_braking_end():
	f=braking_end
	X=np.linspace(0,1,100)
	Y=[f(x) for x in X]
	plt.plot(X,Y,label='braking_end')
	plt.legend()
	plt.grid()
	plt.show()

def visualize_emphasize():
	X=np.linspace(0,1,100)
	f=emphasize(2,2,linear)
	Y=[f(x) for x in X]
	plt.plot(X*6,Y,label='emphasize(t=2,T=2,linear)')
	f=emphasize(1,4,smooth)
	Y=[f(x) for x in X]
	plt.plot(X*6,Y,label='emphasize(t=1,T=4,smooth)')
	plt.legend();plt.grid();plt.show()

def visualize_lagged():
	X=np.linspace(0,1,100)
	f=lagged(0.5)
	Y=[f(x) for x in X]
	plt.plot(X*1.5,Y,label='lagged(t=0.5,T=1,smooth)')
	f=lagged(1,1,linear)
	Y=[f(x) for x in X]
	plt.plot(X*2,Y,label='lagged(t=1,T=1,linear)')
	plt.legend();plt.grid();plt.show()

#visualize_partial()
#visualize_braking_end()
#visualize_emphasize()
visualize_lagged()