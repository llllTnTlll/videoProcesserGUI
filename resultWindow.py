import io
from PIL import Image
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import cv2 as cv
import matplotlib.pyplot as plt


class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 加载ui
        self.ui = uic.loadUi("res/ui/resultWindow.ui")
        self.ROI_COORD_LT = None
        self.ROI_COORD_RB = None
        self.VIDEO_PATH = None
        self.SCALE_RATE = 0.3

    def analysis(self):
        if self.ROI_COORD_LT is not None and self.ROI_COORD_RB is not None and self.VIDEO_PATH is not None:
            # 待绘制点集
            x_points = []
            y_points = []

            capture = cv.VideoCapture(self.VIDEO_PATH)
            frame_count = 0
            while capture.isOpened():
                ret, frame = capture.read()
                if ret:
                    # 读取坐标
                    x_min = int(self.ROI_COORD_LT[0] * (1 / self.SCALE_RATE))
                    x_max = int(self.ROI_COORD_RB[0] * (1 / self.SCALE_RATE))
                    y_min = int(self.ROI_COORD_LT[1] * (1 / self.SCALE_RATE))
                    y_max = int(self.ROI_COORD_RB[1] * (1 / self.SCALE_RATE))

                    # # 对图像进行深度复制
                    # copied = np.empty_like(frame)
                    # copied[:] = frame

                    # 截取图像
                    roi = frame[y_min:y_max, x_min:x_max, :]

                    # 计算灰度平均值
                    gray_means = self.get_avg_gray_value(roi)
                    y_points.append(gray_means)
                    x_points.append(frame_count)

                else:
                    break
                frame_count += 1

            img = self.draw_chart(x_points, y_points)
            self.ui.resultLabel.setPixmap(img.toqpixmap())

    @staticmethod
    def get_avg_gray_value(img):
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        means, dev = cv.meanStdDev(gray)
        return means[0, 0]

    @staticmethod
    def draw_chart(x_points, y_points):
        plt.cla()
        plt.title("GRAYVALUE CHANGE DIAGRAM ")
        plt.plot(x_points, y_points)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='PNG')
        img = Image.open(io.BytesIO(buffer.getvalue()))
        return img
