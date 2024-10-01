# random_name.py
import random
from PyQt5.QtCore import QPropertyAnimation, QRect, QTimer

def randomize_and_assign_with_animation(boys, girls):
    all_students = boys + girls
    current_index = 0

    def assign_next_value():
        nonlocal current_index
        if current_index < len(all_students):
            name, _, label = all_students[current_index]
            random_value = round(random.uniform(0, 1), 5)  # 生成随机数
            all_students[current_index] = (name, random_value, label)  # 赋值
            label.setText(f"{name} {random_value}")  # 更新标签文本

            current_index += 1
        else:
            # 所有学生都已赋值，停止定时器
            timer.stop()
            sort_students_with_animation(all_students)

    # 创建定时器，每次调用 assign_next_value
    timer = QTimer()
    timer.timeout.connect(assign_next_value)
    timer.start(50)  # 每1秒调用一次

def sort_students_with_animation(all_students):
    # 根据随机值排序
    sorted_students = sorted(all_students, key=lambda x: x[1])
    
    # 清除当前序号
    for _, _, label in all_students:
        label.setText("")  # 清空当前序号

    # 获取当前标签的位置
    current_positions = {label: label.geometry() for _, _, label in all_students}

    # 创建动画
    for index, (name, random_value, label) in enumerate(sorted_students):
        # 计算目标位置
        target_y = 50 + index * 30  # 计算目标 y 坐标位置
        start_rect = current_positions[label]
        end_rect = QRect(start_rect.x(), target_y, start_rect.width(), start_rect.height())

        # 创建动画
        animation = QPropertyAnimation(label, b"geometry")
        animation.setDuration(500)  # 动画持续时间
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.start()

        # 更新标签文本
        label.setText(f"{name} {random_value}")  # 更新标签文本

    # 更新序号
    for index, (_, _, label) in enumerate(sorted_students):
        label.setText(label.text().split()[0] + f" {index + 1}")  # 更新序号