import datetime

from PyQt6.QtCore import Qt, QEvent, QTimer, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from BioRegisterApp import Ui_MainWindow
import sys
import requests
from pyzkfp import ZKFP2
import time


class Worker(QObject):
    # кастомный сигнал для связи между потоками
    progress = pyqtSignal(int)
    register_completed = pyqtSignal()
    compare_completed = pyqtSignal(bool)

    # zkfp2 = ZKFP2()
    # zkfp2.Init()
    # zkfp2.OpenDevice(0)

    # Обработчик сигнала с BioRegisterApp
    @pyqtSlot()
    def register_finger(self):
        templates = []
        for i in range(1, 4):
            while True:
                print('зашел в while')
                # capture = Worker.zkfp2.AcquireFingerprint()
                # if capture:
                #     tmp, img = capture
                #     templates.append(tmp)
                time.sleep(1)
                self.progress.emit(i)
                print('progress emit послан!')
                time.sleep(2)
                break
        # regTemp, regTempLen = Worker.zkfp2.DBMerge(*templates)
        # print(regTemp)
        print('функция отработала!')
        self.register_completed.emit()

    # Обработчик сигнала с BioRegisterApp
    @pyqtSlot()
    def compare_finger(self):
        if True:
            self.compare_completed.emit(True)
        else:
            self.compare_completed.emit(False)


class BioRegisterApp(QMainWindow):
    # кастомный сигнал для связи между потоками
    request_worker_register = pyqtSignal()
    request_worker_compare = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)
        self.main_ui.username_label.setText(username)
        self.main_ui.check_button.hide()
        # self.main_ui.check_button.clicked.connect(lambda: print("check"))
        self.main_ui.check_button.clicked.connect(lambda: self.request_worker_compare.emit())
        if islinked:
            self.main_ui.message_label.setText('Ваш аккаунт уже привязан')
            self.main_ui.check_button.show()

        self.worker = Worker()
        self.worker_thread = QThread()

        # подключение кастомных сигналов к кастомным обработчикам
        self.worker.progress.connect(self.update_scanning_status)
        self.worker.register_completed.connect(self.complete_register_finger)
        self.worker.compare_completed.connect(self.complete_compare_finger)

        self.request_worker_register.connect(self.worker.register_finger)
        self.request_worker_compare.connect(self.worker.compare_finger)

        # смещение класса Worker в поток и запуск потока
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        # сигнал классу Worker в другом потоке для запуска scan_finger()
        self.request_worker_register.emit()

    # обработчик сигнала с Worker'a
    def update_scanning_status(self, status: int):
        self.main_ui.message_label.setText(f'status: {status}/3')

    # обработчик сигнала с Worker'a
    def complete_register_finger(self):
        print('Сканирование завершено!')
        self.main_ui.message_label.setText(f'Сканирование завершено!')
        self.main_ui.check_button.show()
        # закрывать поток, если он не нужен, но вроде как всегда нужен
        # self.worker_thread.exit()
        # self.worker_thread.wait()
        # если ломается - убрать deleteLater()
        # self.worker_thread.deleteLater()
        print(f'Поток завершен: {self.worker_thread.isFinished()}')

    # обработчик сигнала с Worker'a
    def complete_compare_finger(self, is_ok: bool):
        print('Сравнение завершено!')
        if is_ok:
            self.main_ui.message_label.setText(f'Отпечатки совпадают, все хорошо!')
        else:
            self.main_ui.message_label.setText(f'Ваш отпечаток не совпадает :(')


def request_api():
    session = requests.Session()
    session.auth = ('admin', 'admin')
    
    # опрос на юзернейм
    # with open('C:\Gizmo\userId.txt', 'r', encoding='UTF-8') as txt:
    #     userid = txt.read().strip()
    userid = 2
    response = session.get(f'http://185.35.130.253/api/users/{userid}', timeout=3)
    res = response.json()
    username = res['result']['username']

    # опрос на проверку привязки аккaунта
    response = session.get(f'http://185.35.130.253/api/users/{userid}/note', timeout=3)
    res = response.json()
    if len(res['result']) == 0:
        return username, False

    print('Ваш аккаунт уже привязан')
    return username, True


if __name__ == '__main__':
    try:
        username, islinked = request_api()
    except Exception as e:
        with open('log.txt', 'a', encoding='UTF-8') as f:
            f.write(f'{datetime.datetime.now().strftime("%x %H:%M:%S")}\n{str(e)}\n\n')
            # exit()
            username, islinked = 'User', False
    
    app = QApplication(sys.argv)
    main_window = BioRegisterApp()
    main_window.show()
    sys.exit(app.exec())