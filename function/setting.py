# -*- coding: utf-8 -*-
import sys
import yaml
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QLineEdit, QCheckBox, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from utils.get_font import font_scale

class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_file = './config.yaml'  # 配置文件路径
        self.config = self.load_config()  # 读取配置
        self.font_scale = font_scale
        self.initUI()

    def load_config(self):
        """读取配置文件并返回配置字典"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"读取配置文件时出错: {e}")
            return {}

    def save_config(self):
        """将配置字典保存到配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, allow_unicode=True)
        except Exception as e:
            print(f"保存配置文件时出错: {e}")

    def initUI(self):
        self.setWindowTitle("设置")
        self.setGeometry(100, 50, 1280, 1000)

        layout = QVBoxLayout()

        # 添加标题
        title_label = QLabel("设置")
        title_label.setFont(QFont('Arial', int(24 * self.font_scale)))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 添加副标题
        subtitle_label = QLabel("所有更改会被立即保存")
        subtitle_label.setFont(QFont('Arial', int(16 * self.font_scale)))
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        layout.addSpacing(20)
        # 输入框和按钮的水平布局
        small_point_layout = QHBoxLayout()

        # 输入框：随机小数位数
        self.text_small_point = QLabel("随机小数位数 (1-5)")
        self.text_small_point.setFont(QFont('Arial',int(24 * self.font_scale)))
        layout.addWidget(self.text_small_point)
        self.small_point_input = QLineEdit()
        self.small_point_input.setFont(QFont('Arial', int(16 * self.font_scale)))
        self.small_point_input.setPlaceholderText("随机小数位数 (1-5)")
        self.small_point_input.setText(str(self.config.get('small_point', 4)))  # 默认值为4
        self.small_point_input.textChanged.connect(self.update_small_point)
        small_point_layout.addWidget(self.small_point_input)

        # 向上箭头按钮
        up_button = QPushButton("↑")
        up_button.setFont(QFont('Arial', int(16 * self.font_scale)))
        up_button.setFixedWidth(150)
        up_button.clicked.connect(self.increment_small_point)
        small_point_layout.addWidget(up_button)

        # 向下箭头按钮
        down_button = QPushButton("↓")
        down_button.setFont(QFont('Arial', int(16 * self.font_scale)))
        down_button.setFixedWidth(150)
        down_button.clicked.connect(self.decrement_small_point)
        small_point_layout.addWidget(down_button)

        layout.addLayout(small_point_layout)

        # 复选框：循环杀死希沃管家服务进程
        layout.addSpacing(50)
        self.regulatory_taskkill_checkbox = QCheckBox("循环杀死希沃管家服务进程(如果希沃识别程序为弹窗广告的情况下开启)")
        self.regulatory_taskkill_checkbox.setFont(QFont('Arial', int(24 * self.font_scale)))
        self.regulatory_taskkill_checkbox.setChecked(self.config.get('regulatory_taskkill', False))
        self.regulatory_taskkill_checkbox.stateChanged.connect(self.update_regulatory_taskkill)
        layout.addWidget(self.regulatory_taskkill_checkbox)

        # 复选框：自动投影
        layout.addSpacing(50)
        self.auto_project_checkbox = QCheckBox("自动投影                                                        ")
        self.auto_project_checkbox.setFont(QFont('Arial', int(24 * self.font_scale)))
        self.auto_project_checkbox.setChecked(self.config.get('auto_project', False))
        self.auto_project_checkbox.stateChanged.connect(self.update_auto_project)
        layout.addWidget(self.auto_project_checkbox)

        layout.addSpacing(50)
        self.web_text = QLabel("程序开源且免费\n"
                               "帮助改进:https://github.com/PengZhangSDF/ClassSeatRandomGenerator/issues\n"
                               "联系作者:236152307@qq.com\n"
                               "开源网站：https://github.com/PengZhangSDF/ClassSeatRandomGenerator\n")
        self.web_text.setFont(QFont('Arial', int(14 * self.font_scale)))
        layout.addWidget(self.web_text)
        # 添加退出设置按钮
        layout.addSpacing(50)
        exit_button = QPushButton("退出设置")
        exit_button.setFont(QFont('Arial', int(24 * self.font_scale)))
        exit_button.clicked.connect(self.exit_settings)
        layout.addWidget(exit_button)

        self.setLayout(layout)
        layout.addStretch(1)
    def increment_small_point(self):
        """增加随机小数位数"""
        try:
            value = int(self.small_point_input.text())
            if 1 <= value < 5:  # 限制最大值为5
                value += 1
                self.small_point_input.setText(str(value))
                self.config['small_point'] = value
                self.save_config()  # 立即保存
        except ValueError:
            self.small_point_input.setText("4")  # 恢复为默认值

    def decrement_small_point(self):
        """减少随机小数位数"""
        try:
            value = int(self.small_point_input.text())
            if 2 <= value <= 5:  # 限制最小值为1
                value -= 1
                self.small_point_input.setText(str(value))
                self.config['small_point'] = value
                self.save_config()  # 立即保存
        except ValueError:
            self.small_point_input.setText("4")  # 恢复为默认值

    def update_small_point(self):
        """更新随机小数位数"""
        try:
            value = int(self.small_point_input.text())
            if 1 <= value <= 5:
                self.config['small_point'] = value
                self.save_config()  # 立即保存
            else:
                self.small_point_input.setText(str(self.config.get('small_point', 4)))  # 恢复为默认值
        except ValueError:
            self.small_point_input.setText(str(self.config.get('small_point', 4)))  # 恢复为默认值

    def update_regulatory_taskkill(self, state):
        """更新循环杀死希沃管家服务进程的状态"""
        self.config['regulatory_taskkill'] = (state == Qt.Checked)
        self.save_config()  # 立即保存

    def update_auto_project(self, state):
        """更新自动投影的状态"""
        self.config['auto_project'] = (state == Qt.Checked)
        self.save_config()  # 立即保存

    def exit_settings(self):
        # 关闭设置窗口
        self.close()
        # 重新加载主界面
        if self.parent():
            self.parent().load_names()  # 重新加载名字
            self.parent().create_color_buttons()  # 重新创建颜色选择按钮
            self.parent().create_action_buttons()  # 重新创建操作按钮
            self.parent().create_seating_grid()  # 重新创建座位表
            self.parent().restore_seating_arrangement(False)  # 恢复座位表状态

def main():
    app = QApplication(sys.argv)
    settings_window = SettingsWindow()
    settings_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()