from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QFont


class RandomizationWindow(QDialog):
    def __init__(self, parent, geometry, current_font, small_point):
        super().__init__(parent)
        self.setWindowTitle("随机过程")
        self.setGeometry(geometry)  # 设置窗口大小和位置
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # 隐藏标题栏
        self.setWindowOpacity(0)  # 设置透明度为80%

        self.layout = QVBoxLayout()
        self.grid_layout = QGridLayout()  # 使用网格布局
        self.layout.addLayout(self.grid_layout)
        self.setLayout(self.layout)
        self.font_scale = current_font
        self.small_point = small_point

    def update_display(self, group_first, group_second, current_index):
        """更新显示的座位信息"""
        # 清空之前的内容
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()  # 删除小部件

        try:
            # 计算每组的最大行数
            max_rows_group1 = (len(group_first) + 2) // 3  # 向上取整，确保每列最多有 max_rows 行
            max_rows_group2 = (len(group_second) + 2) // 3  # 向上取整，确保每列最多有 max_rows 行

            # 根据当前索引决定显示哪个组
            if current_index < len(group_first):
                displayed_students = group_first
                max_rows_current = max_rows_group1
                current_student_index = current_index  # 当前学生在第一组中的索引
            else:
                displayed_students = group_second
                max_rows_current = max_rows_group2
                current_student_index = current_index - len(group_first)  # 当前学生在第二组中的索引

            # 更新显示
            for i in range(len(displayed_students)):
                name, random_value = displayed_students[i]

                # 创建标签并设置字体
                if i == current_student_index:  # 当前学生
                    label = QLabel(
                        f"{name} <span style='background-color: blue; color: white;'>{random_value:.{self.small_point}f}</span>")
                else:  # 其他学生
                    label = QLabel(f"{name} {random_value:.{self.small_point}f}")

                label.setFont(QFont('Arial', int(24 * self.font_scale), QFont.Bold))  # 设置字体大小和加粗
                label.setTextFormat(Qt.RichText)  # 允许使用富文本格式
                label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许文本选择

                # 计算列索引和行索引，保持纵向排列
                column = i // max_rows_current  # 计算列索引（0, 1, 2）
                row = i % max_rows_current  # 计算行索引
                self.grid_layout.addWidget(label, row, column)  # 每列最多 max_rows 行

        except Exception as e:
            print(f"Error updating display: {e}")