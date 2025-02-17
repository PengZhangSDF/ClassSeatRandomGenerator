from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout,QLabel,QHBoxLayout,QPushButton,QApplication
from PyQt5.QtGui import QPixmap

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
        self.normal = ""

        self.setLayout(self.layout)

        self.images = [f".{self.normal}/img/{i}.png" for i in range(1, 7)]  # 图片路径
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

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)  # 创建 QApplication 实例
    showing = ImageViewer()
    showing.normal = "."
    showing.show()
    sys.exit(app.exec_())  # 运行事件循环