
# 班级座位随机生成器
## 为班级便捷生成座位列表
tip:程序基于PyQt5开发。随机原理来自于班主任
## 程序设计操作逻辑为了在电子白板上方便使用
# 使用说明
![图片教程01](https://github.com/PengZhangSDF/ClassSeatRandomGenerator/blob/master/img/1.png)
## 程序界面：

 - **左侧界面：** 显示序号，姓名，随机数（初始为0.000）
 - **右侧界面**：座位表，可以更改，数字对应姓名的序号
 - **下方第一排彩色按钮：** 时座位表编辑按钮，点击按钮，再点击对应座位方块就可以变为相应座位类型。白色和灰色都不会坐人，仅供分割过道，墙面使用。
 - **左侧列表**：boys为男生，girls为女生，ignore为忽略学生。男生一定会坐在蓝色方块上，女生一定会坐在黄色方块上，ignore的学生一定没有座位
 
 - **开始随机按钮：** 点击“开始随机为”非ignore学生随机赋值后重新排序，排出的序号为左侧位置对应的序号
 - **保存当前座位分布表按钮**：点击后将保存当前编辑好的座位表到文件，下次运行直接读取 **！！该操作不可逆！！**
 -  **将结果投影到座位表上按钮:**  将学生姓名按照序号投影到座位表上。（对于这个操作，一旦你编辑座位表，所有投影都会撤销）
 - **清除投影结果按钮**：清除投影的学生姓名
 - **保存本次随机结果**：将本次结果保存为文件方便读取
 - **加载保存的结果**：将保存的结果加载出来
 - **编辑名字**：进入名字编辑界面
 - **导出到Excel**：将**当前显示**的座位表保存为Excel表格（如果你的座位表只有数字那么只会保存为数字）
 ## 图片教程和程序展示
 ![1](https://github.com/PengZhangSDF/ClassSeatRandomGenerator/blob/master/img/2.png)
 ![2](https://github.com/PengZhangSDF/ClassSeatRandomGenerator/blob/master/img/3.png)
 ![3](https://github.com/PengZhangSDF/ClassSeatRandomGenerator/blob/master/img/4.png)
 ![4](https://github.com/PengZhangSDF/ClassSeatRandomGenerator/blob/master/img/5.png)
 ![5](https://github.com/PengZhangSDF/ClassSeatRandomGenerator/blob/master/img/6.png)
 # 感谢
 ## [PyQt5](https://github.com/PyQt5/PyQt)提供图像界面支持
 ## [openpyxl](https://github.com/python-excel/xlrd)提供Excel表格保存
 ## [pandas](https://github.com/pandas-dev/pandas) 提供数据处理