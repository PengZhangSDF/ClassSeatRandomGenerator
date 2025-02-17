from PyQt5.QtWidgets import QDialog, QVBoxLayout,QLabel

class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.add_msg = ''
        self.setWindowTitle("加载中")
        self.setGeometry(800, 500, 300, 50)
        layout = QVBoxLayout()
        label = QLabel(f"{self.add_msg}正在加载，请稍候...")
        layout.addWidget(label)
        self.setLayout(layout)