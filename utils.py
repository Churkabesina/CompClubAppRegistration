import datetime
import os
import re


def write_error_log(e):
    with open('log.txt', 'a', encoding='UTF-8') as f:
        f.write(f'{datetime.datetime.now().strftime("%x %H:%M:%S")}\n{str(e)}\n\n')


def load_settings_register_app() -> dict[str, str]:
    settings_names = ['ip', 'score_limit']
    re_pattern_setting = re.compile(r'\w+=\w.+')
    settings = dict()

    if not os.path.isfile('settings.ini'):
        with open('settings.ini', 'w', encoding='UTF-8') as f:
            f.write(f'score_limit=750\n'
                    f'ip=185.35.130.253')

    with open('settings.ini', 'r', encoding='UTF-8') as f:
        for line in f:
            if re.fullmatch(re_pattern_setting, line.strip()):
                line = line.strip().split('=')
                settings[line[0]] = line[1].replace(' ', '')

    for name in settings_names:
        if name not in settings:
            raise Exception('Неверно заданы настройки в settings.ini')

    return settings