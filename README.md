# videoProcesserGUI
本项目是基于PyQT5和OpenCV完成对图像特定区域灰度值变化的带有图形用户界面的视频分析程序

- [开始之前](#开始之前)
- [使用方法](#使用方法)
- [基本运行逻辑](#基本运行逻辑)
- [联系作者](#联系作者)


### 开始之前
我为该程序准备了两个不同的版本：在编译器中运行的简易无GUI版本以及带UI的可执行文件版本，两者均具有相同的基本逻辑。
+ 如果您在此前并不具备编程基础，并且不想进行复杂的配置，那么我推荐您使用本仓库里 **Realsed** 文件下的已编译文件，并运行 **mainWindow.exe**
+ 如果您在此前具有一定的编程基础，且想要更加直观的了解程序的运行逻辑，请移步[llllTnTlll/videoProcessing](https://github.com/llllTnTlll/videoProcessing)

### 使用方法
使用程序的打包版本即可直接在windows环境下使用本应用，您可以[点击这里](https://github.com/llllTnTlll/videoProcesserGUI/releases/tag/v1.0.0-alpha)获取到本程序的压缩文件，解压**videoProcesserGUI.zip**
后运行 **mainWindow.exe** 即可开始工作,您可以参考下图进行操作：

![操作流程](https://github.com/llllTnTlll/picGit/blob/master/VideoProcesserGUI/mainWindow.drawio.png)

在点击分析按钮之前，请确保您已经正确选择兴趣区域(ROI),应用程序仅会针对兴趣区域内的内容分析灰度值变化,您可以通过在文本框直接输入整数值来划定兴趣区域，也可以通过点击“从当前帧选择ROI”按钮来选择兴趣区域。   
选择完成后，点击分析按钮得到分析结果。

### 基本运行逻辑
为了方便使用，本程序通过一个视频线程以一定频率刷新QLabel实现播放器功能，你可以从下图中了解QLabel刷新的基本流程：

![流程图](https://github.com/llllTnTlll/picGit/blob/master/VideoProcesserGUI/refresh-Page-1.drawio.png)

在灰度平均值计算方面则使用了OpenCV库自带的 **cv.meanStdDev()** 方法：
```python
def get_avg_gray_value(roi):
    gray = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
    means, dev = cv.meanStdDev(gray)
    return means[0, 0]  
```
其中roi代表截取的roi图像，您可以在 **func.py** 文件中找到该api，通过修改该api即可修改程序的绘图逻辑，从而改变程序的功能，请注意返回值必须为一个值，以保证折线图可以被正确绘制。
请注意 **cv.meanStdDev()** 并不是简单的计算灰度值的平均值，而是对RGB三通道设定了一个加权系数，你可以在OpenCV的[官方文档](https://docs.opencv.org/3.4.1/de/d25/imgproc_color_conversions.html)中找到相关说明

### 联系作者
如果您在程序使用过程中感到困惑或是希望直接反馈程序中的bug，请联系：liuzhiyuan991@gmail.com