from settings import Settings


class User:
    def __init__(self, username: str = None, password: str = None, settings: Settings = None):
        self.username = username
        self.password = password
        self.settings = settings
        self.token = None
        self.max_limit = 0

    def setUser(self, username: str, password: str):
        self.username = username
        self.password = password

    def setLimit(self, limit: int):
        self.max_limit = limit

    def bind(self, settings: Settings):
        self.settings = settings
