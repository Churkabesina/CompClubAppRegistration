from PyQt6.QtCore import Qt, QEvent, QTimer, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from BioRegisterApp import Ui_MainWindow
import sys
import requests
from pyzkfp import ZKFP2
import time


class Worker(QObject):
    progress = pyqtSignal(int)
    completed = pyqtSignal()
    # zkfp2 = ZKFP2()
    # zkfp2.Init()
    # zkfp2.OpenDevice(0)

    @pyqtSlot()
    def scan_finger(self):
        templates = []
        for i in range(1, 4):
            while True:
                print('зашел в while')
                # capture = Worker.zkfp2.AcquireFingerprint()
                # if capture:
                #     tmp, img = capture
                #     templates.append(tmp)
                time.sleep(5)
                self.progress.emit(i)
                print('progress emit послан!')
                time.sleep(2)
                break
        # regTemp, regTempLen = Worker.zkfp2.DBMerge(*templates)
        # print(regTemp)
        print('функция отработала!')
        self.completed.emit()


class BioRegisterApp(QMainWindow):
    request_worker = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)
        self.main_ui.username_label.setText(username)
        self.main_ui.check_button.hide()
        self.main_ui.check_button.clicked.connect(lambda: print("check"))
        if islinked:
            self.main_ui.message_label.setText('Ваш аккаунт уже привязан')
            self.main_ui.check_button.show()

        self.worker = Worker()
        self.worker_thread = QThread()

        self.worker.progress.connect(self.update_scanning_status)
        self.worker.completed.connect(self.complete_scanning)

        self.request_worker.connect(self.worker.scan_finger)

        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

    def update_scanning_status(self, status: int):
        self.main_ui.message_label.setText(f'status: {status}/3')

    def complete_scanning(self):
        print('Сканирование завершено!')
        self.main_ui.message_label.setText(f'Сканирование завершено!')
        self.main_ui.check_button.show()
        self.worker_thread.deleteLater()


def request_api():
    session = requests.Session()
    session.auth = ('admin', 'admin')
    
    # опрос на юзернейм
    # with open('C:\Gizmo\userId.txt', 'r', encoding='UTF-8') as txt:
    #     userid = txt.read().strip()
    userid = 2
    response = session.get(f'http://185.35.130.253/api/users/{userid}')
    res = response.json()
    username = res['result']['username']

    # опрос на проверку привязки аккaунта
    response = session.get(f'http://185.35.130.253/api/users/{userid}/note')
    res = response.json()
    if len(res['result']) == 0:
        return username, False
    print('Ваш аккаунт уже привязан')
    return username, True


if __name__ == '__main__':

    username, islinked = request_api()
    
    app = QApplication(sys.argv)
    main_window = BioRegisterApp()
    time.sleep(2)
    main_window.request_worker.emit()
    main_window.show()
    sys.exit(app.exec())