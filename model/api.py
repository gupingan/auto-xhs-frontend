"""
@File: api.py
@Author: 顾平安
@Created: 2023/11/9 15:18
@Description: Created in frontend.
"""
import requests

class API:
    def __init__(self, token, cookies=''):
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Cookies': cookies,
        }

    def get(self, url, params=None):
        if params:
            response = requests.get(url, params=params, headers=self.headers).json()
        else:
            response = requests.get(url, headers=self.headers).json()
        return response

    def post(self, url, data):
        response = requests.post(url=url, data=data, headers=self.headers).json()
        return response
