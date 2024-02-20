from PyQt6.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox

from ui.BioRegisterApp import Ui_MainWindow
from ui import background

import api_requests
import utils

import sys

import base64

from pyzkfp import ZKFP2


class Worker(QObject):
    def __init__(self, u_name):
        super().__init__()
        self.username = u_name

    # кастомные сигналы для связи между потоками
    register_completed = pyqtSignal()
    compare_completed = pyqtSignal(bool, int)
    progress = pyqtSignal(int)

    try:
        zkfp2 = ZKFP2()
        zkfp2.Init()
        zkfp2.OpenDevice(0)
    except Exception as e:
        utils.write_error_log(e)
        exit()

    # Обработчик сигнала с BioRegisterApp
    @pyqtSlot()
    def register_finger(self):
        try:
            templates = []
            for i in range(1, 4):
                while True:
                    capture = Worker.zkfp2.AcquireFingerprint()
                    if capture:
                        tmp, img = capture
                        templates.append(tmp)
                        self.progress.emit(i)
                        break
            reg_temp, reg_temp_len = Worker.zkfp2.DBMerge(*templates)
            python_reg_temp = bytes(reg_temp)
            base64_temp = base64.b64encode(python_reg_temp).decode('utf-8')

            API.put_finger_tmp_to_db(userid=userid, tmp=base64_temp)
        except Exception as e:
            utils.write_error_log(e)
            exit()
        self.register_completed.emit()

    # Обработчик сигнала с BioRegisterApp
    @pyqtSlot()
    def compare_finger(self):
        try:
            base64_tmp_from_db = API.get_finger_tmp_by_userid(userid=userid)
            tmp_from_db = base64.b64decode(base64_tmp_from_db.encode('utf-8'))
            while True:
                capture = Worker.zkfp2.AcquireFingerprint()
                if capture:
                    tmp, img = capture
                    break
            python_tmp = bytes(tmp)
            res = Worker.zkfp2.DBMatch(python_tmp, tmp_from_db)
        except Exception as e:
            utils.write_error_log(e)
            exit()
        if res > SCORE_LIMIT:
            self.compare_completed.emit(True, res)
        else:
            self.compare_completed.emit(False, res)


class BioRegisterApp(QMainWindow):
    # кастомные сигналы для связи между потоками
    request_worker_register = pyqtSignal()
    request_worker_compare = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('./src/fingerprint.png'))
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)
        self.main_ui.username_label.setText(username)
        self.main_ui.check_button.hide()
        self.main_ui.delete_button.hide()
        self.main_ui.check_button.clicked.connect(self.button_compare_finger_click)
        self.main_ui.delete_button.clicked.connect(self.button_delete_finger_click)

        self.worker = Worker(username)
        self.worker_thread = QThread()

        # подключение кастомных сигналов к кастомным обработчикам
        self.worker.register_completed.connect(self.complete_register_finger)
        self.worker.compare_completed.connect(self.complete_compare_finger)
        self.worker.progress.connect(self.register_progress)

        self.request_worker_register.connect(self.worker.register_finger)
        self.request_worker_compare.connect(self.worker.compare_finger)

        # смещение класса Worker в поток и запуск потока
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        if not islinked:
            # сигнал классу Worker в другом потоке для запуска register_finger()
            self.request_worker_register.emit()
        else:
            self.main_ui.message_label.setText('Ваш аккаунт уже привязан')
            self.main_ui.check_button.show()
            self.main_ui.delete_button.show()

    # обработчик сигнала с Worker'a
    def complete_register_finger(self):
        self.main_ui.message_label.setText(f'Ваш отпечаток зарегистрирован!')
        self.main_ui.check_button.show()
        self.main_ui.delete_button.show()

    # обработчик сигнала с Worker'a
    def complete_compare_finger(self, is_ok: bool, score: int):
        if is_ok:
            self.main_ui.message_label.setText(f'Отпечатки совпадают, все хорошо!\nscore: {score}')
        else:
            self.main_ui.message_label.setText(f'Ваш отпечаток не совпадает :(\nscore: {score}')
        self.main_ui.check_button.setEnabled(True)
        self.main_ui.delete_button.setEnabled(True)

    def register_progress(self, progress: int):
        self.main_ui.message_label.setText(f'Этап {progress}/3')

    def button_compare_finger_click(self):
        self.main_ui.message_label.setText('Приложите палец')
        self.main_ui.check_button.setEnabled(False)
        self.main_ui.delete_button.setEnabled(False)
        self.request_worker_compare.emit()

    def button_delete_finger_click(self):
        warning_msg = QMessageBox(self)
        warning_msg.setStyleSheet("QMessageBox {background-color: rgb(56, 56, 56);}"
                                  "QLabel {min_width: 100px;}"
                                  "QPushButton {color: rgb(56, 56, 56);}")
        warning_msg.setIcon(QMessageBox.Icon.Warning)
        warning_msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        warning_msg.button(QMessageBox.StandardButton.Ok).setText('Да')
        warning_msg.button(QMessageBox.StandardButton.Cancel).setText('Нет')
        warning_msg.setWindowTitle('Предупреждение')
        warning_msg.setText('Вы уверены?')
        button = warning_msg.exec()
        if button == QMessageBox.StandardButton.Ok:
            note_id = str(API.get_note_by_user_id(userid))
            API.delete_fingerprint(user_id=userid, note_id=note_id)
            self.main_ui.check_button.hide()
            self.main_ui.delete_button.hide()
            self.request_worker_register.emit()
            self.main_ui.message_label.setText('Для начала регистрации приложите палец')


if __name__ == '__main__':
    try:
        SETTINGS = utils.load_settings_app()
        IP = f'{SETTINGS["ip"]}:{SETTINGS["port"]}'
        SCORE_LIMIT = int(SETTINGS['score_limit'])
        AUTH_DATA = (SETTINGS['login_api'], SETTINGS['password_api'])
        API = api_requests.CompClubRequests(ip=IP,
                                            limit_balance=float(SETTINGS['limit_balance']),
                                            auth_data=AUTH_DATA,
                                            product_ids=SETTINGS['product_ids'])

        # опрос на юзернейм
        with open(r'C:\Gizmo\userId.txt', 'r', encoding='UTF-8') as txt:
            userid = txt.read().strip()
        username, islinked = API.get_username_and_acc_linking(userid=userid)
    except Exception as e:
        utils.write_error_log(e)
        utils.execute_error_msg()

    app = QApplication(sys.argv)
    main_window = BioRegisterApp()
    main_window.setWindowTitle('UltraCyberArena - Регистрация отпечатка')
    main_window.show()
    sys.exit(app.exec())
