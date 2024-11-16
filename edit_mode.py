import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QPushButton, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
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
class SelectableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont('Arial', int(16 * font_scale)))
        self.setAlignment(Qt.AlignLeft)
        self.setStyleSheet("border: 1px solid black;")
        self.setMargin(5)
        self.setAutoFillBackground(True)
        self.selected = False
        self.setFixedSize(140, 40)
        self.font_scale = font_scale
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected = not self.selected
            self.update_style()

    def update_style(self):
        if self.selected:
            self.setStyleSheet("border: 1px solid black; background-color: lightblue;")
        else:
            self.setStyleSheet("border: 1px solid black;")

class EditMode(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.delete_mode = False  # 新增删除模式标志
        self.font_scale = font_scale
    def initUI(self):
        print("Initializing UI...")  # 调试信息
        self.setWindowTitle('编辑名字(看不到按钮就最大化)')
        self.setGeometry(100, 50, 1480, 870)

        main_layout = QVBoxLayout()
        title_label = QLabel("学生名单编辑器")  # 创建标题标签
        title_label.setFont(QFont('Arial', int(24 * font_scale)))  # 设置字体和大小
        title_label.setAlignment(Qt.AlignCenter)  # 设置文本居中
        help_lable = QLabel("使用方法：  ①点击名字，可以多选"
                            "       ②点击按钮，移动名字"
                            "       ③保存并退出")
        help_lable.setFont(QFont('Arial', int(12 * font_scale)))  # 设置字体和大小
        help_lable.setAlignment(Qt.AlignJustify)  # 设置文本居中
        main_layout.addWidget(title_label)  # 将标题添加到主布局
        main_layout.addWidget(help_lable)
        self.names_layout = QVBoxLayout()
        self.names_container = QWidget()
        self.names_container.setLayout(self.names_layout)
        main_layout.addWidget(self.names_container)

        self.action_buttons_layout = QHBoxLayout()
        self.create_action_buttons()
        main_layout.addLayout(self.action_buttons_layout)

        self.setLayout(main_layout)

        self.load_names()
        print("UI initialized.")  # 调试信息

    def load_names(self):
        print("Loading names...")  # 调试信息
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
                label = SelectableLabel(f"{line} ")
                if current_category == 'group_first':
                    self.group_first.append((line, 0.0, label))
                elif current_category == 'group_second':
                    self.group_second.append((line, 0.0, label))
                elif current_category == 'ignore':
                    self.ignore.append((line, label))

        self.update_names_layout()
        print("Names loaded.")  # 调试信息

    def mousePressEvent(self, event):
        print("Label clicked.")  # 调试信息


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

        group_first_layout = QVBoxLayout()
        group_second_layout = QVBoxLayout()
        ignore_layout = QVBoxLayout()

        self.add_names_to_layout(self.group_first, group_first_layout, 6)
        self.add_names_to_layout(self.group_second, group_second_layout, 6)
        self.add_names_to_layout(self.ignore, ignore_layout, 6)

        group_first_group = QGroupBox("组别一")
        group_first_group.setFont(QFont('Arial', int(14 * font_scale)))
        group_first_group.setLayout(group_first_layout)
        group_second_group = QGroupBox("组别二")
        group_second_group.setFont(QFont('Arial', int(14 * font_scale)))
        group_second_group.setLayout(group_second_layout)
        ignore_group = QGroupBox("忽略")
        ignore_group.setFont(QFont('Arial', int(14 * font_scale)))
        ignore_group.setLayout(ignore_layout)

        self.names_layout.addWidget(group_first_group)
        self.names_layout.addWidget(group_second_group)
        self.names_layout.addSpacing(20)
        self.names_layout.addWidget(ignore_group)

        # 添加输入框用于添加新学生
        self.add_input_field(group_first_layout, 'group_first')
        self.add_input_field(group_second_layout, 'group_second')
        self.add_input_field(ignore_layout, 'ignore')

    def add_input_field(self, layout, category):
        input_field = QLineEdit()
        if category == "group_first":
            category_ch = "组别一"
        elif category == "group_second":
            category_ch = "组别二"
        else:
            category_ch = "忽略"
        input_field.setFont(QFont('Arial', int(14 * font_scale)))
        input_field.setPlaceholderText(f"添加 {category_ch} 名字（输入名字后按enter键入）：")
        input_field.setFixedSize(1000, 40)  # 设置文本框的固定大小（宽1000，高40）
        input_field.returnPressed.connect(lambda: self.add_student(input_field.text(), category))
        layout.addWidget(input_field)

    def add_student(self, name, category):
        if name.strip():
            label = SelectableLabel(f"{name} [选择]")
            if category == 'group_first':
                self.group_first.append((name, 0.0, label))
            elif category == 'group_second':
                self.group_second.append((name, 0.0, label))
            elif category == 'ignore':
                self.ignore.append((name, label))
            self.update_names_layout()  # 刷新列表

    def add_names_to_layout(self, names, layout, columns):
        row_layout = None
        for i, name_tuple in enumerate(names):
            if len(name_tuple) == 3:
                name, _, label = name_tuple
            else:
                name, label = name_tuple
            if i % columns == 0:
                row_layout = QHBoxLayout()
                layout.addLayout(row_layout)
            row_layout.addWidget(label)

            # 添加删除按钮
            delete_button = QPushButton("删除")
            delete_button.setStyleSheet("color: red;")
            delete_button.setFixedSize(50, 40)  # 设置按钮的固定大小（宽50，高40）
            delete_button.clicked.connect(lambda _, name=name: self.delete_student(name))
            row_layout.addWidget(delete_button)

        # 补齐空白标签
        missing_count = columns - (len(names) % columns)  # 计算缺少的数量
        if missing_count < columns:  # 只在当前行不满时添加空白标签
            for _ in range(missing_count):
                empty_label = QLabel("")  # 创建一个空白标签
                empty_label.setFixedSize(200, 40)  # 设置空白标签的固定大小（宽50，高40）
                empty_label.setEnabled(False)  # 禁用按钮
                row_layout.addWidget(empty_label)

    def create_action_buttons(self):
        button_font = QFont('Arial', int(14 * font_scale))

        self.save_and_exit_edit_button = QPushButton('保存并退出')
        self.save_and_exit_edit_button.setFont(button_font)
        self.save_and_exit_edit_button.setFixedSize(200, 50)
        self.save_and_exit_edit_button.clicked.connect(self.confirm_save_and_exit)
        self.action_buttons_layout.addWidget(self.save_and_exit_edit_button)

        self.discard_changes_button = QPushButton('不保存更改并退出')
        self.discard_changes_button.setFont(button_font)
        self.discard_changes_button.setFixedSize(200, 50)
        self.discard_changes_button.clicked.connect(self.not_save_and_exit_edit_mode)  # 直接关闭
        self.action_buttons_layout.addWidget(self.discard_changes_button)

        self.move_to_group_first_button = QPushButton('移动到组别一')
        self.move_to_group_first_button.setFont(button_font)
        self.move_to_group_first_button.setFixedSize(200, 50)
        self.move_to_group_first_button.clicked.connect(lambda: self.move_selected_to('group_first'))
        self.action_buttons_layout.addWidget(self.move_to_group_first_button)

        self.move_to_group_second_button = QPushButton('移动到组别二')
        self.move_to_group_second_button.setFont(button_font)
        self.move_to_group_second_button.setFixedSize(200, 50)
        self.move_to_group_second_button.clicked.connect(lambda: self.move_selected_to('group_second'))
        self.action_buttons_layout.addWidget(self.move_to_group_second_button)

        self.move_to_ignore_button = QPushButton('移动到忽略')
        self.move_to_ignore_button.setFont(button_font)
        self.move_to_ignore_button.setFixedSize(200, 50)
        self.move_to_ignore_button.clicked.connect(lambda: self.move_selected_to('ignore'))
        self.action_buttons_layout.addWidget(self.move_to_ignore_button)

    def confirm_save_and_exit(self):
        reply = QMessageBox.question(self, '确认', '您确定要保存更改并退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save_and_exit_edit_mode()

    def delete_student(self, name):
        # 从各个类别中删除学生
        self.group_first = [item for item in self.group_first if item[0] != name]
        self.group_second = [item for item in self.group_second if item[0] != name]
        self.ignore = [item for item in self.ignore if item[0] != name]
        self.update_names_layout()  # 刷新列表

    def move_selected_to(self, category):
        selected_labels = [label for label in self.findChildren(SelectableLabel, options=Qt.FindChildrenRecursively) if label.selected]
        if not selected_labels:
            QMessageBox.warning(self, "警告", "请先选择一个名字")
            return

        for label in selected_labels:
            text = label.text().split()[0]
            if category == 'group_first':
                self.group_first.append((text, 0.000, label))
                self.remove_from_other_categories(text, 'group_first')
            elif category == 'group_second':
                self.group_second.append((text, 0.000, label))
                self.remove_from_other_categories(text, 'group_second')
            elif category == 'ignore':
                self.ignore.append((text, label))
                self.remove_from_other_categories(text, 'ignore')
            label.setParent(None)
            label.selected = False
            label.update_style()
        self.update_names_layout()

    def remove_from_other_categories(self, name, category):
        if category != 'group_first':
            self.group_first = [item for item in self.group_first if item[0] != name]
        if category != 'group_second':
            self.group_second = [item for item in self.group_second if item[0] != name]
        if category != 'ignore':
            self.ignore = [item for item in self.ignore if item[0] != name]

    def save_and_exit_edit_mode(self):
        self.save_names_to_file()
        if self.parent():
            self.parent().load_names()
            self.parent().create_color_buttons()  # 重新创建颜色选择按钮
            self.parent().create_action_buttons()  # 重新创建操作按钮
            self.parent().create_seating_grid()  # 重新创建座位表
            self.parent().restore_seating_arrangement(False)  # 恢复座位表状态
            self.parent().check_seating_balance()
        self.close()

    def not_save_and_exit_edit_mode(self):
        if self.parent():
            self.parent().load_names()
            self.parent().create_color_buttons()  # 重新创建颜色选择按钮
            self.parent().create_action_buttons()  # 重新创建操作按钮
            self.parent().create_seating_grid()  # 重新创建座位表
            self.parent().restore_seating_arrangement(True)  # 恢复座位表状态
            self.parent().check_seating_balance()
        self.close()

    def save_names_to_file(self):
        with open('students.txt', 'w', encoding='utf-8') as file:
            file.write('[group_first]\n')
            for name, _, _ in self.group_first:
                file.write(f"{name}\n")
            file.write('[group_second]\n')
            for name, _, _ in self.group_second:
                file.write(f"{name}\n")
            file.write('[ignore]\n')
            for name, _ in self.ignore:
                file.write(f"{name}\n")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EditMode()
    ex.show()
    sys.exit(app.exec_())