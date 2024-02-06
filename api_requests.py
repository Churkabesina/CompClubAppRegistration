import requests


def get_username_and_acc_linking(userid: str, ip: str = None, session_auth: tuple[str, str] = None) -> tuple[str, bool]:
    session = requests.Session()
    if ip is None:
        ip = '185.35.130.253'
    if session_auth is None:
        session.auth = ('admin', 'admin')

    response = session.get(f'http://{ip}/api/users/{userid}', timeout=3)
    res = response.json()
    username = res['result']['username']

    # опрос на проверку привязки аккaунта
    response = session.get(f'http://{ip}/api/users/{userid}/note', timeout=3)
    res = response.json()
    if len(res['result']) == 0:
        return username, False
    return username, True


def put_finger_tmp_to_db(userid: str, tmp: str, ip: str = None, session_auth: tuple[str, str] = None) -> None:
    session = requests.Session()
    if ip is None:
        ip = '185.35.130.253'
    if session_auth is None:
        session.auth = ('admin', 'admin')

    # вставить текст отпечатка
    response = session.put(f'http://{ip}/api/users/{userid}/note/{tmp}/0')


def get_finger_tmp_by_userid(userid: str, ip: str = None, session_auth: tuple[str, str] = None) -> str:
    session = requests.Session()
    if ip is None:
        ip = '185.35.13253'
    if session_auth is None:
        session.auth = ('admin', 'admin')

    response = session.get(f'http://{ip}/api/users/{userid}/note')
    tmp = response.json()['result']['text']
    return tmp
