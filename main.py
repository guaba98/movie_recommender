# from data_set import *
from data import *

import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# UI 불러오기
form = resource_path('movie_UI.ui') # 메인창 ui
form_class = uic.loadUiType(form)[0]
form_2 = resource_path('movie_btn.ui') # 버튼 ui
form_class_2 = uic.loadUiType(form_2)[0]

# class MovieBtn(QWidget, form_class_2):
#     def __init__(self, parent, btn_name, index):
#         super().__init__()
#         self.parent = parent
#         self.PushButton.setText(btn_name)


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super( ).__init__( )
        self.setupUi(self)
        self.setWindowTitle('초간단 영화추천기')
        # 버튼 시그널 연결
        self.stackedWidget.setCurrentIndex(0)
        self.start_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.main_page_1))
        self.quit_btn.clicked.connect(lambda: self.close())
        self.made_by.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.contributer_page))
        self.background_lab.mousePressEvent = lambda event: self.stackedWidget.setCurrentWidget(self.open_page)


        # 불러오기 테스트
        # print(build_chart('Romance').head(15)) 장르
        # print(improved_recommendations('Mean Girls')) #영화
        # print(md['title'])

        # 위젯에 버튼 넣기
        genres_kor_list = list(genres_dict.keys()) # 20개

        self.button_group = QButtonGroup()
        grid = QGridLayout()
        cnt = 0
        for i in range(1, 6):
            for j in range(1, 5):
                button = QPushButton(genres_kor_list[cnt])
                button.setFixedSize(150, 75)
                button.setCheckable(True)
                self.button_group.addButton(button)
                grid.addWidget(button, i, j)
                cnt+=1
        self.widget.setLayout(grid)



        button_list = self.widget.findChildren(QPushButton)
        for btn in button_list:
            btn.clicked.connect(self.btn_event_func)

    def btn_event_func(self):

        self.button_group.setExclusive(True)

        btn_obj = self.sender()
        print(btn_obj.text())




if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = WindowClass( )
    myWindow.show( )
    app.exec_( )


