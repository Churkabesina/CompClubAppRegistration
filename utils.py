import datetime


def write_error_log(e):
    with open('log.txt', 'a', encoding='UTF-8') as f:
        f.write(f'{datetime.datetime.now().strftime("%x %H:%M:%S")}\n{str(e)}\n\n')