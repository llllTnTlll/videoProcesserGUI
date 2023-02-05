from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class RoiWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 加载ui
        self.ui = uic.loadUi("res/ui/roiWindow.ui")

    def set_roilabel(self, pixmap):
        self.ui.RoiLabel.setPixmap(pixmap)
