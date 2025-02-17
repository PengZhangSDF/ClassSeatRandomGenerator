from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPalette

class SwapPositions:
    def __init__(self, seating_arrangement):
        self.seating_arrangement = seating_arrangement
        self.first_seat = None  # 用于存储第一个选择的座位
        self.exit_mode = True

    def select_seat(self, seat):
        if not self.exit_mode:
            if self.first_seat is None:
                # 选择第一个座位
                self.first_seat = seat
                seat.setStyleSheet("background-color: lightgreen;")  # 设置为绿色
                print(f"选择第一个座位: {seat.text()}")
            else:
                # 选择第二个座位并交换
                second_seat = seat
                print(f"选择第二个座位: {second_seat.text()}")
                self.swap(second_seat)
                # 立即恢复颜色
                self.reset_seat_color(self.first_seat)
                self.reset_seat_color(second_seat)
                self.first_seat = None  # 重置选择

    def swap(self, second_seat):
        # 交换两个座位的文本和 original_color 属性
        temp_text = self.first_seat.text()
        temp_color = self.first_seat.property("original_color")  # 直接使用保存的 original_color

        # 交换文本
        self.first_seat.setText(second_seat.text())
        second_seat.setText(temp_text)

        # 交换 original_color 属性
        self.first_seat.setProperty("original_color", second_seat.property("original_color"))
        second_seat.setProperty("original_color", temp_color)

        # 根据新的 original_color 更新颜色
        self.first_seat.setStyleSheet(f"background-color: {self.first_seat.property('original_color')};")
        second_seat.setStyleSheet(f"background-color: {second_seat.property('original_color')};")

    def reset_seat_color(self, seat):
        # 恢复座位颜色
        original_color = seat.property("original_color")
        if original_color:
            seat.setStyleSheet(f"background-color: {original_color};")  # 恢复原色
        else:
            seat.setStyleSheet("")

    def exit_swap_mode(self):
        if self.first_seat:
            self.reset_seat_color(self.first_seat)  # 清除绿色标记
            self.first_seat = None  # 重置选择
        self.exit_mode = True
        # 恢复座位的点击事件
        for row in self.seating_arrangement.seats:
            for seat in row:
                seat.clicked.disconnect()
                seat.clicked.connect(self.seating_arrangement.change_seat_color)