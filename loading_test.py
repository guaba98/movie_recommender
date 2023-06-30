import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.Qt import *

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

loading_form = resource_path('loading_page.ui')
loading_ui = uic.loadUiType(loading_form)[0]

class Loading(QDialog, loading_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        movie = QMovie('./img/search.gif')
        self.loading_img.setPixmap(QPixmap('./img/search.gif'))
        self.loading_img.setMovie(movie)
        movie.start()

        timer = QTimer(self)
        timer.timeout.connect(self.close)
        timer.start(10000)

        self.DEFAULT_TIME = 10
        timer_2 = QTimer(self)
        timer_2.timeout.connect(self.label_change)
        timer_2.setInterval(1000)
        timer_2.start()




    def label_change(self):
        self.DEFAULT_TIME -= 1
        if self.DEFAULT_TIME == 0:
            self.DEFAULT_TIME = 10
        self.label_2.setText(f'로딩 중입니다....{self.DEFAULT_TIME}')
        print(f'로딩 중입니다....{self.DEFAULT_TIME}')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = Loading()
    myWindow.show()
    app.exec_()
