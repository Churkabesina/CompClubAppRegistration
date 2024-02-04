from PyQt6.QtCore import Qt, QEvent, QTimer, QThread
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from BioRegisterApp import Ui_MainWindow
import sys
import requests
from pyzkfp import ZKFP2
import threading
import time


class BioRegisterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        main_ui = Ui_MainWindow()
        main_ui.setupUi(self)
        main_ui.username_label.setText(username)
        main_ui.check_button.setVisible(False)
        # _thread = threading.Thread(target=scan)
        if islinked:
            main_ui.message_label.setText('Ваш аккаунт уже привязан')
            main_ui.check_button.setVisible(True)

    def scan_finger(self):
        time.sleep(2)
        self.main_ui.message_label.setText('1/3. ')
            # templates = []
            # a = 0
            # for i in range(3):
            #     while True:
                    # capture = zkfp2.AcquireFingerprint()
                    # if capture:
                    #     tmp, img = capture
                    #     templates.append(tmp)
                    #     break
                    # a += 1
                    # print(a)
                # self.main_ui.message_label.setText('1/3. ')
            # regTemp, regTempLen = zkfp2.DBMerge(*templates)

            # # Store the template in the device's database
            # finger_id = 1 # The id of the finger to be registered
            # zkfp2.DBAdd(finger_id, regTemp)
    

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
        flag = False
    else:
        flag = True
        print('Ваш аккаунт уже привязан')
    return username, flag


if __name__ == '__main__':

    # zkfp2 = ZKFP2()
    # zkfp2.Init()
    # zkfp2.OpenDevice(0)

    username, islinked = request_api()
    
    app = QApplication(sys.argv)
    main_window = BioRegisterApp()

    t = threading.Thread(target=main_window.scan_finger)
    t.start()

    main_window.show()
    sys.exit(app.exec())