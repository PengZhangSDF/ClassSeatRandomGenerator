# main.py
import time
from pre_loading.pre_loading import LoadingDialog
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit
import sys
from utils.get_font import font_scale
from utils.get_yaml_value import adjust_font_scale_add

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

        self.prev_button.clicked.connect(self.show_prev_image) # noqa
        self.next_button.clicked.connect(self.show_next_image) # noqa

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
        self.randomization_window = None  # 用于存储随机过程窗口
        self.edit_mode_window = None
        self.selected_color = None  # 初始化 selected_color 属性
        self.saved_seating_arrangement = None  # 保存当前座位表状态
        self.font_scale = font_scale  # 字体大小倍数
        self.current_font = (self.font_scale + self.get_current_value()) # 当前字体大小
        self.is_in_swap_mode = False  # 添加状态标志
        self.start = False
        self.random = True
        self.random_time = 0

        self.small_point = small_point
        self.auto_project = auto_project
        self.regulatory_taskkill = regulatory_taskkill
        self.randomization_window_show = randomization_window_show
        self.current_random_speed = current_random_speed
        self.initUI()
        # # 设置窗口始终在最上面
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        # # 取消窗口始终在最上面的设置
        # self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
    def showEvent(self, event):
        # 在窗口显示时调整大小到最小可缩小的尺寸
        self.adjustSize()  # 调整窗口大小
        super().showEvent(event)  # 调用父类的 showEvent
    def regularly_get(self):
            self.current_font = (self.font_scale + self.get_current_value())
    def initUI(self):

        self.setWindowTitle('随机座位生成器')
        print(f"当前缩放倍率{self.font_scale}")
        if self.font_scale<0.77:
            self.setGeometry(100, 0, 1280, 1000)  # Ensure vertical resolution does not exceed 800
        else:
            self.setGeometry(100, 20, 1280, 1000)  # Ensure vertical resolution does not exceed 800

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
        self.update_text_box()

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
        print("进入全屏模式")
        self.fullscreen_window = QWidget()
        self.fullscreen_window.setWindowTitle("全屏展示座位表")
        self.fullscreen_window.setGeometry(0, 0, 1920, 1080)  # Set to fullscreen size
        layout = QVBoxLayout()

        title_label = QLabel("全屏座位安排:临时互换模式已开启\n  前方")
        font = QFont('Arial', int(28 * self.font_scale))
        font.setBold(True)  # 设置字体为粗体
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        layout.addWidget(title_label)  # 将标题添加到布局

        # Create a scaled seating grid
        scaled_grid = QGridLayout()
        self.temp_swap_positions = SwapPositions(self)  # 创建临时交换位置实例
        self.temp_swap_positions.exit_mode = False

        self.scaled_seats = []  # 用于存储全屏模式下的座位按钮

        for row in range(12):
            for col in range(12):
                seat = self.seats[row][col]
                scaled_seat = QPushButton(seat.text())
                scaled_seat.setFixedSize(145, 60)  # Scale size by 1.5
                scaled_seat.setStyleSheet(seat.styleSheet())  # Keep the same style
                font = QFont('Arial', int(27 * self.font_scale))
                font.setBold(True)  # 设置字体为粗体
                scaled_seat.setFont(font)
                scaled_seat.setProperty("original_color", seat.palette().color(QPalette.Button).name())  # 保存原始颜色
                scaled_seat.clicked.connect(lambda _, s=scaled_seat: self.temp_swap_positions.select_seat(s))  # 连接临时交换位置 # noqa
                scaled_grid.addWidget(scaled_seat, row, col)
                self.scaled_seats.append(scaled_seat)  # 添加到列表中

        layout.addLayout(scaled_grid)

        # Exit fullscreen button
        exit_button = QPushButton("退出全屏展示")
        exit_button.setFixedHeight(100)
        exit_button.setFont(QFont('Arial', int(28 * self.font_scale)))
        exit_button.clicked.connect(self.exit_fullscreen_mode) # noqa
        layout.addWidget(exit_button)
        layout.addStretch(1)

        self.fullscreen_window.setLayout(layout)
        self.fullscreen_window.show()


    def exit_fullscreen_mode(self):
        self.temp_swap_positions.exit_swap_mode()  # 退出临时交换模式
        for seat in self.scaled_seats:
            seat.setStyleSheet("")  # 清除样式
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
                label.setFont(QFont('Arial', int(16 * self.current_font)))  # Increase font size
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

    def restore_seating_arrangement(self, IFreload):
        try:
            with open('temp_seating_arrangement.json', 'r') as file:
                result = json.load(file)
                if IFreload:
                    self.group_first = [(name, random_value, self.create_label(name, random_value)) for
                                        name, random_value in
                                        result['group_first']]
                    self.group_second = [(name, random_value, self.create_label(name, random_value)) for
                                         name, random_value in
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

                    # 设置字体并加粗
                    font = QFont('Arial', int(14 * self.current_font))  # 设置字体
                    font.setBold(True)  # 加粗字体
                    seat.setFont(font)

            self.check_seating_balance()
            self.auto_project = get_yaml_value("auto_project")
            self.regulatory_taskkill = get_yaml_value("regulatory_taskkill")
            self.small_point = get_yaml_value("small_point")
            self.randomization_window_show = get_yaml_value("randomization_window_show")
            self.current_random_speed = get_yaml_value("current_random_speed")
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

        # 设置姓名布局的边距和间距
        self.names_layout.setContentsMargins(0, 0, 0, 0)  # 上、左、下、右边距均为0
        self.names_layout.setSpacing(0)  # 控件之间的间距为2像素

        group_first_layout = QHBoxLayout()
        group_second_layout = QHBoxLayout()
        ignore_layout = QHBoxLayout()

        self.add_names_to_layout(self.group_first, group_first_layout, 3, True)
        self.add_names_to_layout(self.group_second, group_second_layout, 3, True)
        self.add_names_to_layout(self.ignore, ignore_layout, 3, False)

        group_first_group = QGroupBox("组别一")
        group_first_group.setFont(QFont('Arial', int(14 * self.font_scale)))
        group_first_group.setLayout(group_first_layout)
        group_second_group = QGroupBox("组别二")
        group_second_group.setFont(QFont('Arial', int(14 * self.font_scale)))
        group_second_group.setLayout(group_second_layout)
        ignore_group = QGroupBox("忽略（不排入位置）")
        ignore_group.setFont(QFont('Arial', int(14 * self.font_scale)))
        ignore_group.setLayout(ignore_layout)

        self.names_layout.addWidget(group_first_group)
        self.names_layout.addWidget(group_second_group)
        self.names_layout.addSpacing(0)  # Add some space between group_second and ignore
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
                font = QFont('Arial', int(16 * self.font_scale))
                font.setBold(True)  # 设置字体为粗体
                number_label.setFont(font)
                number_label.setAlignment(Qt.AlignLeft)
                h_layout.addWidget(number_label)  # 添加序号标签
                label.setText(f"{name.split()[0]} {random_value}")  # 只显示名字和随机值
            else:
                name, label = item
                number_label = QLabel(f"   {i + 1}. ")  # 序号标签，后面加一个空格
                font = QFont('Arial', int(16 * self.font_scale))
                font.setBold(True)  # 设置字体为粗体
                number_label.setFont(font)
                number_label.setAlignment(Qt.AlignLeft)
                h_layout.addWidget(number_label)  # 添加序号标签
                label.setText(f"{name.split()[0]}")  # 只显示名字

            # 设置姓名标签的字体
            name_font = QFont('Arial', int(16 * self.current_font))
            name_font.setBold(True)  # 如果需要加粗
            label.setFont(name_font)

            # 设置姓名标签的固定高度
            label.setFixedHeight(20)  # 行间距固定为20
            h_layout.addWidget(label)  # 添加姓名标签到水平布局

            column_layouts[col].addLayout(h_layout)  # 将水平布局添加到对应的列布局

        # 在最后一列的最后一个名字后添加编辑按钮
        if total_count > 0:
            last_col = (total_count - 1) // max_items_per_column
            edit_button = QPushButton("编辑姓名")
            edit_button.setFixedHeight(30)  # 设置按钮高度与标签相同
            edit_button.setFont(QFont('Arial', int(16 * self.font_scale)))  # 确保字号一致
            edit_button.setIcon(QIcon("./img/edit_name.png"))  # 设置图标
            edit_button.setIconSize(
                QSize(int(24 * self.font_scale), int(24 * self.font_scale)))  # 设置图标大小
            edit_button.clicked.connect(self.enter_edit_mode) # noqa

            # 创建一个水平布局来对齐按钮
            button_layout = QHBoxLayout()
            button_layout.setSpacing(3)
            button_layout.addWidget(edit_button)

            column_layouts[last_col].addLayout(button_layout)  # 将按钮布局添加到最后一列

        for column_layout in column_layouts:
            layout.addLayout(column_layout)  # 将每列布局添加到主布局

    def create_seating_grid(self):
        self.seats = []
        self.boy_count = 1
        self.girl_count = 1
        self.grid_layout.setContentsMargins(0, 0, 0, 0)  # 上、左、下、右边距均为0
        self.grid_layout.setSpacing(5)  # 控件之间的间距为0
        for row in range(12):
            row_seats = []
            for col in range(12):
                seat = QPushButton()
                seat.setFixedSize(80, 40)
                seat.setStyleSheet("background-color: white;")
                seat.setFont(QFont('Arial', int(14 * self.font_scale)))
                seat.clicked.connect(self.change_seat_color)  # noqa
                self.grid_layout.addWidget(seat, row, col)
                row_seats.append(seat)
            self.seats.append(row_seats)

        # 在座位表下方添加控件
        self.add_controls_below_grid()

    def add_controls_below_grid(self):
        # 创建一个水平布局用于控件
        controls_layout = QHBoxLayout()
        # 创建第一个按钮
        self.button1 = QPushButton("+字体放大+")
        self.button1.setFixedSize(200, 30)
        controls_layout.addWidget(self.button1)
        self.button1.clicked.connect(lambda: self.update_font_scale('add'))  # 连接按钮点击事件

        # 创建文本框
        self.text_box = QLineEdit()
        self.text_box.setReadOnly(True)  # 设置为只读
        self.text_box.setFixedSize(150, 30)
        controls_layout.addWidget(self.text_box)

        # 创建第二个按钮
        self.button2 = QPushButton("-字体缩小-")
        self.button2.setFixedSize(200, 30)
        controls_layout.addWidget(self.button2)
        self.button2.clicked.connect(lambda: self.update_font_scale('subtract'))  # 连接按钮点击事件

        if self.font_scale < 0.78:
            # 创建关闭程序按钮
            self.close_button = QPushButton("关闭程序")
            self.close_button.setFixedSize(100, 30)
            self.close_button.setStyleSheet("background-color: red; color: white;")  # 设置按钮为红色
            controls_layout.addWidget(self.close_button)
            self.close_button.clicked.connect(self.close_application)  # 连接关闭程序的事件

            # 创建最小化按钮
            self.minimize_button = QPushButton("最小化")
            self.minimize_button.setFixedSize(100, 30)
            self.minimize_button.setStyleSheet("background-color: white; color: red;")  # 设置按钮为红色
            controls_layout.addWidget(self.minimize_button)
            self.minimize_button.clicked.connect(self.showMinimized)  # 连接最小化事件

            # 创建最大化按钮
            self.maximize_button = QPushButton("最大化")
            self.maximize_button.setFixedSize(100, 30)
            self.maximize_button.setStyleSheet("background-color: white; color: red;")  # 设置按钮为红色
            controls_layout.addWidget(self.maximize_button)
            self.maximize_button.clicked.connect(self.showMaximized)  # 连接最大化事件

        # 将控件布局添加到主布局
        self.grid_layout.addLayout(controls_layout, 12, 0, 1, 12)  # 假设 grid_layout 是 QGridLayout

    def close_application(self):
        # 关闭程序
        QApplication.quit()  # 退出应用程序

    def update_font_scale(self, operation):
        new_value = adjust_font_scale_add(operation)
        self.update_text_box(new_value)
        self.regularly_get()
    def update_text_box(self, value=None):
        if value is None:
            import yaml
            with open('config.yaml', 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                value = data.get('font_scale_add', 0)
        self.text_box.setText(f"当前字体倍数: {value:.2f}")
        self.refresh_ui()


    def refresh_ui(self):
        if self.start:
            file_name = self.save_random_result(False)
            self.load_random_result(file_name=file_name)
            if os.path.exists(file_name):
                os.remove(file_name)  # 删除文件
        self.start = True

    def export_seating_arrangement(self):
        loading_dialog = LoadingDialog()
        loading_dialog.add_msg = 'Excel'
        loading_dialog.show()
        from function.export_to_excel import export_seating_arrangement
        loading_dialog.close()
        export_seating_arrangement(self.seats, self.group_first, self.group_second)  # 调用导出功能

    def enter_edit_mode(self):
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

    def open_settings(self):
        # 保存当前界面状态到临时文件
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

        # 创建并显示设置窗口
        from function.setting import SettingsWindow
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

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

    def enter_swap_mode(self):
        print("进入交换模式")
        self.is_in_swap_mode = True  # 设置状态标志
        self.swap_positions = SwapPositions(self)  # 创建交换位置实例
        self.swap_positions.exit_mode = False
        for row in self.seats:
            for seat in row:
                seat.setProperty("original_color", seat.palette().color(QPalette.Button).name())  # 保存原始颜色
                seat.clicked.disconnect()  # 先断开之前的连接 # noqa
                seat.clicked.connect(lambda _, s=seat: self.swap_positions.select_seat(s))  # 连接座位点击事件 # noqa

    def create_color_buttons(self):
        self.color_buttons = QButtonGroup(self)
        self.color_buttons.setExclusive(True)  # 设置为互斥模式
        self.color_buttons.buttonClicked[int].connect(self.set_selected_color)

        # 创建 QLabel 用于显示当前选择的按钮类型
        self.selected_color_label = QLabel("点击颜色按钮以更换座位类型")
        self.selected_color_label.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.color_buttons_layout.addWidget(self.selected_color_label)  # 将标签添加到布局中

        # 创建按钮并设置为可选中
        self.white_button = QPushButton("空白位置")
        self.white_button.setCheckable(True)
        self.white_button.setStyleSheet("background-color: white;")
        self.white_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.white_button.setFixedHeight(30)
        self.color_buttons.addButton(self.white_button, 0)
        self.color_buttons_layout.addWidget(self.white_button)

        self.lightblue_button = QPushButton("组别一位置")
        self.lightblue_button.setCheckable(True)
        self.lightblue_button.setStyleSheet("background-color: lightblue;")
        self.lightblue_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.lightblue_button.setFixedHeight(30)
        self.color_buttons.addButton(self.lightblue_button, 1)
        self.color_buttons_layout.addWidget(self.lightblue_button)

        self.lightyellow_button = QPushButton("组别二位置")
        self.lightyellow_button.setCheckable(True)
        self.lightyellow_button.setStyleSheet("background-color: lightyellow;")
        self.lightyellow_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.lightyellow_button.setFixedHeight(30)
        self.color_buttons.addButton(self.lightyellow_button, 2)
        self.color_buttons_layout.addWidget(self.lightyellow_button)

        self.gray_button = QPushButton("无意义位置")
        self.gray_button.setCheckable(True)
        self.gray_button.setStyleSheet("background-color: gray;")
        self.gray_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.gray_button.setFixedHeight(30)
        self.color_buttons.addButton(self.gray_button, 3)
        self.color_buttons_layout.addWidget(self.gray_button)

        self.swap_button = QPushButton("交换位置")
        self.swap_button.setCheckable(True)
        self.swap_button.setStyleSheet("background-color: yellow;")
        self.swap_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.swap_button.setFixedHeight(30)
        self.swap_button.clicked.connect(self.enter_swap_mode)  # 连接到进入交换模式的函数 # noqa
        self.color_buttons.addButton(self.swap_button, 4)
        self.color_buttons_layout.addWidget(self.swap_button)

        # 连接按钮点击事件
        self.white_button.clicked.connect(self.on_color_button_clicked) # noqa
        self.lightblue_button.clicked.connect(self.on_color_button_clicked) # noqa
        self.lightyellow_button.clicked.connect(self.on_color_button_clicked) # noqa
        self.gray_button.clicked.connect(self.on_color_button_clicked) # noqa
        self.swap_button.clicked.connect(self.swap_button_lable) # noqa
    def swap_button_lable(self):
        self.selected_color_label.setStyleSheet("color: red;")  # 设置文本颜色为红色
        self.selected_color_label.setText(f"注意：您正处于交换模式中！")

    def on_color_button_clicked(self):
        if self.is_in_swap_mode:
            self.swap_positions.exit_swap_mode()  # 退出交换模式
            self.is_in_swap_mode = False  # 重置状态标志
        # 获取被点击的按钮
        clicked_button = self.sender()
        self.selected_color_label.setStyleSheet("color: black;")
        # 更新 QLabel 显示当前选择的按钮类型
        self.selected_color_label.setText(f"当前选择: {clicked_button.text()}")



    def create_action_buttons(self):
        button_font = QFont('Arial', int(14 * self.font_scale))
        action_buttons_layout = QGridLayout()  # 使用网格布局

        # 创建“开始随机”按钮
        self.randomize_button = QPushButton("开始随机")
        self.randomize_button.setIcon(QIcon("./img/random.png"))  # 设置图标
        self.randomize_button.setIconSize(QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.randomize_button.setFont(button_font)
        self.randomize_button.setFixedHeight(50)
        self.randomize_button.clicked.connect(self.randomize_seating) # noqa
        action_buttons_layout.addWidget(self.randomize_button, 0, 0)  # 第一行第一列

        # 创建“投影结果到座位表”按钮
        self.project_button = QPushButton("投影结果到座位表")
        self.project_button.setIcon(QIcon("./img/project.png"))  # 设置图标
        self.project_button.setIconSize(QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.project_button.setFont(button_font)
        self.project_button.setFixedHeight(50)
        self.project_button.clicked.connect(self.project_to_seating) # noqa
        action_buttons_layout.addWidget(self.project_button, 0, 1)  # 第一行第二列

        # 创建“清除投影的结果”按钮
        self.clear_projection_button = QPushButton("清除投影的结果")
        self.clear_projection_button.setIcon(QIcon("./img/clear.png"))  # 设置图标
        self.clear_projection_button.setIconSize(QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.clear_projection_button.setFont(button_font)
        self.clear_projection_button.setFixedHeight(50)
        self.clear_projection_button.clicked.connect(self.clear_projection) # noqa
        action_buttons_layout.addWidget(self.clear_projection_button, 0, 2)  # 第一行第三列

        self.fullscreen_button = QPushButton("全屏展示当前座位表")
        self.fullscreen_button.setStyleSheet("background-color: orange;")
        self.fullscreen_button.setIcon(QIcon("./img/expand.png"))  # 设置图标
        self.fullscreen_button.setIconSize(
            QSize(int(18 * self.font_scale), int(18 * self.font_scale)))  # 设置图标大小
        self.fullscreen_button.setFont(QFont('Arial', int(14 * self.font_scale)))  # 使用字体倍数
        self.fullscreen_button.setFixedHeight(50)
        self.fullscreen_button.clicked.connect(self.enter_fullscreen_mode) # noqa
        self.color_buttons.addButton(self.fullscreen_button, 4)
        action_buttons_layout.addWidget(self.fullscreen_button,0,4)

        # 创建“设置”按钮
        self.settings_button = QPushButton("设置")
        self.settings_button.setIcon(QIcon("./img/setting.png"))  # 设置图标
        self.settings_button.setIconSize(QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.settings_button.setFont(button_font)
        self.settings_button.setFixedHeight(50)  # 缩小按钮高度
        self.settings_button.setFixedWidth(140)  # 设置按钮宽度
        self.settings_button.clicked.connect(self.open_settings)  # noqa # 连接设置功能
        action_buttons_layout.addWidget(self.settings_button, 0, 5)  # 第一行第四列

        # 创建“保存本次随机结果”按钮
        self.save_random_result_button = QPushButton("保存结果")
        self.save_random_result_button.setIcon(QIcon("./img/save.png"))  # 设置图标
        self.save_random_result_button.setIconSize(
            QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.save_random_result_button.setFont(button_font)
        self.save_random_result_button.setFixedWidth(140)  # 设置按钮宽度
        self.save_random_result_button.setFixedHeight(50)  # 缩小按钮高度
        self.save_random_result_button.clicked.connect(lambda: self.save_random_result(information=True)) # noqa
        action_buttons_layout.addWidget(self.save_random_result_button, 0, 6)  # 第一行第五列

        # 创建“加载保存的结果”按钮
        self.load_random_result_button = QPushButton("加载结果")
        self.load_random_result_button.setIcon(QIcon("./img/load.png"))  # 设置图标
        self.load_random_result_button.setIconSize(
            QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.load_random_result_button.setFont(button_font)
        self.load_random_result_button.setFixedWidth(140)  # 设置按钮宽度
        self.load_random_result_button.setFixedHeight(50)  # 缩小按钮高度
        self.load_random_result_button.clicked.connect(self.load_random_result) # noqa
        action_buttons_layout.addWidget(self.load_random_result_button, 0, 7)  # 第二行第一列

        # 创建“导出座位表到 Excel”按钮
        self.export_button = QPushButton("导出Excel")
        self.export_button.setIcon(QIcon("./img/excel.png"))  # 设置图标
        self.export_button.setIconSize(QSize(int(32 * self.font_scale), int(32 * self.font_scale)))  # 设置图标大小
        self.export_button.setFont(button_font)
        self.export_button.setFixedHeight(50)  # 缩小按钮高度
        self.export_button.setFixedWidth(140)  # 设置按钮宽度
        self.export_button.clicked.connect(self.export_seating_arrangement)  # 连接导出功能 # noqa
        action_buttons_layout.addWidget(self.export_button, 0, 8)  # 第二行第二列
        # 将按钮布局添加到主布局中
        self.action_buttons_layout.addLayout(action_buttons_layout)  # 只传递布局


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
        # 禁用所有按钮
        self.set_buttons_enabled(False)
        add = 17
        # 获取右侧座位表的位置和大小
        seat_table_geometry = self.grid_layout.geometry()  # 获取座位表的几何信息
        global_position = self.mapToGlobal(seat_table_geometry.topLeft())  # 转换为全局坐标

        # 计算右侧座位表的几何信息
        right_seat_table_geometry = QRect(global_position.x() + self.names_container.width() + add,
                                          global_position.y(),
                                          seat_table_geometry.width(),
                                          seat_table_geometry.height())
        self.first_random = False

        # 创建随机过程窗口，设置为覆盖右侧座位表
        if self.randomization_window_show:
            self.randomization_window = RandomizationWindow(self, right_seat_table_geometry,
                                                            self.current_font, self.small_point)  # 使用 QRect 设置窗口位置和大小
            self.randomization_window.show()  # 显示窗口

        all_students = self.group_first + self.group_second
        current_index = 0

        # 初始化学生信息列表，并将所有随机值设置为0
        student_info = [(name, 0) for name, _, _ in all_students]  # 初始随机值为0

        # 刷新界面标签，确保显示为0
        for i, (name, _) in enumerate(student_info):
            label = all_students[i][2]  # 获取原界面标签
            label.setText(f"{name} {0:.{self.small_point}f}")  # 更新原界面标签文本为0

        def assign_next_value():
            nonlocal current_index
            if current_index < len(all_students):
                try:
                    name, _, label = all_students[current_index]
                    random_value = round(random.uniform(0, 1), self.small_point)  # 生成随机数，保留小数
                    student_info[current_index] = (name, random_value)  # 更新学生信息
                    label.setText(f"{name} {random_value:.{self.small_point}f}")  # 更新原界面标签文本

                    # 更新随机窗口显示
                    if self.randomization_window_show:
                        try:
                            # 这里确保传递的是最新的 group_first 和 group_second
                            self.randomization_window.update_display(student_info[:len(self.group_first)],
                                                                     student_info[len(self.group_first):],
                                                                     current_index)
                        except Exception as e:
                            print(f"Error during update_display: {e}")

                        # 实时更新随机窗口的位置
                        right_seat_table_geometry.moveTopLeft(
                            self.mapToGlobal(seat_table_geometry.topLeft()) + QPoint(self.names_container.width() + add,
                                                                                     0))
                        self.randomization_window.setGeometry(right_seat_table_geometry)  # 更新窗口位置

                        # 实时更新窗口透明度
                        if 1 < current_index < 11 and self.randomization_window.windowOpacity() < 0.9:
                            new_opacity = min(1, self.randomization_window.windowOpacity() + 0.1)  # 增加透明度
                        elif current_index == 1:
                            new_opacity = 0
                        elif current_index > len(self.group_first) + len(self.group_second) - 10:
                            new_opacity = max(0, self.randomization_window.windowOpacity() - 0.1)  # 减小透明度
                        else:
                            new_opacity = 1
                        self.randomization_window.setWindowOpacity(new_opacity)  # 设置新的透明度

                    current_index += 1
                    # 使用 QTimer.singleShot 来设置下一个调用
                    QTimer.singleShot(max(self.current_random_speed, 10), assign_next_value)  # 设定下次调用的时间
                except Exception as e:
                    print(f"Error during assignment: {e}")
                    current_index += 1  # 跳过当前索引，继续下一次循环
                    # 继续调用下一个
                    QTimer.singleShot(max(self.current_random_speed, 10), assign_next_value)

            else:
                # 所有学生都已赋值，停止计时器
                print("完成停止计时器")
                if self.randomization_window_show:
                    self.randomization_window.close()  # 关闭随机过程窗口

                # 将赋值结果写回到各自的类别
                self.group_first = student_info[:len(self.group_first)]
                self.group_second = student_info[len(self.group_first):]

                # 对男生和女生类别分别进行排序
                for category in [self.group_first, self.group_second]:
                    category.sort(key=lambda x: x[1])  # 按随机值排序

                # 更新主界面上的标签
                try:
                    for i, (name, random_value) in enumerate(self.group_first):
                        self.group_first[i] = (name, random_value, self.create_label(name, random_value))
                    for i, (name, random_value) in enumerate(self.group_second):
                        self.group_second[i] = (name, random_value, self.create_label(name, random_value))
                except Exception as e:
                    print(f"随机过程指针越界: {e}")

                # 更新布局
                self.update_names_layout()
                if self.auto_project:
                    self.project_to_seating()
                self.set_buttons_enabled(True)

        # 启动第一次调用
        assign_next_value()

    # def start_timer(self):
    #     self.timer = QTimer()
    #     self.timer.setSingleShot(True)  # 设为单次触发
    #     self.timer.timeout.connect(self.safe_assign)
    #     self.timer.start(self.current_random_speed)
    #
    # def safe_assign(self):
    #     try:
    #         self.assign_next_value()
    #     finally:
    #         # 处理完成后重新启动
    #         self.timer.start(self.current_random_speed)

    def set_buttons_enabled(self, enabled):
        """启用或禁用所有按钮"""
        # 禁用/启用所有按钮
        for button in self.findChildren(QPushButton):
            button.setEnabled(enabled)

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
                    font = QFont('Arial', int(14 * self.current_font))  # 设置字体
                    font.setBold(True)  # 加粗字体
                    seat.setFont(font)
                    boy_index += 1
                elif seat_color == "#ffffe0" and girl_index < len(self.group_second):  # lightyellow
                    name, _, label = self.group_second[girl_index]
                    seat.setText(name.split()[0])
                    font = QFont('Arial', int(14 * self.current_font))  # 设置字体
                    font.setBold(True)  # 加粗字体
                    seat.setFont(font)
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

                    # 设置字体并加粗
                    font = QFont('Arial', int(14 * self.current_font))  # 设置字体
                    font.setBold(True)  # 加粗字体
                    seat.setFont(font)

            self.check_seating_balance()
        except FileNotFoundError:
            pass

    def save_random_result(self, information=True):
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
        if information:
            QMessageBox.information(None,"保存成功",f"配置保存为{filename}。",QMessageBox.Ok )
        return filename
    def get_current_value(self):
        import yaml
        with open('config.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            value = data.get('font_scale_add', 0)
            return value

    def load_random_result(self, file_name=None):
        if not file_name:
            filename, _ = QFileDialog.getOpenFileName(self, "选择要加载的结果文件", "", "JSON Files (*.json)")
            if not filename:  # 如果用户取消了对话框
                return
        else:
            filename = file_name
        try:
            with open(filename, 'r') as file:
                result = json.load(file)
                self.group_first = [(name, random_value, self.create_label(name, random_value)) for name, random_value
                                    in result['group_first']]
                self.group_second = [(name, random_value, self.create_label(name, random_value)) for name, random_value
                                     in result['group_second']]
                self.update_names_layout()

                for seat_info in result['seating_arrangement']:
                    row = seat_info['row']
                    col = seat_info['col']
                    color = seat_info['color']
                    text = seat_info['text']
                    seat = self.seats[row][col]
                    seat.setStyleSheet(f"background-color: {color};")
                    seat.setText(text)

                    # 设置字体并加粗
                    now_font = int(14 * (self.font_scale + self.get_current_value()))
                    font = QFont('Arial', now_font)  # 设置字体
                    font.setBold(True)  # 加粗字体
                    seat.setFont(font)

                    # 如果座位文本是数字（序号），也要加粗
                    if text.isdigit():  # 检查文本是否为数字
                        seat.setText(f"{text}")  # 确保文本是数字
                        seat.setFont(font)  # 设置加粗字体

                # 加粗列表中的名字
                for name, random_value, label in self.group_first:
                    label.setFont(QFont('Arial', now_font, QFont.Bold))  # 加粗字体
                for name, random_value, label in self.group_second:
                    label.setFont(QFont('Arial', now_font, QFont.Bold))  # 加粗字体
                for name, label in self.ignore:
                    label.setFont(QFont('Arial', now_font, QFont.Bold))  # 加粗字体

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
def load_heavy_modules():
    # 延迟导入
    from function.edit_mode import EditMode
    from utils.get_yaml_value import get_yaml_value
    from function.swap_position import SwapPositions
    global EditMode, get_yaml_value, kill_process, SwapPositions

if __name__ == '__main__':

    time_start = time.time()
    import threading
    from utils.setting_utils import kill_process
    thread_load = threading.Thread(target=load_heavy_modules)
    thread_load.start()
    thread = threading.Thread(target=kill_process,args=("SeewoAbility.exe",))
    thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
    thread.start()
    app = QApplication(sys.argv)
    loading_dialog = LoadingDialog()
    thread_load.join()
    loading_dialog.show()
    from function.random_large import RandomizationWindow
    from PyQt5.QtWidgets import QHBoxLayout, QPushButton,QGridLayout, \
        QButtonGroup, QFileDialog, QGroupBox, QMessageBox
    from PyQt5.QtCore import Qt, QTimer, QSize, QRect, QPoint, QTime
    from PyQt5.QtGui import QFont, QPalette, QPixmap, QIcon
    import sys
    import random
    import json
    from datetime import datetime
    import os

    auto_project = get_yaml_value("auto_project")
    regulatory_taskkill = get_yaml_value("regulatory_taskkill")
    small_point = get_yaml_value("small_point")
    current_random_speed = get_yaml_value("current_random_speed")
    randomization_window_show = get_yaml_value("randomization_window_show")
    ex = SeatingArrangement()
    ex.show()
    ex.raise_()  # 将窗口提升到最上层
    ex.activateWindow()  # 激活窗口并将其置于前面
    ex.check_seating_balance()
    ex.check_first_run()
    loading_dialog.close()  # 关闭加载对话框
    time_end = time.time()
    print(time_end - time_start)
    sys.exit(app.exec_())

