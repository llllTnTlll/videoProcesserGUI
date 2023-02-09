import sys
import time
from pathlib import Path

import cv2 as cv
import numpy as np
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox

from funcs import get_avg_gray_value, raise_up_window, draw_chart
from resultWindow import ResultWindow
from roiWindow import RoiWindow
from ops import VideoInfo, VideoStatus, Signals


class VideoPlayer(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.player_status = VideoStatus.VIDEO_NOT_LOADED
        self.refresh_rate = 20.0
        self.mutex = QMutex()
        self.signals = Signals()
        self.is_slider_pressed = False

    def run(self):
        while True:
            if self.player_status != VideoStatus.VIDEO_PLAY:
                continue
            if not self.is_slider_pressed:
                self.signals.refresh_signal.emit()
                time.sleep(1 / self.refresh_rate)

    def play(self):
        with QMutexLocker(self.mutex):
            self.player_status = VideoStatus.VIDEO_PLAY

    def pause(self):
        with QMutexLocker(self.mutex):
            self.player_status = VideoStatus.VIDEO_PAUSE

    def set_fps(self, fps):
        self.refresh_rate = fps

    def slider_pressed(self):
        self.is_slider_pressed = True

    def slider_released(self):
        self.is_slider_pressed = False


class AnalysisThread(QThread):
    def __init__(self, info: VideoInfo):
        super().__init__()
        self.video_info = info
        self.signals = Signals()
        # self.is_offset = is_offset

    def run(self):
        if not all(
                (
                        self.video_info.ROI_COORD_LT,
                        self.video_info.ROI_COORD_RB,
                        self.video_info.VIDEO_PATH,
                )
        ):
            return

        x_points = []
        y_points = []

        capture = cv.VideoCapture(self.video_info.VIDEO_PATH)
        frame_count = 0
        while capture.isOpened():
            ret, frame = capture.read()
            if not ret:
                break
            x_min = int(self.video_info.ROI_COORD_LT[0] * (1 / self.video_info.SCALE_RATE))
            x_max = int(self.video_info.ROI_COORD_RB[0] * (1 / self.video_info.SCALE_RATE))
            y_min = int(self.video_info.ROI_COORD_LT[1] * (1 / self.video_info.SCALE_RATE))
            y_max = int(self.video_info.ROI_COORD_RB[1] * (1 / self.video_info.SCALE_RATE))
            roi = frame[y_min:y_max, x_min:x_max, :]
            gray_means = get_avg_gray_value(roi)
            # if self.is_offset:
            #     gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            #     average = np.mean(gray)
            #     gray_means = gray_means - average
            y_points.append(gray_means)
            x_points.append(frame_count)
            frame_count += 1
        capture.release()
        self.signals.analysis_finished_signal.emit(x_points, y_points)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 属性
        self.video_info = VideoInfo()
        self.video_capture = cv.VideoCapture()

        # 子窗体
        self.result_window = ResultWindow()
        self.roi_window = RoiWindow()

        # 加载ui
        self.ui = uic.loadUi("./res/ui/MainWindow.ui")
        self.reset_coord()

        self.ui.BrushWidthSlider.valueChanged.connect(self.brush_width_changed)
        self.ui.BrushWidthSlider.setRange(1, 10)
        self.ui.BrushWidthSlider.setValue(5)
        self.ui.rply_checkbox.setChecked(True)

        self.colors = [("Red", (255, 0, 0)), ("Green", (0, 255, 0)), ("Blue", (0, 0, 255)), ("Yellow", (255, 255, 0)), ("Purple", (255, 0, 255))]
        for color_name, color_value in self.colors:
            self.ui.comboBox_Color.addItem(color_name)
            self.ui.comboBox_Color.setItemData(self.ui.comboBox_Color.count() - 1, QColor(*color_value), Qt.BackgroundRole)
        self.ui.comboBox_Color.activated[int].connect(self.brush_color_changed)
        self.ui.comboBox_Color.setCurrentIndex(0)
        self.ui.label_brush_color.setText("(255, 0, 0)")

        # 按键功能
        self.ui.playBtn.clicked.connect(self.play_or_pause)
        self.ui.analysisBtn.clicked.connect(self.start_analysis)
        self.ui.selectRoiBtn.clicked.connect(self.select_roi)

        # 动作
        self.ui.openAct.triggered.connect(self.open_act)

        # 视频播放
        self.player = VideoPlayer()

        self.player.start()
        self.ui.videoSlider.sliderMoved.connect(self.slider_moved)
        self.ui.videoSlider.sliderReleased.connect(self.slider_released)
        self.ui.VideoLabel.setScaledContents(True)

        self.ui.LineEdit_x1.editingFinished.connect(self.coord_changed)
        self.ui.LineEdit_x2.editingFinished.connect(self.coord_changed)
        self.ui.LineEdit_y1.editingFinished.connect(self.coord_changed)
        self.ui.LineEdit_y2.editingFinished.connect(self.coord_changed)

        self.behaviors_lock(True)
        self.set_curtain()

        # 多线程
        self.t = AnalysisThread(self.video_info)

        # 信号
        self.player.signals.refresh_signal.connect(self.frame_refresh)
        self.t.signals.analysis_finished_signal.connect(self.show_result)
        self.roi_window.signals.roi_selected_signal.connect(self.roi_selected)

    # 基本功能与按键响应
    def behaviors_lock(self, status):
        if status:
            self.ui.behaviors_groupBox.setEnabled(False)
            self.ui.parameters_groupBox.setEnabled(False)
        elif not status:
            self.ui.behaviors_groupBox.setEnabled(True)
            self.ui.parameters_groupBox.setEnabled(True)

    def open_act(self):
        cap = "open video file"
        filt = "视频文件(*.wmv *.avi *.mp4 *.mov)"
        path = QFileDialog.getOpenFileName(caption=cap, filter=filt)[0]
        if path != "" and Path(path).is_file():
            self.video_init(path)
            self.video_play(is_first=True)
            self.behaviors_lock(False)

    def start_analysis(self):
        self.ui.behaviors_groupBox.setEnabled(False)
        if self.ui.checkBox_offset.isChecked():
            self.t = AnalysisThread(self.video_info)
        self.t.start()

    def select_roi(self):
        pixmap = self.video_info.VIDEO_FRAME
        self.roi_window.set_roilabel(pixmap)
        self.roi_window.ui.show()

    def brush_color_changed(self, index):
        color = self.colors[index][1]
        self.ui.label_brush_color.setText(f"({color[0]}, {color[1]}, {color[2]})")
        self.video_info.ROI_COLOR = color

    def brush_width_changed(self):
        self.ui.label_brush_width.setText(str(self.ui.BrushWidthSlider.value()))
        self.video_info.ROI_THICKNESS = int(self.ui.BrushWidthSlider.value())

    # 视频相关
    def play_or_pause(self):
        """视频暂停播放按钮"""
        if self.player.player_status == VideoStatus.VIDEO_PLAY:
            self.video_pause()
        elif self.player.player_status == VideoStatus.VIDEO_PAUSE:
            self.video_play()

    def display_progress(self):
        position = int((self.video_info.VIDEO_FRAME_NOW / self.video_info.VIDEO_FRAME_COUNT) * 100)
        if not self.player.is_slider_pressed:
            self.ui.videoSlider.setSliderPosition(position)
        self.ui.ratioLabel.setText("Frame {} of {}".format(str(self.video_info.VIDEO_FRAME_NOW), str(self.video_info.VIDEO_FRAME_COUNT)))

    def set_progress(self, frame_now, frame_count=None):
        if frame_count is not None:
            self.video_info.VIDEO_FRAME_COUNT = frame_count
        self.video_info.VIDEO_FRAME_NOW = frame_now
        self.display_progress()

    def video_init(self, path):
        # 存储路径
        self.video_info.VIDEO_PATH = path

        # 获取视频默认帧速率与总帧数
        self.video_capture.open(self.video_info.VIDEO_PATH)
        self.player.set_fps(int(self.video_capture.get(cv.CAP_PROP_FPS)))

        # 设置进度label
        self.set_progress(0, int(self.video_capture.get(cv.CAP_PROP_FRAME_COUNT)))

        # 设置幕布大小
        height = int(self.video_capture.get(cv.CAP_PROP_FRAME_HEIGHT) * self.video_info.SCALE_RATE)
        width = int(self.video_capture.get(cv.CAP_PROP_FRAME_WIDTH) * self.video_info.SCALE_RATE)
        self.video_info.CURTAIN_SIZE = (width, height)
        self.set_curtain()

    def video_play(self, is_first=False):
        if self.player.player_status != VideoStatus.VIDEO_NOT_LOADED or is_first:
            self.player.play()
            self.ui.playBtn.setStyleSheet("QPushButton{qproperty-icon:url(res/icon/pause.png)}")

    def video_pause(self):
        if self.player.player_status != VideoStatus.VIDEO_NOT_LOADED:
            self.player.pause()
            self.ui.playBtn.setStyleSheet("QPushButton{qproperty-icon:url(res/icon/play.png)}")

    def video_reset(self):
        self.video_info.VIDEO_FRAME_NOW = 0
        self.video_capture.set(cv.CAP_PROP_POS_FRAMES, 0)

    def slider_moved(self, position):
        self.player.slider_pressed()
        if self.player.player_status != VideoStatus.VIDEO_NOT_LOADED:
            target_frame = int((position / 100) * self.video_info.VIDEO_FRAME_COUNT)
            self.video_capture.set(cv.CAP_PROP_POS_FRAMES, target_frame)
            self.set_progress(target_frame)

    def slider_released(self):
        self.player.slider_released()

    def set_curtain(self):
        """初始化幕布"""
        curtain = np.zeros((self.video_info.CURTAIN_SIZE[0], self.video_info.CURTAIN_SIZE[1], 3), np.uint8)
        self.ui.VideoLabel.resize(self.video_info.CURTAIN_SIZE[0], self.video_info.CURTAIN_SIZE[1])
        curtain = self.to_pixmap(curtain, self.video_info.CURTAIN_SIZE[0], self.video_info.CURTAIN_SIZE[1])
        self.ui.VideoLabel.setPixmap(curtain)

    def to_pixmap(self, img, width, height):
        """帧格式转化"""
        temp_image = QImage(img.flatten(), width, height, QImage.Format_RGB888)
        temp_pixmap = QPixmap.fromImage(temp_image)
        temp_pixmap.scaled(self.video_info.CURTAIN_SIZE[0], self.video_info.CURTAIN_SIZE[1])
        return temp_pixmap

    def process(self, rgb):
        if self.ui.ingray_checkBox.isChecked():
            gray = cv.cvtColor(rgb, cv.COLOR_RGB2GRAY)
            rgb = cv.cvtColor(gray, cv.COLOR_GRAY2RGB)
        processed = cv.rectangle(np.copy(rgb), self.video_info.ROI_COORD_LT, self.video_info.ROI_COORD_RB, self.video_info.ROI_COLOR, self.video_info.ROI_THICKNESS)
        return processed

    # 信号响应
    def frame_refresh(self):
        """帧重绘"""
        if self.video_capture.isOpened():
            flag, frame = self.video_capture.read()
            if flag:
                frame = cv.resize(frame, (0, 0), fx=self.video_info.SCALE_RATE, fy=self.video_info.SCALE_RATE)
                height, width = frame.shape[:2]
                if frame.ndim == 3:
                    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                    processed = self.to_pixmap(self.process(rgb), width, height)
                elif frame.ndim == 2:
                    rgb = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)
                    processed = self.to_pixmap(self.process(rgb), width, height)

                self.video_info.VIDEO_FRAME = self.to_pixmap(rgb, width, height)
                self.video_info.VIDEO_FRAME_PROCESSED = processed
                self.ui.VideoLabel.setPixmap(self.video_info.VIDEO_FRAME_PROCESSED)

                self.video_info.VIDEO_FRAME_NOW += 1
                self.display_progress()

            else:
                # 当播放结束时
                if self.ui.rply_checkbox.isChecked():
                    self.video_reset()
                    self.video_play()
                else:
                    self.video_reset()
                    self.video_pause()
        else:
            print("open file or capturing device error, init again")

    def show_result(self, x_points, y_points):
        chart = draw_chart(x_points, y_points, "Frame number", "Difference in gray scale")
        self.result_window.refresh_result(x_points, y_points, chart)
        self.ui.behaviors_groupBox.setEnabled(True)
        self.result_window.ui.show()
        raise_up_window(self.result_window.ui)

    def roi_selected(self, selected):
        self.video_info.ROI_COORD_LT = [selected[0], selected[1]]
        self.video_info.ROI_COORD_RB = [selected[2], selected[3]]
        self.reset_coord()

    # 兴趣区域相关
    def reset_coord(self):
        self.ui.LineEdit_x1.setText("{}".format(self.video_info.ROI_COORD_LT[0]))
        self.ui.LineEdit_y1.setText("{}".format(self.video_info.ROI_COORD_LT[1]))
        self.ui.LineEdit_x2.setText("{}".format(self.video_info.ROI_COORD_RB[0]))
        self.ui.LineEdit_y2.setText("{}".format(self.video_info.ROI_COORD_RB[1]))

    def coord_changed(self):

        try:
            p1 = (int(self.ui.LineEdit_x1.text()), int(self.ui.LineEdit_y1.text()))
            p2 = (int(self.ui.LineEdit_x2.text()), int(self.ui.LineEdit_y2.text()))
        except ValueError:
            self.reset_coord()
            QMessageBox(QMessageBox.Warning, 'Warning', '请输入整数型坐标值').exec()
            return

        if p1[0] < p2[0] and p1[1] < p2[1]:
            if p1[0] > 0 and p1[1] > 0:
                if p2[0] > 0 and p2[1] > 0:
                    if p1[0] < self.video_info.CURTAIN_SIZE[0] and p2[0] < self.video_info.CURTAIN_SIZE[0]:
                        if p1[1] < self.video_info.CURTAIN_SIZE[1] and p2[1] < self.video_info.CURTAIN_SIZE[1]:
                            self.video_info.ROI_COORD_LT = p1
                            self.video_info.ROI_COORD_RB = p2
                            return
        self.reset_coord()
        QMessageBox(QMessageBox.Warning, 'Warning', '坐标输入非法').exec()


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    w = MainWindow()
    w.ui.show()
    app.exec()
