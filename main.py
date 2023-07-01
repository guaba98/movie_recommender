
from genre_recommend import build_chart
from recommend_for_movie import get_recommendations
from movie_recommender import *
from data import genres_dict
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
    """로딩창"""
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.parent = parent

        # gif 파일 불러와서 라벨에 불러줌
        movie = QMovie('./img/search.gif')
        self.loading_img.setPixmap(QPixmap('./img/search.gif'))
        self.loading_img.setMovie(movie)
        movie.start()

        # 타이머 1: 창 닫아주는 타이머
        timer = QTimer(self)
        timer.timeout.connect(self.close_and_move)
        timer.start(10000)

        # 타이머2: 남은 초 알려주는 타이머 -> 10초 기준으로 함
        self.DEFAULT_TIME = 10
        timer_2 = QTimer(self)
        timer_2.timeout.connect(self.label_change)
        timer_2.setInterval(1000) # 1초에 한번씩 연결함
        timer_2.start()

    def close_and_move(self):
        """닫아주고 스택위젯 페이지 옮김"""
        self.close()
        self.parent.stackedWidget.setCurrentWidget(self.parent.main_page_2)

    def label_change(self):
        self.DEFAULT_TIME -= 1 # 1초씩 깎아준다.
        if self.DEFAULT_TIME == 0: # 만약 0이라면
            self.DEFAULT_TIME = 10 # 다시 10으로 만들어줌
        self.label_2.setText(f'로딩 중입니다....{self.DEFAULT_TIME}')


