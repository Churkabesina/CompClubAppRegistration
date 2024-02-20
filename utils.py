import datetime
import os
import re
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox


def execute_error_msg():
    app = QApplication([])
    error_msg = QMessageBox()
    error_msg.setIcon(QMessageBox.Icon.Critical)
    error_msg.setWindowTitle('Ошибка запуска')
    error_msg.setText('Во время запуска произошла ошибка\n-> log.txt')
    error_msg.buttonClicked.connect(lambda: app.exit())
    error_msg.show()
    sys.exit(app.exec())


def write_error_log(e):
    with open('log.txt', 'a', encoding='UTF-8') as f:
        f.write(f'{datetime.datetime.now().strftime("%x %H:%M:%S")}\n{str(e)}\n\n')


def load_settings_app() -> dict[str, str]:
    settings_names = ['ip', 'score_limit', 'port', 'limit_balance', 'path_to_bat', 'product_ids', 'login_api', 'password_api']
    re_pattern_setting = re.compile(r'\S+=\S+')
    settings = dict()

    if not os.path.isfile('settings.ini'):
        with open('settings.ini', 'w', encoding='UTF-8') as f:
            f.write(f'score_limit=750\n'
                    f'ip=ultragame.keenetic.pro\n'
                    f'port=85\n'
                    f'limit_balance=100\n'
                    f'path_to_bat=C:\n'
                    f'product_ids=11,10,9\n'
                    f'login_api=admin\n'
                    f'password_api=admin')

    with open('settings.ini', 'r', encoding='UTF-8') as f:
        for line in f:
            if re.fullmatch(re_pattern_setting, line.strip()):
                line = line.strip().split('=')
                settings[line[0]] = line[1].replace(' ', '')

    for name in settings_names:
        if name not in settings:
            raise Exception('Неверно заданы настройки в settings.ini\n'
                            '#score_limit=750\n'
                            '#ip=<ip>\n'
                            '#port=<your_port>\n'
                            '#limit_balance=100\n'
                            '#path_to_bat=C:\\Gizmo\\file.bat\n'
                            '#product_ids=11,10,9\n'
                            '#Заполняйте все без пробелов и кавычек, product_ids через запятую')

    return settings
