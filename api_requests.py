import requests


class CompClubRequests:
    def __init__(self, ip: str, limit_balance: float, product_ids: str, auth_data: tuple):
        self.IP = ip
        self.SESSION = requests.Session()
        self.SESSION.auth = auth_data
        self.limit_balance = limit_balance
        self.product_ids = [int(x) for x in product_ids.split(',')]

    def get_username_and_acc_linking(self, userid: str) -> tuple[str, bool]:

        response = self.SESSION.get(f'http://{self.IP}/api/users/{userid}')
        res = response.json()
        username = res['result']['username']

        # опрос на проверку привязки аккaунта
        response = self.SESSION.get(f'http://{self.IP}/api/users/{userid}/note')
        res = response.json()
        if len(res['result']) == 0:
            return username, False
        return username, True

    def put_finger_tmp_to_db(self, userid: str, tmp: str) -> None:
        
        body = {
            'text': tmp,
            'severity': 0
        }
        # вставить текст отпечатка
        response = self.SESSION.post(f'http://{self.IP}/api/v2.0/users/{userid}/notes', json=body)

    def get_finger_tmp_by_userid(self, userid: str) -> str:

        response = self.SESSION.get(f'http://{self.IP}/api/users/{userid}/note')
        tmp = response.json()['result'][0]['text']
        return tmp

    def check_data_login(self, login: str, password: str) -> tuple[bool, str]:

        # провера на валидность
        res = self.SESSION.get(f'http://{self.IP}/api/users/{login}/{password}/valid')
        checking = int(res.json()['result']['result'])
        if checking != 0:
            return False, 'Неверный логин или пароль'
        
        # проверка на человек внутри
        user_id = res.json()['result']['identity']['userId']
        res = self.SESSION.get(f'http://{self.IP}/api/usersessions/activeinfo')
        for i in res.json()['result']:
            if i['userId'] == user_id:
                return True, 'Активная сессия, проходите'
        
        # проверка на баланс
        res = self.SESSION.get(f'http://{self.IP}/api/users/{user_id}/balance')
        if res.json()['result']['deposits'] < self.limit_balance:
            # проверка на абонемент>>>
            res = self.SESSION.get(f'http://{self.IP}/api/v2.0/users/{user_id}/userusagetime')
            for i in res.json()['result']:
                if i['timeOffer']:
                    if int(i['timeOffer']['productId']) in self.product_ids:
                        return True, 'У вас VIP, проходите'
            return False, 'У вас нет ВИП и не хватает баланса'
            # <<<проверка на абонемент
        else:
            return True, 'Достаточно средств, проходите'

    def check_data_finger(self, user_id: str) -> tuple[bool, str]:

        # проверка на человек внутри
        res = self.SESSION.get(f'http://{self.IP}/api/usersessions/activeinfo')
        for i in res.json()['result']:
            if str(i['userId']) == user_id:
                return True, 'Активная сессия, проходите'
        
        # проверка на баланс
        res = self.SESSION.get(f'http://{self.IP}/api/users/{user_id}/balance')
        if res.json()['result']['deposits'] < self.limit_balance:
            # проверка на абонемент>>>
            res = self.SESSION.get(f'http://{self.IP}/api/v2.0/users/{user_id}/userusagetime')
            for i in res.json()['result']:
                if i['timeOffer']:
                    if int(i['timeOffer']['productId']) in self.product_ids:
                        return True, 'У вас VIP, проходите'
            return False, 'У вас нет ВИП и не хватает баланса'
            # <<<проверка на абонемент
        else:
            return True, 'Достаточно средств, проходите'

    def get_all_ids(self):
        all_userids = []
        res = self.SESSION.get(f'http://{self.IP}/api/v2.0/users?IsDisabled=false&IsDeleted=false')
        for i in res.json()['result']['data']:
            all_userids.append(str(i['id']))
        return all_userids

    def get_note_by_user_id(self, user_id):
        res = self.SESSION.get(f'http://{self.IP}/api/users/{user_id}/note')
        note_id = res.json()['result'][0]['id']
        return note_id

    def delete_fingerprint(self, user_id: str, note_id: str):
        res = self.SESSION.delete(f'http://{self.IP}/api/v2.0/users/{user_id}/notes/{note_id}')