class WindowClass(QMainWindow, form_class):
    """추천 메인 화면"""
    def __init__(self):
        super( ).__init__( )
        self.setupUi(self)
        self.setWindowTitle('초간단 영화추천기')
        self.setWindowIcon(QIcon('./img/bono_face.png'))
        # self.setWindowIcon()
        self.setCursor(QCursor(QPixmap('./img/bono_face.png').scaled(80, 80)))


        # 버튼 시그널 연결
        self.stackedWidget.setCurrentIndex(0) # 기본 페이지는 0(오프닝 페이지)
        self.re_check_btn.clicked.connect(lambda : self.stackedWidget.setCurrentWidget(self.open_page))
        self.start_btn.clicked.connect(lambda :self.stackedWidget.setCurrentWidget(self.main_page_0))
        self.quit_btn.clicked.connect(lambda: self.close())
        self.made_by.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.contributer_page)) # 만든사람들 창
        self.background_lab.mousePressEvent = lambda event: self.stackedWidget.setCurrentWidget(self.open_page) # 이미지 클릭하면 오프닝 페이지로 이동
        # self.go_to_openpage.mousePressEvent = lambda event: self.stackedWidget.setCurrentWidget(self.open_page) # 이미지 클릭하면 오프닝 페이지로 이동
        self.go_to_openpage.mousePressEvent = lambda event: self.remove_btns() # 이미지 클릭하면 오프닝 페이지로 이동

        self.recommend_for_movie.clicked.connect(lambda: self.show_result_page('movie'))
        self.recommend_for_genre.clicked.connect(lambda: self.show_result_page('genre'))
        self.user_choice = None

        # 콤보박스에 숫자 넣기
        self.comboBox.addItems([str(e) for e in range(1, 101)])
        self.comboBox.setCurrentIndex(9)  # 콤보박스의 기본값은 10으로 지정

        # 불러오기 테스트
        # print(build_chart('Romance').head(15)) 장르
        # print(improved_recommendations('Mean Girls')) #영화
        self.check_btn.clicked.connect(self.show_result)

    def remove_btns(self):
        self.stackedWidget.setCurrentWidget(self.open_page)
        button_list = self.scrollAreaWidgetContents.findChildren(QPushButton)
        for btn in button_list:
            btn.deleteLater()

    def show_result_page(self, name):
        self.button_list = self.widget.findChildren(QPushButton)

        if name == 'movie':
            self.user_choice = 'movie'
            # 라벨에 텍스트 입력
            self.text_info.setText('재미있게 본 영화를 선택하세요.')

            # 페이지 이동
            self.stackedWidget.setCurrentWidget(self.main_page_1)

            # 그리드 레이아웃 생성 및 그리드 영역에 버튼 넣기
            self.button_group = QButtonGroup()  # 버튼 그룹 생성
            grid = QGridLayout(self.scrollAreaWidgetContents)
            cnt = 0
            for i in range(1, 41):
                for j in range(1, 6):
                    # print(cnt, qualified_list[cnt])
                    cnt += 1
                    button = QPushButton(qualified_list[cnt])
                    self.button_group.addButton(button)
                    button.setFixedSize(140, 75)
                    button.setCheckable(True)
                    grid.addWidget(button, i, j)

        elif name == 'genre':
            self.user_choice = 'genre'
            self.text_info.setText('추천받고 싶은 영화 장르를 선택하세요!')
            self.stackedWidget.setCurrentWidget(self.main_page_1)

            # 위젯에 버튼 넣기
            genres_kor_list = list(genres_dict.keys())  # 20개
            self.button_group = QButtonGroup()  # 버튼 그룹 생성
            grid = QGridLayout(self.scrollAreaWidgetContents)
            cnt = 0
            for i in range(1, 6):
                for j in range(1, 5):
                    button = QPushButton(genres_kor_list[cnt])  # 버튼 생성 및 이름 넣어줌
                    button.setFixedSize(150, 75)  # 버튼의 크기 고정
                    button.setCheckable(True)  # 선택할 수 있게 설정
                    self.button_group.addButton(button)  # 버튼 그룹에 버튼 추가
                    grid.addWidget(button, i, j)
                    cnt += 1
            # self.widget.setLayout(grid)

        for btn in self.button_list:
            btn.clicked.connect(self.btn_event_func)

    def btn_event_func(self):
        """버튼 한 번만 눌리게 """
        self.button_group.setExclusive(True)

    def show_loading_page(self):
        """로딩 페이지 가져와서 보여주기"""
        loading_page = Loading(self)
        loading_page.show()
        loading_page.exec_()

    def show_result(self):
        """정보 받아와서 결과를 보여주는 부분"""
        self.button_list = self.widget.findChildren(QPushButton)

        try:
            # 정보 넣어주기
            for btn in self.button_list:
                if btn.isChecked():
                    btn_name = btn.text()
            combobox_text = self.comboBox.currentText() # 콤보박스 정보
            if self.user_choice == 'movie':
                result = get_recommendations(btn_name).head(int(combobox_text))
            else:
                result = build_chart(genres_dict[btn_name]).head(int(combobox_text))  #
            self.insert_data_in_tablewidget(self.user_choice, result, btn_name, int(combobox_text))  # 테이블 위젯에 값 넣어주기

            self.show_loading_page() # 로딩 페이지 보여주기

        except UnboundLocalError:
            QMessageBox.warning(self, "Warning", "버튼이 눌려지지 않았습니다.")

    def insert_data_in_tablewidget(self, type, data, btn_name, row):

        self.movie_result.setText(f'{btn_name} 영화의 추천 결과는...')
        self.tableWidget.setRowCount(row)
        translator = Translator()
        for idx, title in enumerate(data['title']):
            word = translator.translate(title, dest='ko')
            # print(word.text)
            self.tableWidget.setItem(idx, 0, QtWidgets.QTableWidgetItem(title))
            self.tableWidget.setItem(idx, 1, QtWidgets.QTableWidgetItem(word.text))

        if type == 'movie':
            for idx, year in enumerate(data['release_date']):
                self.tableWidget.setItem(idx, 2, QtWidgets.QTableWidgetItem(year))
            for idx, wr in enumerate(data['vote_average']):
                self.tableWidget.setItem(idx, 3, QtWidgets.QTableWidgetItem(str(round(wr, 2))))
        else:
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


