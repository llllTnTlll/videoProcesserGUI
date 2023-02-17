# videoProcesserGUI
本项目是基于PyQT5和OpenCV完成对图像特定区域灰度值变化的带有图形用户界面的视频分析程序
### 开始之前
我为该程序准备了两个不同的版本：在编译器中运行的简易无GUI版本以及带UI的可执行文件版本，两者均具有相同的基本逻辑。
+ 如果您在此前并不具备编程基础，并且不想进行复杂的配置，那么我推荐您使用本仓库里**Realsed**文件下的已编译文件，并运行**mainWindow.exe**
+ 如果您在此前具有一定的编程基础，且想要更加直观的了解程序的运行逻辑，请移步[llllTnTlll/videoProcessing](https://github.com/llllTnTlll/videoProcessing)

### 使用方法
使用程序的打包版本即可直接在windows环境下使用本应用，您可以在[这里](https://github.com/llllTnTlll/videoProcesserGUI/releases/tag/v1.0.0-alpha)获取到本程序的压缩文件，解压videoProcesserGUI.zip
后运行mainWindow.exe即可开始工作

### 基本运行逻辑
为了方便使用，本程序通过一个视频线程以一定频率刷新QLabel实现播放器功能，你可以从下图中了解QLabel刷新的基本流程：
![流程图](https://github.com/llllTnTlll/picGit/blob/master/VideoProcesserGUI/refresh-Page-1.drawio.png)

