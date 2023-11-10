from .user import User
from .api import API
from .spider import BaseAPI


class QrCode:
    def __init__(self, user: User = None):
        self.user = user
        self.info_api = f'{BaseAPI}/qrcode/info'
        self.state_api = f'{BaseAPI}/qrcode/state'
        self.api = API(self.user.token)

    def info(self):
        try:
            response = self.api.get(self.info_api)
            return response['data']['url'], response['data']['qr_id'], response['data']['code']
        except Exception as e:
            print(f'系统：获取二维码信息失败，错误信息：{e}')
            return None, None, None

    def state(self, qr_id, code):
        try:
            params = {'qrId': qr_id, 'code': code}
            response = self.api.get(self.state_api, params)
            return response['success'], response['msg'], response['data']
        except Exception as e:
            print(f'系统：获取二维码状态失败，错误信息：{e}')
            return None, None, None
