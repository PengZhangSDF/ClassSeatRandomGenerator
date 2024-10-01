import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QPropertyAnimation, QRect, Qt, QTimer

class AnimationWindow(QWidget):
    def __init__(self, students):
        super().__init__()
        self.students = students
        self.initUI()

    def initUI(self):
        self.setWindowTitle('动画演示')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()
        self.labels = []

        # 创建初始标签
        for index, (name, value) in enumerate(self.students):
            label = QLabel(f"{index + 1}. {name} {value:.3f}")
            label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(label)
            self.labels.append(label)

        self.setLayout(self.layout)

        # 开始动画
        self.start_animation()

    def start_animation(self):
        # 清除原始姓名
        for label in self.labels:
            label.setText("")  # 清空姓名

        # 随机赋值并更新标签
        for i, (name, _) in enumerate(self.students):
            new_value = random.uniform(0, 1)
            QTimer.singleShot(i * 100, lambda i=i, new_value=new_value: self.update_label(i, new_value))

        # 等待1秒后进行排序动画
        QTimer.singleShot(len(self.students) * 100 + 1000, self.sort_students)

    def update_label(self, index, value):
        self.labels[index].setText(f"{index + 1}. {self.students[index][0]} {value:.3f}")

    def sort_students(self):
        # 按值排序
        sorted_students = sorted(self.students, key=lambda x: x[1])
        self.layout.takeAt(0)  # 清空布局
        self.labels.clear()

        # 创建排序后的标签
        for index, (name, value) in enumerate(sorted_students):
            label = QLabel(f"{index + 1}. {name} {value:.3f}")
            label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(label)
            self.labels.append(label)

        # 动画移动到初始位置
        self.animate_labels()

    def animate_labels(self):
        for i, label in enumerate(self.labels):
            label.setGeometry(0, 0, 800, 50)  # 设置初始位置
            animation = QPropertyAnimation(label, b"geometry")
            animation.setDuration(1000)
            animation.setStartValue(QRect(0, 0, 800, 50))  # 初始位置
            animation.setEndValue(QRect(0, i * 50, 800, 50))  # 目标位置
            animation.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    students = [("张三", 0), ("李四", 0), ("王五", 0), ("赵六", 0)]  # 示例学生
    ex = AnimationWindow(students)
    ex.show()
    sys.exit(app.exec_())