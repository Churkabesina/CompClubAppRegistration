import requests

session = requests.Session()
session.auth = ('admin', 'admin')

# опрос на юзернейм
with open('C:\Gizmo\userId.txt', 'r', encoding='UTF-8') as txt:
    userid = txt.read().strip()
response = session.get(f'http://185.35.130.253/api/users/{userid}')
res = response.json()
username = res['result']['username']

# опрос на проверку привязки акквунта
response = session.get(f'http://185.35.130.253/api/users/{userid}/note')
res = response.json()
if len(res['result']) == 0:
    pass
else:
    print('Ваш аккаунт уже привязан')

# вставить текст отпечатка
response = session.put(f'http://xxx.xx.xxx.xxx/api/users/userId/note/{finger_txt}/0')


# http://185.35.130.253/doc/index.html    http://xxx.xx.xxx.xxx/api/users/7   http://xxx.xx.xxx.xxx/api/users/userId/note