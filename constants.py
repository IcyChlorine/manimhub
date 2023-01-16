# GLOBAL Preamable
BG_COLOR = '#222222'
DUMMY = 'DUMMY'#占位符

XDIM = 0
YDIM = 1

#语速
CH_PER_SECOND = 2.5 *2 # *2是因为中文是unicode字符，便于后面的计算
CH_PER_SEC = CH_PER_SECOND

#一些颜色
from manimlib.constants import GREY_A, YELLOW
FML_COLOR = GREY_A
ANNOTATION_COLOR = YELLOW
ANNOT_COLOR = ANNOTATION_COLOR # alias

# 中文字体
# 查看系统所有可用字体：py控制台中import manimpango, 随后manimpango.list_fonts()
# 查看中文字体对应的英文表示符：直接开始菜单搜索“字体”，打开“字体设置”即可查看。
黑体='SimHei'
楷体='KaiTi'
宋体='NSimSun'
微软雅黑='Microsoft YaHei UI'
落霞孤鹜='LXGW Wenkai'
文楷=落霞孤鹜 # alias

END_SCENE = 0
RESTART_SCENE = 1