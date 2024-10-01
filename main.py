# main.py
import sys, os
import random
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, \
    QButtonGroup, QFileDialog, QGroupBox, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QPixmap
from edit_mode import EditMode
from export_to_excel import export_seating_arrangement


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
        self.selected_color = None  # 初始化 selected_color 属性
        self.saved_seating_arrangement = None  # 保存当前座位表状态
        self.initUI()

    def initUI(self):
        self.setWindowTitle('随机座位生成器')
        self.setGeometry(100, 50, 1280, 1000)  # Ensure vertical resolution does not exceed 800

        main_layout = QVBoxLayout()

        # Top part: Names list and seating grid
        top_layout = QHBoxLayout()

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
        self.warning_label.setStyleSheet("background-color: white;")
        self.warning_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.warning_label)

        self.setLayout(main_layout)

        self.load_names()
        self.load_seating_arrangement()

    def check_first_run(self):
        if not os.path.exists("hello_world.txt"):
            with open("hello_world.txt", "w") as f:
                f.write("This is the first run of the program.")
            self.show_image_viewer()  # Show the image viewer on first run

    def show_image_viewer(self):
        self.image_viewer = ImageViewer()
        self.image_viewer.show()

    def load_names(self):
        self.boys = []
        self.girls = []
        self.ignore = []

        with open('students.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()

        current_category = None
        for line in lines:
            line = line.strip()
            if line == '[boys]':
                current_category = 'boys'
            elif line == '[girls]':
                current_category = 'girls'
            elif line == '[ignore]':
                current_category = 'ignore'
            elif line:
                label = QLabel(f"{line} 0.000")
                label.setFont(QFont('Arial', 16))  # Increase font size
                label.setAlignment(Qt.AlignLeft)
                if current_category == 'boys':
                    self.boys.append((line, 0.000, label))
                elif current_category == 'girls':
                    self.girls.append((line, 0.000, label))
                elif current_category == 'ignore':
                    self.ignore.append((line, label))

        self.update_names_layout()

    def save_current_seating_arrangement(self):
        self.saved_seating_arrangement = []
        for row in range(12):
            for col in range(12):
                seat = self.seats[row][col]
                seat_color = seat.palette().color(QPalette.Button).name()
                seat_text = seat.text()
                self.saved_seating_arrangement.append({
                    'row': row,
                    'col': col,
                    'color': seat_color,
                    'text': seat_text
                })

    def restore_seating_arrangement(self):
        try:
            with open('temp_seating_arrangement.json', 'r') as file:
                seating_arrangement = json.load(file)
                for seat_info in seating_arrangement:
                    row = seat_info['row']
                    col = seat_info['col']
                    color = seat_info['color']
                    text = seat_info['text']
                    seat = self.seats[row][col]
                    seat.setStyleSheet(f"background-color: {color};")
                    seat.setText(text)
            os.remove('temp_seating_arrangement.json')  # 删除临时文件
            self.check_seating_balance()
        except FileNotFoundError:
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

        boys_layout = QHBoxLayout()
        girls_layout = QHBoxLayout()
        ignore_layout = QHBoxLayout()

        self.add_names_to_layout(self.boys, boys_layout, 3, True)
        self.add_names_to_layout(self.girls, girls_layout, 3, True)
        self.add_names_to_layout(self.ignore, ignore_layout, 3, False)

        boys_group = QGroupBox("Boys")
        boys_group.setLayout(boys_layout)
        girls_group = QGroupBox("Girls")
        girls_group.setLayout(girls_layout)
        ignore_group = QGroupBox("Ignore")
        ignore_group.setLayout(ignore_layout)

        self.names_layout.addWidget(boys_group)
        self.names_layout.addWidget(girls_group)
        self.names_layout.addSpacing(20)  # Add some space between girls and ignore
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
                number_label.setFont(QFont('Arial', 16))  # 确保字号一致
                number_label.setAlignment(Qt.AlignLeft)
                h_layout.addWidget(number_label)  # 添加序号标签
                label.setText(f"{name.split()[0]} {random_value}")  # 只显示名字和随机值
            else:
                name, label = item
                number_label = QLabel(f"   {i + 1}. ")  # 序号标签，后面加一个空格
                number_label.setFont(QFont('Arial', 16))  # 确保字号一致
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
                seat.setFont(QFont('Arial', 14))
                seat.clicked.connect(self.change_seat_color)
                self.grid_layout.addWidget(seat, row, col)
                row_seats.append(seat)
            self.seats.append(row_seats)

    def export_seating_arrangement(self):
        export_seating_arrangement(self.seats, self.boys, self.girls)  # 调用导出功能

    def enter_edit_mode(self):
        # 保存当前座位表状态到临时文件
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

        with open('temp_seating_arrangement.json', 'w') as file:
            json.dump(seating_arrangement, file, indent=4)

    def create_color_buttons(self):
        self.color_buttons = QButtonGroup(self)
        self.color_buttons.buttonClicked[int].connect(self.set_selected_color)

        self.white_button = QPushButton("空白位置")
        self.white_button.setStyleSheet("background-color: white;")
        self.white_button.setFixedSize(400, 30)
        self.color_buttons.addButton(self.white_button, 0)
        self.color_buttons_layout.addWidget(self.white_button)

        self.lightblue_button = QPushButton("男生位置")
        self.lightblue_button.setStyleSheet("background-color: lightblue;")
        self.lightblue_button.setFixedSize(400, 30)
        self.color_buttons.addButton(self.lightblue_button, 1)
        self.color_buttons_layout.addWidget(self.lightblue_button)

        self.lightyellow_button = QPushButton("女生位置")
        self.lightyellow_button.setStyleSheet("background-color: lightyellow;")
        self.lightyellow_button.setFixedSize(400, 30)
        self.color_buttons.addButton(self.lightyellow_button, 2)
        self.color_buttons_layout.addWidget(self.lightyellow_button)

        self.gray_button = QPushButton("无意义位置")
        self.gray_button.setStyleSheet("background-color: gray;")
        self.color_buttons.addButton(self.gray_button, 3)
        self.color_buttons_layout.addWidget(self.gray_button)

    def create_action_buttons(self):
        button_font = QFont('Arial', 14)

        self.randomize_button = QPushButton("开始随机")
        self.randomize_button.setFont(button_font)
        self.randomize_button.setFixedSize(200, 50)
        self.randomize_button.clicked.connect(self.randomize_seating)
        self.action_buttons_layout.addWidget(self.randomize_button)

        self.save_button = QPushButton("保存当前座位分布表")
        self.save_button.setFont(button_font)
        self.save_button.setFixedSize(200, 50)
        self.save_button.clicked.connect(self.save_seating_arrangement)
        self.action_buttons_layout.addWidget(self.save_button)

        self.project_button = QPushButton("将结果投影到座位表上")
        self.project_button.setFont(button_font)
        self.project_button.setFixedSize(200, 50)
        self.project_button.clicked.connect(self.project_to_seating)
        self.action_buttons_layout.addWidget(self.project_button)

        self.clear_projection_button = QPushButton("清除投影的结果")
        self.clear_projection_button.setFont(button_font)
        self.clear_projection_button.setFixedSize(200, 50)
        self.clear_projection_button.clicked.connect(self.clear_projection)
        self.action_buttons_layout.addWidget(self.clear_projection_button)

        self.save_random_result_button = QPushButton("保存本次随机结果")
        self.save_random_result_button.setFont(button_font)
        self.save_random_result_button.setFixedSize(200, 50)
        self.save_random_result_button.clicked.connect(self.save_random_result)
        self.action_buttons_layout.addWidget(self.save_random_result_button)

        self.load_random_result_button = QPushButton("加载保存的结果")
        self.load_random_result_button.setFont(button_font)
        self.load_random_result_button.setFixedSize(200, 50)
        self.load_random_result_button.clicked.connect(self.load_random_result)
        self.action_buttons_layout.addWidget(self.load_random_result_button)

        self.edit_names_button = QPushButton('编辑名字')
        self.edit_names_button.setFont(button_font)
        self.edit_names_button.setFixedSize(200, 50)
        self.edit_names_button.clicked.connect(self.enter_edit_mode)
        self.action_buttons_layout.addWidget(self.edit_names_button)

        self.export_button = QPushButton("导出座位表到 Excel")
        self.export_button.setFont(button_font)
        self.export_button.setFixedSize(200, 50)
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
        all_students = self.boys + self.girls
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

                # 将赋值结果写回到各自的类别
                self.boys = all_students[:len(self.boys)]
                self.girls = all_students[len(self.boys):]

                # 对男生和女生类别分别进行排序
                for category in [self.boys, self.girls]:
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
                if seat_color == "#add8e6" and boy_index < len(self.boys):  # lightblue
                    name, _, label = self.boys[boy_index]
                    seat.setText(name.split()[0])
                    boy_index += 1
                elif seat_color == "#ffffe0" and girl_index < len(self.girls):  # lightyellow
                    name, _, label = self.girls[girl_index]
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
            'boys': [(name, random_value) for name, random_value, _ in self.boys],
            'girls': [(name, random_value) for name, random_value, _ in self.girls],
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
        QMessageBox.information(None,"保存成功",f"配置保存为：{filename}。",QMessageBox.Ok )
    def load_random_result(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择要加载的结果文件", "", "JSON Files (*.json)")
        if not filename:  # 如果用户取消了对话框
            return
        try:
            with open(filename, 'r') as file:
                result = json.load(file)
                self.boys = [(name, random_value, self.create_label(name, random_value)) for name, random_value in
                             result['boys']]
                self.girls = [(name, random_value, self.create_label(name, random_value)) for name, random_value in
                              result['girls']]
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
        label.setFont(QFont('Arial', 16))  # Ensure font size is consistent
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

        total_boys = len(self.boys)
        total_girls = len(self.girls)

        if boy_count > total_boys or girl_count > total_girls:
            self.warning_label.setText("Warning: 当前学生数量少于座位数")
        elif boy_count < total_boys or girl_count < total_girls:
            self.warning_label.setText("Warning: 当前学生数量多于座位数")
        else:
            self.warning_label.setText("当前学生数量和座位数量相匹配")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SeatingArrangement()
    ex.show()
    ex.check_first_run()
    sys.exit(app.exec_())
