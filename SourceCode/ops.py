from PyQt5.QtCore import QObject, pyqtSignal


class VideoStatus:
    # -1为未加载 1为播放 0为暂停
    VIDEO_NOT_LOADED = -1
    VIDEO_PAUSE = 0
    VIDEO_PLAY = 1


class Signals(QObject):
    refresh_signal = pyqtSignal()
    analysis_finished_signal = pyqtSignal(list, list)
    roi_selected_signal = pyqtSignal(list)


class VideoInfo:
    def __init__(self):
        self.VIDEO_PATH = None
        self.VIDEO_FPS = 0
        self.VIDEO_FRAME_COUNT = 0
        self.VIDEO_FRAME_NOW = 0
        self.ROI_COORD_LT = (400, 500)
        self.ROI_COORD_RB = (850, 1000)
        self.ROI_COLOR = (255, 0, 0)
        self.ROI_THICKNESS = 2
        self.SCALE_RATE = 1
        self.CURTAIN_SIZE = (600, 400)
        self.VIDEO_FRAME = None
        self.VIDEO_FRAME_PROCESSED = None