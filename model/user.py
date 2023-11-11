from settings import Settings


class User:
    def __init__(self, username: str = None, password: str = None, settings: Settings = None):
        self.username = username
        self.password = password
        self.settings = settings
        self.token = None
        self.max_limit = 0
        self.ip = None
        self.login_time = None

    def setUser(self, username: str, password: str):
        self.username = username
        self.password = password

    def setLimit(self, limit: int):
        self.max_limit = limit

    def setIP(self, ip):
        self.ip = ip

    def setTime(self, time_):
        self.login_time = time_

    def bind(self, settings: Settings):
        self.settings = settings
