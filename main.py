# from data_set import *
from genre_recommend import build_chart
from data import *
from googletrans import Translator
import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.Qt import *


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# UI 불러오기
form = resource_path('movie_UI.ui') # 메인창 ui
form_class = uic.loadUiType(form)[0]

loading_form = resource_path('loading_page.ui')
loading_ui = uic.loadUiType(loading_form)[0]

class Loading(QDialog, loading_ui):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.parent = parent

        movie = QMovie('./img/search.gif')
        self.loading_img.setPixmap(QPixmap('./img/search.gif'))
        self.loading_img.setMovie(movie)
        movie.start()

        timer = QTimer(self)
        timer.timeout.connect(self.close_and_move)
        timer.start(5000)

        self.DEFAULT_TIME = 10
        timer_2 = QTimer(self)
        timer_2.timeout.connect(self.label_change)
        timer_2.setInterval(1000)
        timer_2.start()

    def close_and_move(self):
        self.close()
        self.parent.stackedWidget.setCurrentWidget(self.parent.main_page_2)

    def label_change(self):
        self.DEFAULT_TIME -= 1
        if self.DEFAULT_TIME == 0:
            self.DEFAULT_TIME = 10
        self.label_2.setText(f'로딩 중입니다....{self.DEFAULT_TIME}')
        print(f'로딩 중입니다....{self.DEFAULT_TIME}')


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super( ).__init__( )
        self.setupUi(self)
        self.setWindowTitle('초간단 영화추천기')
        self.setCursor(QCursor(QPixmap('./img/bono_face.png').scaled(80, 80)))
        # 버튼 시그널 연결

        self.stackedWidget.setCurrentIndex(0) # 기본 페이지는 0(오프닝 페이지)
        self.re_check_btn.clicked.connect(lambda : self.stackedWidget.setCurrentWidget(self.open_page))
        self.start_btn.clicked.connect(self.test)
        # self.check_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.main_page_2))
        self.quit_btn.clicked.connect(lambda: self.close())
        self.made_by.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.contributer_page)) # 만든사람들 창
        self.background_lab.mousePressEvent = lambda event: self.stackedWidget.setCurrentWidget(self.open_page) # 이미지 클릭하면 오프닝 페이지로 이동


        # 불러오기 테스트
        # print(build_chart('Romance').head(15)) 장르
        # print(improved_recommendations('Mean Girls')) #영화


        # 콤보박스에 숫자 넣기
        self.comboBox.addItems([str(e) for e in range(1, 101)])
        self.comboBox.setCurrentIndex(9) #콤보박스의 기본값은 10으로 지정
        # 위젯에 버튼 넣기
        genres_kor_list = list(genres_dict.keys()) # 20개
        self.button_group = QButtonGroup() # 버튼 그룹 생성
        grid = QGridLayout()
        cnt = 0
        for i in range(1, 6):
            for j in range(1, 5):
                button = QPushButton(genres_kor_list[cnt]) # 버튼 생성 및 이름 넣어줌
                button.setFixedSize(150, 75) # 버튼의 크기 고정
                button.setCheckable(True) # 선택할 수 있게 설정
                self.button_group.addButton(button) # 버튼 그룹에 버튼 추가
                grid.addWidget(button, i, j)
                cnt+=1
        self.widget.setLayout(grid)

        self.button_list = self.widget.findChildren(QPushButton)
        for btn in self.button_list:
            btn.clicked.connect(self.btn_event_func)

        self.check_btn.clicked.connect(self.show_result)
        # self.check_btn.clicked.connect(self.show_loading_page)

    def test(self):
        """버튼 다 체크되어있지 않게 하기"""
        self.stackedWidget.setCurrentWidget(self.main_page_1)
        for btn in self.button_list:
            btn.setChecked(False)

    def btn_event_func(self):
        """버튼 한 번만 눌리게 """
        self.button_group.setExclusive(True)

    def show_loading_page(self):
        loading_page = Loading(self)
        loading_page.show()
        loading_page.exec_()

    def show_result(self):
        """정보 받아와서 결과를 보여주는 부분"""

        try:
            # 정보 넣어주기
            for btn in self.button_list:
                if btn.isChecked():
                    btn_name = btn.text()
            # btn_obj = self.sender().text() # 버튼 정보
            combobox_text = self.comboBox.currentText() # 콤보박스 정보


            print(btn_name, combobox_text)
            result = build_chart(genres_dict[btn_name]).head(int(combobox_text))
            print(result)
            self.insert_data_in_tablewidget(result, btn_name, int(combobox_text))
            self.show_loading_page() # 로딩 페이지 보여주기
        except UnboundLocalError:
            QMessageBox.warning(self, "Warning", "버튼이 눌려지지 않았습니다.")

    def insert_data_in_tablewidget(self, data, btn_name, row):
        self.movie_result.setText(f'{btn_name} 영화의 추천 결과는...')
        self.tableWidget.setRowCount(row)
        translator = Translator()
        for idx, title in enumerate(data['title']):
            word = translator.translate(title, dest='ko')
            # print(word.text)
            self.tableWidget.setItem(idx, 0, QtWidgets.QTableWidgetItem(title))
            self.tableWidget.setItem(idx, 1, QtWidgets.QTableWidgetItem(word.text))
        for idx, year in enumerate(data['year']):
            self.tableWidget.setItem(idx, 2, QtWidgets.QTableWidgetItem(year))
        for idx, wr in enumerate(data['wr']):
            self.tableWidget.setItem(idx, 3, QtWidgets.QTableWidgetItem(str(round(wr, 2))))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 열 너비를 조정합니다.




if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = WindowClass( )
    myWindow.show( )
    app.exec_( )


