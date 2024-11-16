# main.py
import sys, os
import random
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, \
    QButtonGroup, QFileDialog, QGroupBox, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QPalette, QPixmap, QIcon
from edit_mode import EditMode
from export_to_excel import export_seating_arrangement

from win32 import win32api, win32gui, win32print
from win32.lib import win32con
from win32.win32api import GetSystemMetrics
import os
import time

def get_real_resolution():
    """获取真实的分辨率"""
    hDC = win32gui.GetDC(0)
    # 横向分辨率
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return w, h

def get_screen_size():
    """获取缩放后的分辨率"""
    w = GetSystemMetrics(0)
    h = GetSystemMetrics(1)
    return w, h

def get_dpi():
    real_resolution = get_real_resolution()
    screen_size = get_screen_size()

    screen_scale_rate = round(real_resolution[0] / screen_size[0], 2)
    screen_scale_rate = screen_scale_rate * 100
    return screen_scale_rate

userdpi = get_dpi()
print('当前系统缩放率为:', userdpi, '%', end='')
font_scale = 1/(userdpi/100)
class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("欢迎使用程序")
        self.setGeometry(50, 20, 1480, 1000)

        self.layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.button_layout = QHBoxLayout()
        self.prev_button = QPushButton("上一步")
        self.prev_button.setFixedSize(600, 30)
        self.next_button = QPushButton("下一步")
        self.next_button.setFixedSize(600, 30)
        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.next_button)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

        self.images = [f"./img/{i}.png" for i in range(1, 7)]  # 图片路径
        self.current_index = 0

        self.prev_button.clicked.connect(self.show_prev_image)
        self.next_button.clicked.connect(self.show_next_image)

        self.show_image()

    def show_image(self):
        if 0 <= self.current_index < len(self.images):
            pixmap = QPixmap(self.images[self.current_index])
            self.image_label.setPixmap(pixmap)  # 显示原始大小的图片
            self.image_label.setFixedSize(pixmap.size())  # 设置标签大小为图片大小

    def show_prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()

    def show_next_image(self):
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.show_image()
        else:
            self.close()  # 关闭图片查看器


