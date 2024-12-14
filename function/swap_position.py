from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPalette

class SwapPositions:
    def __init__(self, seating_arrangement):
        self.seating_arrangement = seating_arrangement
        self.first_seat = None  # 用于存储第一个选择的座位
        self.exit_mode = True

    def select_seat(self, seat):
        # 检查座位是否为空或无意义
        if not self.exit_mode:
            if seat.text() == "" or seat.text() == "无意义位置":
                print(f"选择的座位 '{seat.text()}' 无效，忽略。")
                return  # 不做任何反应

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
                self.reset_seat_color(self.first_seat)
                self.reset_seat_color(second_seat)
                self.first_seat = None  # 重置选择

    def swap(self, second_seat):
        # 交换两个座位的内容
        temp_text = self.first_seat.text()
        self.first_seat.setText(second_seat.text())
        second_seat.setText(temp_text)


    def reset_seat_color(self, seat):
        # 恢复座位颜色
        original_color = seat.property("original_color")
        if original_color:
            seat.setStyleSheet(f"background-color: {original_color};")  # 恢复原色


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