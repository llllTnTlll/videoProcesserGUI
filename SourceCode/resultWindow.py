from PyQt5.QtWidgets import QWidget, QHeaderView, QTableWidgetItem, QFileDialog
from PyQt5 import uic
import pyperclip


class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 加载ui
        self.ui = uic.loadUi("res/ui/resultWindow.ui")
        self.CHART = None
        self.X_POINTS = None
        self.Y_POINTS = None

        self.ui.pushButton_copy.clicked.connect(self.copy_result)
        self.ui.pushButto_save.clicked.connect(self.save_chart)

    def refresh_result(self, x_points, y_points, chart):
        self.CHART = chart
        self.X_POINTS = x_points
        self.Y_POINTS = y_points
        self.set_table()
        self.set_label()

    def set_table(self):
        self.ui.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.resultTable.setColumnCount(1)
        self.ui.resultTable.setRowCount(len(self.Y_POINTS))
        self.ui.resultTable.setHorizontalHeaderLabels(['GrayValue'])
        for i in range(len(self.Y_POINTS)):
            item = QTableWidgetItem(str(self.Y_POINTS[i]))
            self.ui.resultTable.setItem(i, 0, item)

    def set_label(self):
        self.ui.resultLabel.setPixmap(self.CHART.toqpixmap())

    def copy_result(self):
        pyperclip.copy(str(self.Y_POINTS))

    def save_chart(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                   "Images (*.png *.xpm *.jpg *.bmp *.gif);;All Files (*)",
                                                   options=options)
        if file_name:
            self.CHART.save(file_name)
