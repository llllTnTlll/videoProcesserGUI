import cv2 as cv
import matplotlib.pyplot as plt
from PIL import Image
import io


def get_avg_gray_value(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    means, dev = cv.meanStdDev(gray)
    return means[0, 0]


def draw_chart(x_points, y_points, title, xlabel, ylabel):
    plt.cla()
    plt.title(title)
    plt.plot(x_points, y_points)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='PNG')
    img = Image.open(io.BytesIO(buffer.getvalue()))
    return img