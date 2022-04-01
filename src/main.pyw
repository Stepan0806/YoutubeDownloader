import os
import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QImage, QPixmap

from download import find_video, download
from main_window import Ui_MainWindow


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thumbnail = QImage('img/Youtube.png')
        self.streams = {}
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showMaximized()
        self.ui.url_input.returnPressed.connect(lambda: self.find_video())
        self.ui.save_button.pressed.connect(self.save)

    def find_video(self):
        self.ui.video_title.setText('Please wait...')
        title, thumbnail_data, self.streams = find_video(self.ui.url_input.text())
        self.ui.video_title.setText(title)

        if thumbnail_data:
            self.thumbnail = QImage()
            self.thumbnail.loadFromData(thumbnail_data)
        else:
            self.thumbnail = QImage('img/Youtube.png')
        self.resizeEvent(None)

        self.ui.download_choose.clear()
        for stream_info in self.streams.keys():
            self.ui.download_choose.addItem(stream_info)
        self.ui.download_choose.setCurrentIndex(0)

    def save(self):
        download_choose = self.ui.download_choose.currentText()
        if download_choose == '':
            return
        title = self.ui.video_title.text()
        path = self.get_save_path(download_choose, title)
        if not path:
            return
        self.ui.file_name_label.setText(path[-1])
        self.ui.video_title.setText('Downloading...')
        result = download(self.streams[download_choose], path)
        if result != 'done':
            self.ui.video_title.setText(result)
        else:
            self.ui.video_title.setText(title)

    def get_save_path(self, download_choose, title):
        directory = os.path.join(os.path.expanduser('~'), 'Videos', title)
        filter = ' '.join(download_choose.split()[-2:])
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'YoutubeDownloader', directory, filter)[0]
        if not path:
            return
        true_extension = filter.split('.')[-1][:-1]
        path = '.'.join([path.split('.')[0], true_extension])
        return os.path.split(path)

    def resizeEvent(self, event):
        size = self.ui.video_thumbnail.size()
        pixmap = QPixmap(self.thumbnail).scaled(size.width(), size.height(), QtCore.Qt.KeepAspectRatio)
        self.ui.video_thumbnail.setPixmap(pixmap)
        if event is not None:
            QtWidgets.QMainWindow.resizeEvent(self, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
