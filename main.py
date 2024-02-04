import requests

session = requests.Session()
session.auth = ('admin', 'admin')
response = session.get('http://185.35.130.253/api/users/7')
print(response.json())




# http://185.35.130.253/doc/index.html    http://xxx.xx.xxx.xxx/api/users/7,