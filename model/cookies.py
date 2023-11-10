class Cookies:
    def __init__(self, ):
        cookies_str = 'abRequestId=b3a24d97-e349-553f-866c-7fba9239ccaa; a1=18b287fe0af9atg98uvl7aoprycn0jsa7sc9ov2z750000374905; webId=037a83ee1baebf147894c93a32bf9802; gid=yYDJYWifdKWdyYDJYWid8MhJ0ij09kjY7h1WSuW0lUFvSj28I8VM0l888qW4j8280q00WSKf; xsecappid=xhs-pc-web; webBuild=3.14.1; websectiga=82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28; sec_poison_id=3d15f87a-6800-4f2e-88f3-c72c3b0cd034; web_session=040069b2f4a6242ffbafe2d072374bbbc5addd; unread={%22ub%22:%22654389730000000025016160%22%2C%22ue%22:%22653cd502000000001e03ca91%22%2C%22uc%22:27}; cacheId=63020028-d17d-46fe-ac0a-2dd35e7c0558'
        self.cookies = {}
        self.parse_cookies(cookies_str)

    def parse_cookies(self, cookies_str):
        cookie_list = cookies_str.split("; ")
        for cookie in cookie_list:
            key, value = cookie.split("=")
            self.cookies[key] = value

    def get_cookies_str(self):
        cookies_list = [f"{key}={value}" for key, value in self.cookies.items()]
        return "; ".join(cookies_list)

    def get_cookie(self, key):
        return self.cookies.get(key)

    def update_cookie(self, key, value):
        self.cookies[key] = value
        return self

    def delete_cookie(self, key):
        if key in self.cookies:
            del self.cookies[key]

    def __str__(self):
        return self.get_cookies_str()
