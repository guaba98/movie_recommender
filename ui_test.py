import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QListWidget, QGridLayout, QHBoxLayout, QVBoxLayout, \
    QSizePolicy
from PyQt5.QtCore import Qt


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moving Items Between List Widgets")
        self.window_width, self.window_height = 1200, 800
        self.setMinimumSize(self.window_width, self.window_height)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.initUI()

        for i in range(10):
            self.listWidgetLeft.addItem('Item {0}'.format(list("ABCDEFGHIJK")[i]))

        self.updateButtonStatus()
        self.setButtonConnections()

    def initUI(self):
        subLayouts = {}

        subLayouts['LeftColumn'] = QGridLayout()
        subLayouts['RightColumn'] = QVBoxLayout()
        self.layout.addLayout(subLayouts['LeftColumn'], 1)
        self.layout.addLayout(subLayouts['RightColumn'], 1)

        self.buttons = {}
        self.buttons['>>'] = QPushButton('&>>')
        self.buttons['>'] = QPushButton('>')
        self.buttons['<'] = QPushButton('<')
        self.buttons['<<'] = QPushButton('&<<')
        self.buttons['Up'] = QPushButton('&Up')
        self.buttons['Down'] = QPushButton('&Down')

        for k in self.buttons:
            self.buttons[k].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

        """
        First Column
        """
        self.listWidgetLeft = QListWidget()
        subLayouts['LeftColumn'].addWidget(self.listWidgetLeft, 1, 0, 4, 4)

        subLayouts['LeftColumn'].setRowStretch(4, 1)
        subLayouts['LeftColumn'].addWidget(self.buttons['>>'], 1, 4, 1, 1, alignment=Qt.AlignTop)
        subLayouts['LeftColumn'].addWidget(self.buttons['<'], 2, 4, 1, 1, alignment=Qt.AlignTop)
        subLayouts['LeftColumn'].addWidget(self.buttons['>'], 3, 4, 1, 1, alignment=Qt.AlignTop)
        subLayouts['LeftColumn'].addWidget(self.buttons['<<'], 4, 4, 1, 1, alignment=Qt.AlignTop)

        """
        Second Column
        """
        self.listWidgetRight = QListWidget()

        hLayout = QHBoxLayout()
        subLayouts['RightColumn'].addLayout(hLayout)

        hLayout.addWidget(self.listWidgetRight, 4)

        vLayout = QVBoxLayout()
        hLayout.addLayout(vLayout, 1)

        vLayout.addWidget(self.buttons['Up'])
        vLayout.addWidget(self.buttons['Down'])
        vLayout.addStretch(1)

    def setButtonConnections(self):
        self.listWidgetLeft.itemSelectionChanged.connect(self.updateButtonStatus)
        self.listWidgetRight.itemSelectionChanged.connect(self.updateButtonStatus)

        self.buttons['>'].clicked.connect(self.buttonAddClicked)
        self.buttons['<'].clicked.connect(self.buttonRemoveClicked)
        self.buttons['>>'].clicked.connect(self.buttonAddAllClicked)
        self.buttons['<<'].clicked.connect(self.buttonRemoveAllClicked)

        self.buttons['Up'].clicked.connect(self.buttonUpClicked)
        self.buttons['Down'].clicked.connect(self.buttonDownClicked)

    def buttonAddClicked(self):
        row = self.listWidgetLeft.currentRow()
        rowItem = self.listWidgetLeft.takeItem(row)
        self.listWidgetRight.addItem(rowItem)

    def buttonRemoveClicked(self):
        row = self.listWidgetRight.currentRow()
        rowItem = self.listWidgetRight.takeItem(row)
        self.listWidgetLeft.addItem(rowItem)

    def buttonAddAllClicked(self):
        for i in range(self.listWidgetLeft.count()):
            self.listWidgetRight.addItem(self.listWidgetLeft.takeItem(0))

    def buttonRemoveAllClicked(self):
        for i in range(self.listWidgetRight.count()):
            self.listWidgetLeft.addItem(self.listWidgetRight.takeItem(0))

    def buttonUpClicked(self):
        rowIndex = self.listWidgetRight.currentRow()
        currentItem = self.listWidgetRight.takeItem(rowIndex)
        self.listWidgetRight.insertItem(rowIndex - 1, currentItem)
        self.listWidgetRight.setCurrentRow(rowIndex - 1)

    def buttonDownClicked(self):
        rowIndex = self.listWidgetRight.currentRow()
        currentItem = self.listWidgetRight.takeItem(rowIndex)
        self.listWidgetRight.insertItem(rowIndex + 1, currentItem)
        self.listWidgetRight.setCurrentRow(rowIndex + 1)

    def updateButtonStatus(self):
        self.buttons['Up'].setDisabled(
            not bool(self.listWidgetRight.selectedItems()) or self.listWidgetRight.currentRow() == 0)
        self.buttons['Down'].setDisabled(not bool(
            self.listWidgetRight.selectedItems()) or self.listWidgetRight.currentRow() == self.listWidgetRight.count() - 1)
        self.buttons['>'].setDisabled(not bool(self.listWidgetLeft.selectedItems()) or self.listWidgetLeft.count() == 0)
        self.buttons['<'].setDisabled(
            not bool(self.listWidgetRight.selectedItems()) or self.listWidgetRight.count() == 0)


if __name__ == '__main__':
    # don't auto scale when drag app to a different monitor.
    # QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget {
            font-size: 30px;
        }
        QPushButton {
            font-size: 30px;
            width: 200px;
            height: 45px;
        }
    ''')

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')