# manimhub

a repo for manim customization for starsky

### Manifesto

在使用manim进行创作的过程中，往往需要自定义mobject、修改manim库、来达到想要的效果。这可以通过两种方式达到：

+ 修改manim库源码
+ 继承manim中的类，通过继承和多态实现自己需要的功能

直接修改manim源码的话，代码很难进入manim主仓库，导致自己的代码分支与主要开发分支渐行渐远。因此一个更好的解决方案是*尽可能*通过继承和重载实现自己的功能。

在自定义的对象中，我将常用的代码抽离，放到这个叫做manimhub的仓库中，从而我可以统一管理，避免代码冗余。此外，我还可以进行代码版本管理，发布到github以进行备份。

### Contents

在这个repo里主要包括的内容有：

+ custom_mobject.py 自定义的mobject
+ little_creature.py 小白的代码 
+ custom_animation.py 自定义的动画效果，如Popup
+ custom_rate_func.py 自定义的插值函数，为动画配合
+ my_scene.py 我的scene，加了一些额外功能
+ test/ 测试模块——代码未动，测试先行！

### Tips

使用方法：

```python
# 不安装时的食用方法
import os, sys
sys.path.append('C:/StarSky/Programming/MyProjects/')
from manimhub import *
```

manimhub的分支与manim的分支对应。例如，manimhub中的starsky分支对应在manim的starsky分支上配合使用。否则可能出现一些bug。