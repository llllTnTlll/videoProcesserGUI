import cv2 as cv
import matplotlib.pyplot as plt
from PIL import Image
import io

from PyQt5.QtWidgets import QDesktopWidget


def get_avg_gray_value(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    means, dev = cv.meanStdDev(gray)
    return means[0, 0]


def draw_chart(x_points, y_points, xlabel, ylabel):
    plt.cla()
    plt.plot(x_points, y_points)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='PNG')
    img = Image.open(io.BytesIO(buffer.getvalue()))
    return img


def raise_up_window(win):
    qr = win.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    win.move(qr.topLeft())
    win.raise_()