class SeatingArrangement(QWidget):
    def __init__(self):
        super().__init__()
        self.edit_mode_window = None
        self.selected_color = None  # 初始化 selected_color 属性
        self.saved_seating_arrangement = None  # 保存当前座位表状态
        self.font_scale = font_scale  # 字体大小倍数
        self.initUI()
    def showEvent(self, event):
        # 在窗口显示时调整大小到最小可缩小的尺寸
        self.adjustSize()  # 调整窗口大小
        super().showEvent(event)  # 调用父类的 showEvent

    def initUI(self):
        self.setWindowTitle('随机座位生成器')
        self.setGeometry(100, 50, 1280, 1000)  # Ensure vertical resolution does not exceed 800

        main_layout = QVBoxLayout()

        # Top part: Names list and seating grid
        top_layout = QHBoxLayout()
        self.check_and_update_students_file()
        # Left side: Names list
        self.names_layout = QVBoxLayout()
        self.names_container = QWidget()
        self.names_container.setLayout(self.names_layout)
        top_layout.addWidget(self.names_container)

        # Right side: Seating grid
        self.grid_layout = QGridLayout()
        self.create_seating_grid()
        grid_container = QWidget()
        grid_container.setLayout(self.grid_layout)
        top_layout.addWidget(grid_container)

        main_layout.addLayout(top_layout)

        # Bottom part: Color selection buttons and action buttons
        self.color_buttons_layout = QHBoxLayout()
        self.create_color_buttons()
        main_layout.addLayout(self.color_buttons_layout)

        self.action_buttons_layout = QHBoxLayout()
        self.create_action_buttons()
        main_layout.addLayout(self.action_buttons_layout)

        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.warning_label)

        self.setLayout(main_layout)

        self.load_names()
        self.load_seating_arrangement()

    def check_and_update_students_file(self):
        filename = 'students.txt'

        # 检查文件是否存在
        if not os.path.exists(filename):
            QMessageBox.warning(None, "第一次使用？", "请先创建一个students.txt！\n文件里面竖向排列姓名,最后移动到程序目录下，例如：\n"
                                                     ">>students.txt\n张三\n李四\n王五", QMessageBox.Ok)
            exit()  # 结束程序运行

        # 读取文件内容
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 检查是否存在 [group_first], [group_second], [ignore]
        has_group_first = '[group_first]\n' in lines
        has_group_second = '[group_second]\n' in lines
        has_ignore = '[ignore]\n' in lines

        # 如果都存在，结束函数
        if has_group_first and has_group_second and has_ignore:
            return

        # 创建新的内容列表
        new_lines = []

        # 添加 [group_first] 在开头
        if not has_group_first:
            new_lines.append('[group_first]\n')

        # 添加原有内容
        new_lines.extend(lines)

        # 添加 [group_second] 在中间行
        if not has_group_second:
            middle_index = len(new_lines) // 2  # 计算中间行的索引
            new_lines.insert(middle_index, '[group_second]\n')

        # 添加 [ignore] 在末尾
        if not has_ignore:
            new_lines.append('[ignore]\n')

        # 写入新的内容到文件
        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
    def enter_fullscreen_mode(self):
        self.fullscreen_window = QWidget()
        self.fullscreen_window.setWindowTitle("全屏展示座位表")
        self.fullscreen_window.setGeometry(0, 0, 1920, 1080)  # Set to fullscreen size
        layout = QVBoxLayout()

        # Create a scaled seating grid
        scaled_grid = QGridLayout()
        for row in range(12):
            for col in range(12):
                seat = self.seats[row][col]
                scaled_seat = QPushButton(seat.text())
                scaled_seat.setFixedSize(120, 60)  # Scale size by 1.5
                scaled_seat.setStyleSheet(seat.styleSheet())  # Keep the same style
                scaled_seat.setFont(QFont('Arial', int(21 * self.font_scale)))  # Scale font size by 1.5
                scaled_grid.addWidget(scaled_seat, row, col)

        layout.addLayout(scaled_grid)

        # Exit fullscreen button
        exit_button = QPushButton("退出全屏展示")
        exit_button.setFixedHeight(100)
        exit_button.setFont(QFont('Arial', int(24 * self.font_scale)))
        exit_button.clicked.connect(self.exit_fullscreen_mode)
        layout.addWidget(exit_button)

        self.fullscreen_window.setLayout(layout)
        self.fullscreen_window.show()

    def exit_fullscreen_mode(self):
        self.fullscreen_window.close()
    def check_first_run(self):
        if not os.path.exists("hello_world.txt"):
            with open("hello_world.txt", "w") as f:
                f.write("This is the first run of the program.")
            self.show_image_viewer()  # Show the image viewer on first run

    def show_image_viewer(self):
        self.image_viewer = ImageViewer()
        self.image_viewer.show()

    def load_names(self):
        self.group_first = []
        self.group_second = []
        self.ignore = []

        with open('students.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()

        current_category = None
        for line in lines:
            line = line.strip()
            if line == '[group_first]':
                current_category = 'group_first'
            elif line == '[group_second]':
                current_category = 'group_second'
            elif line == '[ignore]':
                current_category = 'ignore'
            elif line:
                label = QLabel(f"{line} 0.000")
                label.setFont(QFont('Arial', int(16 * self.font_scale)))  # Increase font size
                label.setAlignment(Qt.AlignLeft)
                if current_category == 'group_first':
                    self.group_first.append((line, 0.000, label))
                elif current_category == 'group_second':
                    self.group_second.append((line, 0.000, label))
                elif current_category == 'ignore':
                    self.ignore.append((line, label))

        self.update_names_layout()

    def save_current_seating_arrangement(self):
        result = {
            'group_first': [(name, random_value) for name, random_value, _ in self.group_first],
            'group_second': [(name, random_value) for name, random_value, _ in self.group_second],
            'seating_arrangement': []
        }
        for row in range(12):
            for col in range(12):
                seat = self.seats[row][col]
                seat_color = seat.palette().color(QPalette.Button).name()
                seat_text = seat.text()
                result['seating_arrangement'].append({
                    'row': row,
                    'col': col,
                    'color': seat_color,
                    'text': seat_text
                })
        filename = "temp_seating_arrangement.json"
        with open(filename, 'w') as file:
            json.dump(result, file, indent=4)

    def restore_seating_arrangement(self,IFreload):
        try:
            with open('temp_seating_arrangement.json', 'r') as file:
                result = json.load(file)
                if IFreload:
                    self.group_first = [(name, random_value, self.create_label(name, random_value)) for name, random_value in
                                 result['group_first']]
                    self.group_second = [(name, random_value, self.create_label(name, random_value)) for name, random_value in
                                  result['group_second']]
                    self.update_names_layout()

                for seat_info in result['seating_arrangement']:
                    row = seat_info['row']
                    col = seat_info['col']
                    color = seat_info['color']
                    text = seat_info['text']
                    seat = self.seats[row][col]
                    seat.setStyleSheet(f"background-color: {color};")
                    seat.setText(text)
            self.check_seating_balance()
            os.remove('temp_seating_arrangement.json')  # 删除临时文件
        except:
            os.remove('temp_seating_arrangement.json')  # 删除临时文件
            pass

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    def update_names_layout(self):
        self.clear_layout(self.names_layout)

        group_first_layout = QHBoxLayout()
        group_second_layout = QHBoxLayout()
        ignore_layout = QHBoxLayout()

        self.add_names_to_layout(self.group_first, group_first_layout, 3, True)
        self.add_names_to_layout(self.group_second, group_second_layout, 3, True)
        self.add_names_to_layout(self.ignore, ignore_layout, 3, False)

        group_first_group = QGroupBox("组别一")
        group_first_group.setFont(QFont('Arial', int(14 * font_scale)))
        group_first_group.setLayout(group_first_layout)
        group_second_group = QGroupBox("组别二")
        group_second_group.setFont(QFont('Arial', int(14 * font_scale)))
        group_second_group.setLayout(group_second_layout)
        ignore_group = QGroupBox("忽略（不排入位置）")
        ignore_group.setFont(QFont('Arial', int(14 * font_scale)))
        ignore_group.setLayout(ignore_layout)

        self.names_layout.addWidget(group_first_group)
        self.names_layout.addWidget(group_second_group)
        self.names_layout.addSpacing(20)  # Add some space between group_second and ignore
        self.names_layout.addWidget(ignore_group)
    def add_names_to_layout(self, names, layout, columns, has_random_value):
        total_count = len(names)
        max_items_per_column = (total_count + columns - 1) // columns  # 计算每列的最大项数

        column_layouts = [QVBoxLayout() for _ in range(columns)]

        # 按列竖向添加姓名
        for i, item in enumerate(names):
            col = i // max_items_per_column  # 确定当前项所在的列
            row = i % max_items_per_column  # 确定当前项所在的行

            # 确保列索引不超过最大列数
            if col >= columns:
                break  # 如果列索引超出范围，停止添加

            # 创建一个水平布局来对齐序号和姓名
            h_layout = QHBoxLayout()
            h_layout.setSpacing(3)  # 设置列间隔为3个空格

            if has_random_value:
                name, random_value, label = item
                if col == 0:
                    number_label = QLabel(f"{i + 1}. ")  # 序号标签，后面加一个空格
                else:
                    number_label = QLabel(f"      {i + 1}. ")  # 序号标签，后面加一个空格
                number_label.setFont(QFont('Arial', int(16 * self.font_scale)))  # 确保字号一致
                number_label.setAlignment(Qt.AlignLeft)
                h_layout.addWidget(number_label)  # 添加序号标签
                label.setText(f"{name.split()[0]} {random_value}")  # 只显示名字和随机值
            else:
                name, label = item
                number_label = QLabel(f"   {i + 1}. ")  # 序号标签，后面加一个空格
                number_label.setFont(QFont('Arial', int(16 * self.font_scale)))  # 确保字号一致
                number_label.setAlignment(Qt.AlignLeft)
                h_layout.addWidget(number_label)  # 添加序号标签
                label.setText(f"{name.split()[0]}")  # 只显示名字

            # 设置姓名标签的固定高度
            label.setFixedHeight(20)  # 行间距固定为20
            h_layout.addWidget(label)  # 添加姓名标签到水平布局

            column_layouts[col].addLayout(h_layout)  # 将水平布局添加到对应的列布局

        # 填充空白行以保持列高度一致
        for col in range(columns):
            current_row_count = column_layouts[col].count()  # 获取当前列的项数
            for _ in range(max_items_per_column - current_row_count):
                h_layout = QHBoxLayout()
                h_layout.setSpacing(3)  # 设置列间隔为3个空格
                h_layout.addWidget(QLabel(""))  # 添加一个空标签以占位
                column_layouts[col].addLayout(h_layout)  # 将空布局添加到对应的列布局

        for column_layout in column_layouts:
            layout.addLayout(column_layout)  # 将每列布局添加到主布局

    def create_seating_grid(self):
        self.seats = []
        self.boy_count = 1
        self.girl_count = 1
        for row in range(12):
            row_seats = []
            for col in range(12):
                seat = QPushButton()
                seat.setFixedSize(80, 40)
                seat.setStyleSheet("background-color: white;")
                seat.setFont(QFont('Arial', int(14 * self.font_scale)))
                seat.clicked.connect(self.change_seat_color)
                self.grid_layout.addWidget(seat, row, col)
                row_seats.append(seat)
            self.seats.append(row_seats)

    def export_seating_arrangement(self):
        export_seating_arrangement(self.seats, self.group_first, self.group_second)  # 调用导出功能

    def enter_edit_mode(self):
        print("Entering edit mode...")  # 调试信息
        # 保存当前座位表状态到临时文件
        if os.path.exists('temp_seating_arrangement.json'):
            os.remove('temp_seating_arrangement.json')
            print("Deleted temp_seating_arrangement.json")
        self.save_current_seating_arrangement_to_file()

        # 清空界面
        self.clear_layout(self.names_layout)
        self.clear_layout(self.grid_layout)
        self.clear_layout(self.color_buttons_layout)
        self.clear_layout(self.action_buttons_layout)
        self.warning_label.clear()

        self.edit_mode_window = EditMode(self)
        self.edit_mode_window.show()

    def save_current_seating_arrangement_to_file(self):
        result = {
            'group_first': [(name, random_value) for name, random_value, _ in self.group_first],
            'group_second': [(name, random_value) for name, random_value, _ in self.group_second],
            'seating_arrangement': []
        }
        for row in range(12):
            for col in range(12):
                seat = self.seats[row][col]
                seat_color = seat.palette().color(QPalette.Button).name()
                seat_text = seat.text()
                result['seating_arrangement'].append({
                    'row': row,
                    'col': col,
                    'color': seat_color,
                    'text': seat_text
                })
        file_index = 1
        filename = f'temp_seating_arrangement.json'

        # 检查文件是否已存在，递增数字
        while os.path.exists(filename):
            file_index += 1
            filename = f'temp_seating_arrangement.json'

        with open(filename, 'w') as file:
            json.dump(result, file, indent=4)

    def create_color_buttons(self):
        self.color_buttons = QButtonGroup(self)
        self.color_buttons.buttonClicked[int].connect(self.set_selected_color)

        self.white_button = QPushButton("空白位置")
        self.white_button.setStyleSheet("background-color: white;")
        self.white_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.white_button.setFixedHeight(30)
        self.color_buttons.addButton(self.white_button, 0)
        self.color_buttons_layout.addWidget(self.white_button)

        self.lightblue_button = QPushButton("组别一位置")
        self.lightblue_button.setStyleSheet("background-color: lightblue;")
        self.lightblue_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.lightblue_button.setFixedHeight(30)
        self.color_buttons.addButton(self.lightblue_button, 1)
        self.color_buttons_layout.addWidget(self.lightblue_button)

        self.lightyellow_button = QPushButton("组别二位置")
        self.lightyellow_button.setStyleSheet("background-color: lightyellow;")
        self.lightyellow_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.lightyellow_button.setFixedHeight(30)
        self.color_buttons.addButton(self.lightyellow_button, 2)
        self.color_buttons_layout.addWidget(self.lightyellow_button)

        self.gray_button = QPushButton("无意义位置")
        self.gray_button.setStyleSheet("background-color: gray;")
        self.gray_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.gray_button.setFixedHeight(30)
        self.color_buttons.addButton(self.gray_button, 3)
        self.color_buttons_layout.addWidget(self.gray_button)

        self.fullscreen_button = QPushButton("全屏展示当前座位表")
        self.fullscreen_button.setStyleSheet("background-color: orange;")
        self.fullscreen_button.setIcon(QIcon("./img/expand.png"))  # 设置图标
        self.fullscreen_button.setIconSize(
            QSize(int(18 * self.font_scale), int(18 * self.font_scale)))  # 设置图标大小
        self.fullscreen_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.fullscreen_button.setFixedHeight(30)
        self.fullscreen_button.clicked.connect(self.enter_fullscreen_mode)
        self.color_buttons.addButton(self.fullscreen_button, 4)
        self.color_buttons_layout.addWidget(self.fullscreen_button)

    def create_action_buttons(self):
        button_font = QFont('Arial', int(14 * self.font_scale))

        self.randomize_button = QPushButton("开始随机")
        self.randomize_button.setIcon(QIcon("./img/random.png"))  # 设置图标
        self.randomize_button.setIconSize(QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.randomize_button.setFont(button_font)
        self.randomize_button.setFixedHeight(50)
        self.randomize_button.clicked.connect(self.randomize_seating)
        self.action_buttons_layout.addWidget(self.randomize_button)

        #self.save_button = QPushButton("保存当前座位分布表")
#        self.save_button.setFont(button_font)
#        self.save_button.setFixedHeight(50)
#        self.save_button.clicked.connect(self.save_seating_arrangement)
#       self.action_buttons_layout.addWidget(self.save_button)

        self.project_button = QPushButton("投影结果到座位表")
        self.project_button.setIcon(QIcon("./img/project.png"))  # 设置图标
        self.project_button.setIconSize(QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.project_button.setFont(button_font)
        self.project_button.setFixedHeight(50)
        self.project_button.clicked.connect(self.project_to_seating)
        self.action_buttons_layout.addWidget(self.project_button)

        self.clear_projection_button = QPushButton("清除投影的结果")
        self.clear_projection_button.setIcon(QIcon("./img/clear.png"))  # 设置图标
        self.clear_projection_button.setIconSize(QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.clear_projection_button.setFont(button_font)
        self.clear_projection_button.setFixedHeight(50)
        self.clear_projection_button.clicked.connect(self.clear_projection)
        self.action_buttons_layout.addWidget(self.clear_projection_button)

        self.save_random_result_button = QPushButton("保存本次随机结果")
        self.save_random_result_button.setIcon(QIcon("./img/save.png"))  # 设置图标
        self.save_random_result_button.setIconSize(QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.save_random_result_button.setFont(button_font)
        self.save_random_result_button.setFixedHeight(50)
        self.save_random_result_button.clicked.connect(self.save_random_result)
        self.action_buttons_layout.addWidget(self.save_random_result_button)

        self.load_random_result_button = QPushButton("加载保存的结果")
        self.load_random_result_button.setIcon(QIcon("./img/load.png"))  # 设置图标
        self.load_random_result_button.setIconSize(QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.load_random_result_button.setFont(button_font)
        self.load_random_result_button.setFixedHeight(50)
        self.load_random_result_button.clicked.connect(self.load_random_result)
        self.action_buttons_layout.addWidget(self.load_random_result_button)

        self.edit_names_button = QPushButton('编辑名字')
        self.edit_names_button.setIcon(QIcon("./img/edit_name.png"))  # 设置图标
        self.edit_names_button.setIconSize(
            QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.edit_names_button.setFont(button_font)
        self.edit_names_button.setFixedHeight(50)
        self.edit_names_button.clicked.connect(self.enter_edit_mode)
        self.action_buttons_layout.addWidget(self.edit_names_button)

        self.export_button = QPushButton("导出座位表到 Excel")
        self.export_button.setIcon(QIcon("./img/excel.png"))  # 设置图标
        self.export_button.setIconSize(
            QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.export_button.setFont(button_font)
        self.export_button.setFixedHeight(50)
        self.export_button.clicked.connect(self.export_seating_arrangement)  # 连接导出功能
        self.action_buttons_layout.addWidget(self.export_button)

    def set_selected_color(self, id):
        if id == 0:
            self.selected_color = "white"
        elif id == 1:
            self.selected_color = "lightblue"
        elif id == 2:
            self.selected_color = "lightyellow"
        elif id == 3:
            self.selected_color = "gray"
    def change_seat_color(self):
        sender = self.sender()
        if self.selected_color:
            current_color = sender.palette().color(QPalette.Button).name()
            if self.selected_color == "white":
                sender.setStyleSheet("background-color: white;")
                sender.setText("")
            elif self.selected_color == "lightblue":
                sender.setStyleSheet("background-color: lightblue;")
            elif self.selected_color == "lightyellow":
                sender.setStyleSheet("background-color: lightyellow;")
            elif self.selected_color == "gray":
                sender.setStyleSheet("background-color: gray;")
                sender.setText("")
            self.update_seat_numbers()
            self.check_seating_balance()
            self.save_seating_arrangement()

    def update_seat_numbers(self):
        self.boy_count = 1
        self.girl_count = 1

        for row in self.seats:
            for seat in row:
                seat_color = seat.palette().color(QPalette.Button).name()
                if seat_color == "#add8e6":  # lightblue
                    seat.setText(str(self.boy_count))
                    self.boy_count += 1
                elif seat_color == "#ffffe0":  # lightyellow
                    seat.setText(str(self.girl_count))
                    self.girl_count += 1
                else:
                    seat.setText("")

    def randomize_seating(self):
        all_students = self.group_first + self.group_second
        current_index = 0

        def assign_next_value():
            nonlocal current_index
            if current_index < len(all_students):
                name, _, label = all_students[current_index]
                random_value = round(random.uniform(0, 1), 4)  # 生成随机数
                all_students[current_index] = (name, random_value, label)  # 赋值
                label.setText(f"{name} {random_value}")  # 更新标签文本

                current_index += 1
            else:
                # 所有学生都已赋值，停止定时器
                timer.stop()

                # 将赋值结果写回到各自的类别
                self.group_first = all_students[:len(self.group_first)]
                self.group_second = all_students[len(self.group_first):]

                # 对男生和女生类别分别进行排序
                for category in [self.group_first, self.group_second]:
                    category.sort(key=lambda x: x[1])

                # 更新布局
                self.update_names_layout()

        # 创建定时器，每50毫秒调用一次 assign_next_value
        timer = QTimer()
        timer.timeout.connect(assign_next_value)
        timer.start(50)  # 每50毫秒调用一次

    def project_to_seating(self):
        boy_index = 0
        girl_index = 0
        for row in range(12):
            for col in range(12):
                seat = self.seats[row][col]
                seat_color = seat.palette().color(QPalette.Button).name()
                if seat_color == "#add8e6" and boy_index < len(self.group_first):  # lightblue
                    name, _, label = self.group_first[boy_index]
                    seat.setText(name.split()[0])
                    boy_index += 1
                elif seat_color == "#ffffe0" and girl_index < len(self.group_second):  # lightyellow
                    name, _, label = self.group_second[girl_index]
                    seat.setText(name.split()[0])
                    girl_index += 1
        self.check_seating_balance()

    def clear_projection(self):
        for row in range(12):
            for col in range(12):
                seat = self.seats[row][col]
                seat.setText("")
        self.update_seat_numbers()
        self.check_seating_balance()

    def save_seating_arrangement(self):
        seating_arrangement = []
        for row in range(12):
            for col in range(12):
                seat = self.seats[row][col]
                seat_color = seat.palette().color(QPalette.Button).name()
                seat_text = seat.text()
                seating_arrangement.append({
                    'row': row,
                    'col': col,
                    'color': seat_color,
                    'text': seat_text
                })

        with open('seating_arrangement.json', 'w') as file:
            json.dump(seating_arrangement, file, indent=4)

    def load_seating_arrangement(self):
        try:
            with open('seating_arrangement.json', 'r') as file:
                seating_arrangement = json.load(file)
                for seat_info in seating_arrangement:
                    row = seat_info['row']
                    col = seat_info['col']
                    color = seat_info['color']
                    text = seat_info['text']
                    seat = self.seats[row][col]
                    seat.setStyleSheet(f"background-color: {color};")
                    seat.setText(text)
            self.check_seating_balance()
        except FileNotFoundError:
            pass

    def save_random_result(self):
        result = {
            'group_first': [(name, random_value) for name, random_value, _ in self.group_first],
            'group_second': [(name, random_value) for name, random_value, _ in self.group_second],
            'seating_arrangement': []
        }
        for row in range(12):
            for col in range(12):
                seat = self.seats[row][col]
                seat_color = seat.palette().color(QPalette.Button).name()
                seat_text = seat.text()
                result['seating_arrangement'].append({
                    'row': row,
                    'col': col,
                    'color': seat_color,
                    'text': seat_text
                })
        today = datetime.now()
        month = today.month
        day = today.day
        base_filename = f"随机座位结果{month}月{day}日"
        file_index = 1
        filename = f"{base_filename}({file_index}).json"

        # 检查文件是否已存在，递增数字
        while os.path.exists(filename):
            file_index += 1
            filename = f"{base_filename}({file_index}).json"

        with open(filename, 'w') as file:
            json.dump(result, file, indent=4)
        QMessageBox.information(None,"保存成功",f"配置保存为{filename}。",QMessageBox.Ok )
    def load_random_result(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择要加载的结果文件", "", "JSON Files (*.json)")
        if not filename:  # 如果用户取消了对话框
            return
        try:
            with open(filename, 'r') as file:
                result = json.load(file)
                self.group_first = [(name, random_value, self.create_label(name, random_value)) for name, random_value in
                             result['group_first']]
                self.group_second = [(name, random_value, self.create_label(name, random_value)) for name, random_value in
                              result['group_second']]
                self.update_names_layout()

                for seat_info in result['seating_arrangement']:
                    row = seat_info['row']
                    col = seat_info['col']
                    color = seat_info['color']
                    text = seat_info['text']
                    seat = self.seats[row][col]
                    seat.setStyleSheet(f"background-color: {color};")
                    seat.setText(text)
            self.check_seating_balance()
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"No saved result found for today ({filename})")

    def create_label(self, name, random_value):
        label = QLabel(f"{name} {random_value}")
        label.setFont(QFont('Arial', int(16 * self.font_scale)))  # Ensure font size is consistent
        label.setAlignment(Qt.AlignLeft)
        return label

    def check_seating_balance(self):
        boy_count = 0
        girl_count = 0
        for row in self.seats:
            for seat in row:
                seat_color = seat.palette().color(QPalette.Button).name()
                if seat_color == "#add8e6":  # lightblue
                    boy_count += 1
                elif seat_color == "#ffffe0":  # lightyellow
                    girl_count += 1

        total_group_first = len(self.group_first)
        total_group_second = len(self.group_second)

        if boy_count > total_group_first or girl_count > total_group_second:
            self.warning_label.setText("Warning: 当前学生数量少于座位数")
            self.warning_label.setFont(QFont('Arial', int(14 * self.font_scale)))
        elif boy_count < total_group_first or girl_count < total_group_second:
            self.warning_label.setText("Warning: 当前学生数量多于座位数")
            self.warning_label.setFont(QFont('Arial', int(14 * self.font_scale)))
        else:
            self.warning_label.setText("当前学生数量和座位数量相匹配")
            self.warning_label.setFont(QFont('Arial', int(14 * self.font_scale)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SeatingArrangement()
    ex.show()
    ex.check_seating_balance()
    ex.check_first_run()
    sys.exit(app.exec_())
