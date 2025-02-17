import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QPushButton, \
    QMessageBox, QLineEdit, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.get_font import font_scale



class SelectableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        font = QFont('Arial', int(16 * font_scale))
        font.setBold(True)  # 加粗字体
        self.setFont(font)
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

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.open_edit_dialog()  # 调用打开编辑对话框的方法

    def open_edit_dialog(self):
        dialog = EditNameDialog(self.text(), self)
        dialog.exec_()  # 显示对话框并等待用户操作


    def edit_name(self):
        # 创建输入框
        input_dialog = QLineEdit(self.text())
        input_dialog.setFixedSize(140, 40)
        input_dialog.setFont(self.font())
        input_dialog.setStyleSheet("border: 1px solid black;")
        input_dialog.setAlignment(Qt.AlignLeft)

        # 显示输入框并处理输入
        input_dialog.returnPressed.connect(lambda: self.update_name(input_dialog.text()))
        input_dialog.setFocus()  # 设置焦点到输入框
        input_dialog.show()

    def update_name(self, new_name):
        if new_name.strip():  # 确保新名字不为空
            self.setText(new_name + " [新]")  # 更新标签文本
            self.selected = False  # 取消选择状态
            self.update_style()  # 更新样式

    def update_style(self):
        if self.selected:
            self.setStyleSheet("border: 1px solid black; background-color: lightblue;")
        else:
            self.setStyleSheet("border: 1px solid black;")
class EditNameDialog(QDialog):
    def __init__(self, current_name, label, parent=None):
        super().__init__(parent)
        self.label = label
        self.setWindowTitle("更改名字")  # 设置对话框标题
        self.setFixedSize(300,300)

        layout = QVBoxLayout()
        self.input_field = QLineEdit(current_name)
        self.input_field.setPlaceholderText("输入新名字")
        layout.addWidget(self.input_field)

        button_layout = QHBoxLayout()
        self.confirm_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")

        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.confirm_button.clicked.connect(self.confirm_change)
        self.cancel_button.clicked.connect(self.reject)  # 关闭对话框

    def confirm_change(self):
        new_name = self.input_field.text()
        self.label.update_name(new_name)  # 更新标签的名字
        self.accept()  # 关闭对话框并返回接受状态
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

        with open('./students.txt', 'r', encoding='utf-8') as file:
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
            label = SelectableLabel(f"{name} [新]")
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
        selected_labels = [label for label in self.findChildren(SelectableLabel, options=Qt.FindChildrenRecursively) if
                           label.selected]
        if not selected_labels:
            QMessageBox.warning(self, "警告", "请先选择一个名字")
            return

        for label in selected_labels:
            text = label.text().split()[0]  # 获取名字部分
            # 检查当前标签所在的组别
            current_group = None
            if label in [entry[2] for entry in self.group_first]:
                current_group = 'group_first'
            elif label in [entry[2] for entry in self.group_second]:
                current_group = 'group_second'
            elif label in [entry[1] for entry in self.ignore]:
                current_group = 'ignore'

            # 检查是否尝试将标签移动到其当前组别
            if current_group == category:
                QMessageBox.warning(self, "警告", f"不能将名字移动到当前组别: {category}")
                continue  # 跳过此标签的移动
            # 从原组别中删除该名字
            self.remove_from_other_categories(text, category)

            # 根据选择的目标组别将名字移动到新组别
            if category == 'group_first':
                self.group_first.append((text, 0.000, label))
            elif category == 'group_second':
                self.group_second.append((text, 0.000, label))
            elif category == 'ignore':
                self.ignore.append((text, label))

            # 从当前布局中移除标签
            label.setParent(None)
            label.selected = False  # 取消选中状态
            label.update_style()  # 更新样式

            # 将标签重新添加到目标组别布局中
            self.update_names_layout()

        self.update_names_layout()  # 刷新布局

    def remove_from_other_categories(self, name, category):
        if category != 'group_first':
            self.group_first = [item for item in self.group_first if item[0] != name]
        if category != 'group_second':
            self.group_second = [item for item in self.group_second if item[0] != name]
        if category != 'ignore':
            self.ignore = [item for item in self.ignore if item[0] != name]

    def update_names_layout(self):
        self.clear_layout(self.names_layout)

        group_first_layout = QVBoxLayout()
        group_second_layout = QVBoxLayout()
        ignore_layout = QVBoxLayout()

        self.add_names_to_layout(self.group_first, group_first_layout, 6)
        self.add_names_to_layout(self.group_second, group_second_layout, 6)
        self.add_names_to_layout(self.ignore, ignore_layout, 6)

        group_first_group = QGroupBox("组别一")
        font = QFont('Arial', int(14 * font_scale))
        font.setBold(True)  # 加粗字体
        group_first_group.setFont(font)
        group_first_group.setLayout(group_first_layout)

        group_second_group = QGroupBox("组别二")
        group_second_group.setFont(font)
        group_second_group.setLayout(group_second_layout)

        ignore_group = QGroupBox("忽略")
        ignore_group.setFont(font)
        ignore_group.setLayout(ignore_layout)

        self.names_layout.addWidget(group_first_group)
        self.names_layout.addWidget(group_second_group)
        self.names_layout.addSpacing(20)
        self.names_layout.addWidget(ignore_group)

        # 添加输入框用于添加新学生
        self.add_input_field(group_first_layout, 'group_first')
        self.add_input_field(group_second_layout, 'group_second')
        self.add_input_field(ignore_layout, 'ignore')

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
        with open('./students.txt', 'w', encoding='utf-8') as file:
            file.write('[group_first]\n')
            for entry in self.group_first:
                label = entry[2]
                current_name = label.text().replace(" [新]", "").strip()
                file.write(f"{current_name}\n")
            file.write('[group_second]\n')
            for entry in self.group_second:
                label = entry[2]
                current_name = label.text().replace(" [新]", "").strip()
                file.write(f"{current_name}\n")
            file.write('[ignore]\n')
            for entry in self.ignore:
                label = entry[1]
                current_name = label.text().replace(" [新]", "").strip()
                file.write(f"{current_name}\n")

if __name__ == '__main__':
    import os
    # 获取当前文件的目录
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # 设置工作目录为上级目录
    parent_directory = os.path.dirname(current_directory)
    os.chdir(parent_directory)
    app = QApplication(sys.argv)
    ex = EditMode()
    ex.show()
    sys.exit(app.exec_())