"""
@File: controller.py
@Author: 秦宇
@Created: 2023/11/5 16:10
@Description: Created in 咸鱼-自动化-AutoXhs.
"""
import json
import os
import time
import requests
from datetime import datetime
from qrcode import QRCode
from model import Spiders, User, Spider, QrCode, Cookies, UncollectTask, SkipCollectedTask, CommentTask, CollectTask, \
    LikeTask, FollowTask, EndTask, generateGPAValues
from view import *


class Controller:
    def __init__(self):
        self.user = User()
        self.view = View()
        self.commands = {
            'clear': self.clear,
            'cls': self.clear,
            'menu': self.view.menu,
            'main': self.view.menu,
            'home': self.view.menu,
            'help': self.view.help,
        }

    def current(self, type_: str = 'datetime', template: str = "%Y-%m-%d %H:%M:%S"):
        now = datetime.now()
        if type_ == 'str':
            return now.strftime(template)
        elif type_ == 'datetime':
            return now
        elif type_ == 'timestamp':
            now.timestamp()
        return None

    def login(self, username, password):
        try:
            response = requests.post(
                url=f'{self.view.settings.baseAPI}/user/login',
                data={
                    'uname': username,
                    'upwd': password
                }
            )
            self.user.token = response.json().get('token')
            return bool(response.status_code == 200 and response.json()['success']), response.json()['msg']
        except Exception:
            return False, '当前无法登录，请检查网络服务'

    def get_max_limit(self):
        try:
            response = requests.get(
                url=f'{self.view.settings.baseAPI}/user/limit',
                headers={
                    'Authorization': f'Bearer {self.user.token}',
                }
            )
            return response.json()['data']
        except Exception:
            return 0

    def run(self):
        os.system('cls')
        while True:
            uname, upwd = self.view.login()
            if not (uname and upwd):
                printc('系统：', BLUE, end='')
                return print('已终止登录')
            if not self.view.validate_input(uname, upwd):
                continue
            login_state, login_msg = self.login(uname, upwd)
            printc('系统：', BLUE, end='')
            print(f'{login_msg}')
            if login_state:
                break
        if not (logs_folder := Path(f'./日志-{uname}/')).exists():
            logs_folder.mkdir()
        self.user.set(uname, upwd)
        self.user.max_limit = self.get_max_limit()
        self.main()

    def main(self):
        os.system('cls')
        self.view.menu()
        while True:
            option = inputc(f'[{self.user.username}]$ ')
            if option.lower() in ('q', '0', 'exit', 'quit'):
                again = inputc('系统：确认退出？[y|N]$ ', RED)
                if again.lower() == 'y':
                    for spider in Spiders.values():
                        spider.stop()
                    printc('系统：', BLUE, end='')
                    return print('已退出程序')
            elif option == '1':
                self.spider_config()
            elif option == '2':
                self.add_spider()
            elif option == '3':
                self.show_spiders()
            elif option == '4':
                self.operate_spider()
            elif option == '5':
                printc('系统：', BLUE, end='')
                print('功能未开发，敬请期待！')
            elif option == '6':
                self.show_log()
            elif option == '7':
                self.view.show_user_info(self.user, len(Spiders))
            elif not option:
                pass
            elif option.startswith('log '):
                option = option.split(' ')
                if len(option) == 2:
                    self.find_log(option[1])
                elif len(option) == 3:
                    self.find_log(option[1], option[2])
            elif option.startswith('show '):
                option = option.split(' ')
                if len(option) == 2 and (spider := Spiders.get(option[1])):
                    self.view.show_spider_detail(spider)
            elif option.startswith('urls '):
                option = option.split(' ')
                if len(option) == 2 and (spider := Spiders.get(option[1])):
                    self.view.show_spider_urls(spider)
                elif len(option) == 3 and option[2].isdigit():
                    if spider := Spiders.get(option[1]):
                        self.view.show_spider_urls(spider, start=int(option[2]))
                elif len(option) == 4 and option[2].isdigit() and option[3].isdigit():
                    if spider := Spiders.get(option[1]):
                        self.view.show_spider_urls(spider, start=int(option[2]) - 1, end=int(option[3]) + 1)
            else:
                command = self.commands.get(option, lambda: printc('系统：输入有误，请重新输入', RED))
                if command == self.clear:
                    self.clear(self.view.menu)
                else:
                    command()

    @staticmethod
    def clear(func):
        os.system('cls')
        return func()

    def spider_config(self):
        config_items, length = self.view.show_spider_config()
        print("请输入序号选择配置项，输入q或者回车返回上一级")
        while True:
            option = inputc(f'[{self.user.username}/修改配置]$ ')
            if not option or option.lower() in ('q', 'quit', 'exit'):
                self.clear(self.view.menu)
                break
            elif option.isdigit() and 0 <= int(option) < length:
                option = int(option)
                print(f'当前配置项为：{config_items[option][2]}, 输入n/N或回车放弃修改')
                value = inputc(f'[{self.user.username}/爬虫配置]({config_items[option][3]})$ ')
                if not value or value.lower() == 'n':
                    continue
                elif option in (0, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 19):
                    value = bool(value == '1' or value == '开启')
                    if option == 11:
                        if value == self.view.settings.get(config_items[12][0], config_items[12][1]) is True:
                            printc('系统：不能与`再评论再收藏`共同设置为开启，这是无意义的行为', RED)
                            continue
                    if option == 12:
                        if value == self.view.settings.get(config_items[11][0], config_items[11][1]) is True:
                            printc('系统：不能与`跳过已收藏`共同设置为开启，这是无意义的行为', RED)
                            continue
                    if option in (11, 12, 13, 15, 16):
                        if not self.view.settings.get(config_items[10][0], config_items[10][1]):
                            printc('系统：使用某些设置前先必须保证`是否评论`开启', RED)
                            continue
                    if option == 16 and value is True:
                        if not self.view.settings.get(config_items[15][0], config_items[15][1]):
                            printc('系统：使用`屏蔽重试`前先必须保证`检查屏蔽开启`开启', RED)
                            continue
                elif option in (2, 3):
                    items = config_items[option][3].split('|')
                    if value.isdigit() and 0 <= int(value) < len(items):
                        value = items[int(value)].split(' ')[-1]
                    else:
                        printc('系统：输入不规范，配置失败', RED)
                        continue
                elif option in (4, 6, 14, 17, 18):
                    if not value.isdigit():
                        printc('系统：输入不规范，配置失败', RED)
                        continue
                    if option == 4 and not (2 <= int(value) <= 999):
                        printc('系统：任务数量只能设置在[2-999]之间', RED)
                        continue
                    if option == 6 and not (2 <= int(value) <= 999):
                        printc('系统：循环间隔分钟数只能设置在[2-999]之间', RED)
                        continue
                    if option == 14 and not (1 <= int(value) <= 99):
                        printc('系统：生僻字数量只能设置在[1-99]之间', RED)
                        continue
                    if option == 17 and not (1 <= int(value) <= 9):
                        printc('系统：重试次数只能设置在[1-9]之间', RED)
                        continue
                    if option == 18 and not (1 <= int(value) <= 999):
                        printc('系统：任务间隔时间只能设置在[1-999]之间', RED)
                        continue
                elif option == 20:
                    if not Path(value.strip('"')).exists():
                        printc('系统：文件不存在，配置失败', RED)
                        continue
                    value = Path(value.strip('"')).absolute()
                self.view.settings.set(config_items[option][0], config_items[option][1], str(value))
                self.view.settings.save()
                self.view.settings.update()
                self.user.settings.update()
                printc('系统：配置修改成功', GREEN)
            elif option.startswith('log '):
                option = option.split(' ')
                if len(option) == 2:
                    self.find_log(option[1])
                elif len(option) == 3:
                    self.find_log(option[1], option[2])
            elif option.startswith('show '):
                option = option.split(' ')
                if len(option) == 2 and (spider := Spiders.get(option[1])):
                    self.view.show_spider_detail(spider)
            elif option.startswith('urls '):
                option = option.split(' ')
                if len(option) == 2 and (spider := Spiders.get(option[1])):
                    self.view.show_spider_urls(spider)
                elif len(option) == 3 and option[2].isdigit():
                    if spider := Spiders.get(option[1]):
                        self.view.show_spider_urls(spider, start=int(option[2]))
                elif len(option) == 4 and option[2].isdigit() and option[3].isdigit():
                    if spider := Spiders.get(option[1]):
                        self.view.show_spider_urls(spider, start=int(option[2]) - 1, end=int(option[3]) + 1)
            else:
                command = self.commands.get(option, lambda: printc('系统：输入有误，请重新输入', RED))
                if command == self.clear:
                    config_items, length = self.clear(self.view.show_spider_config)
                    print("请输入序号选择配置项，输入q或者回车返回上一级")
                else:
                    command()

    def add_spider(self):
        self.view.settings.update()
        self.user.settings.update()
        if not self.user.settings.check():
            return
        printc('系统：', BLUE, end='')
        print('你确定要创建爬虫吗？请输入 y 准备扫码')
        if 'y' != inputc(f'[{self.user.username}](y|N)$ ').lower():
            printc('系统：', BLUE, end='')
            return print('已经取消创建爬虫操作')
        qrcode = QrCode(self.user)
        url, qr_id, code = qrcode.get_info()
        if not (url and qr_id and code):
            return False
        printc('系统：', BLUE, end='')
        print('请尽快使用手机扫描二维码，防止失效')
        time.sleep(1)
        qr = QRCode()
        qr.add_data(url)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.show()
        while True:
            time.sleep(3)
            success, msg, data = qrcode.get_state(qr_id, code)
            if not success and msg in ('二维码已过期', '未知错误', None):
                return printc('系统：扫码登录失败，请尝试重新请求', RED)
            if success and msg == '登录成功':
                break
        printc('系统：', BLUE, end='')
        print('扫码登录成功，可以关闭二维码')
        cookies = Cookies().update_cookie('web_session', data['session'])
        printc('系统：', BLUE, end='')
        print('请为爬虫命名(推荐使用数字)，方便后续激活、暂停等操作')
        while True:
            spider_name = inputc(f'[{self.user.username}/添加爬虫](回车或N/n取消)$ ')
            if not spider_name or spider_name.lower() in ('n', 'q', 'quit', 'exit'): return
            if spider_name in Spiders.keys():
                printc(f'系统：爬虫 {spider_name} 已存在，请重新命名', RED)
                continue
            if spider_name in self.user.settings.buildWords:
                printc(f'系统：名字 {spider_name} 属于内置关键字，不可使用', RED)
                continue
            if (spider_name not in Spiders.keys()) and (spider_name not in self.commands.keys()):
                break
        spider = Spider(spider_name, self.user, data['user_id'])
        spider.source(cookies)
        # 安排自动化任务
        if spider.isComment and spider.isAgainCommentCollect:
            spider.append_task(UncollectTask())
        if spider.isComment and spider.isSkipCollect:
            spider.append_task(SkipCollectedTask())
        if spider.isComment:
            spider.append_task(CommentTask())
        if spider.isCollect or (spider.isComment and spider.isSkipCollect):
            spider.append_task(CollectTask())
        if spider.isLike:
            spider.append_task(LikeTask())
        if spider.isFollow:
            spider.append_task(FollowTask())
        if len(spider.tasks):
            spider.tasks.append(EndTask())
        # 送进服务器
        create_api = '/api/spider'
        gpa_s, gpa_t = generateGPAValues(self.user.settings.gpaKey, create_api)
        post_data = {
            'count': len(Spiders),
            'info': json.dumps(dict(spider)),
            'gpa_s': gpa_s,
            'gpa_t': gpa_t,
        }
        response = spider.api.post(f"{self.user.settings.baseURL}{create_api}", data=post_data)
        if not response['success']:
            return printc(f'系统：创建爬虫失败 {response["msg"]}', RED)
        # 送进总字典中
        Spiders[spider_name] = spider
        printc('系统：', BLUE, end='')
        print(f'{response["msg"]} 是否激活爬虫？(默认不激活)')
        is_activate = inputc(f'[{self.user.username}/添加爬虫](y|N)$ ')
        if is_activate.lower() == 'y':
            spider.start()

    def show_spiders(self):
        spiders = [(name, states[spider.state], spider.success_count, spider.failure_count, spider.finished_count) for
                   name, spider in Spiders.items()]
        if spiders:
            self.view.show_spiders(spiders)
        else:
            printc('系统：', BLUE, end='')
            print('还没有创建任何爬虫')

    def operate_spider(self):
        printc('系统：', BLUE, end='')
        print('请输入爬虫名称进行选择，输入q或者回车返回上一级')
        while True:
            spider_name = inputc(f'[{self.user.username}/操作爬虫]$ ')
            if not spider_name or spider_name.lower() in ('q', 'exit', 'quit'):
                self.clear(self.view.menu)
                break
            if spider := Spiders.get(spider_name):
                printc('系统：', BLUE, end='')
                print('请用户输入操作序号，回车/q/0可取消')
                print('操作序号：1 激活 | 2 暂停 | 3 恢复 | 4 终止 | 5 删除')
                operate = inputc(f'[{self.user.username}/操作爬虫](选择操作)$ ')
                if not operate or operate in ('0', 'q'):
                    printc('系统：', BLUE, end='')
                    print(f'用户已取消对爬虫 {spider_name} 操作')
                    continue
                elif operate == '1':
                    if spider.state in ('running', 'paused'):
                        return printc(f'系统：爬虫 {spider_name} 已激活过了，不可再激活', RED)
                    spider.start()
                elif operate == '2':
                    if spider.state in ('stopped', 'paused'):
                        return printc(f'系统：爬虫 {spider_name} 已经暂停或者已经终止，不可再暂停', RED)
                    spider.pause()
                elif operate == '3':
                    if spider.state in ('running', 'stopped'):
                        return printc(f'系统：爬虫 {spider_name} 正在运行或者已经终止，不可再恢复', RED)
                    spider.resume()
                elif operate == '4':
                    if spider.state == 'stopped':
                        return printc(f'系统：爬虫 {spider_name} 已经终止，不可再终止', RED)
                    spider.stop()
                elif operate == '5':
                    if spider.state != 'stopped':
                        spider.stop()
                    del Spiders[spider_name]
                    printc('系统：', BLUE, end='')
                    return printc(f'爬虫 {spider_name} 被移除', YELLOW)
                spiders = [(spider.name, states[spider.state], spider.success_count, spider.failure_count,
                            spider.finished_count)]
                self.view.show_spiders(spiders)
            elif spider_name.startswith('show '):
                operate = spider_name.split(' ')
                if len(operate) == 2 and (spider := Spiders.get(operate[1])):
                    self.view.show_spider_detail(spider)
            elif spider_name.startswith('log '):
                operate = spider_name.split(' ')
                if len(operate) == 2:
                    self.find_log(operate[1])
                elif len(operate) == 3:
                    self.find_log(operate[1], operate[2])
            elif spider_name.startswith('urls '):
                operate = spider_name.split(' ')
                if len(operate) == 2 and (spider := Spiders.get(operate[1])):
                    self.view.show_spider_urls(spider)
                elif len(operate) == 3 and operate[2].isdigit():
                    if spider := Spiders.get(operate[1]):
                        self.view.show_spider_urls(spider, start=int(operate[2]))
                elif len(operate) == 4 and operate[2].isdigit() and operate[3].isdigit():
                    if spider := Spiders.get(operate[1]):
                        self.view.show_spider_urls(spider, start=int(operate[2]) - 1, end=int(operate[3]) + 1)
            else:
                command = self.commands.get(spider_name, lambda: printc(f'系统：爬虫 {spider_name} 不存在', RED))
                if command == self.clear:
                    printc('系统：', BLUE, end='')
                    self.clear(lambda: print('请输入爬虫名称进行选择，输入q或者回车返回上一级'))
                else:
                    command()

    def show_log(self):
        self.view.log_help()
        log_command = inputc(f'[{self.user.username}/浏览日志]$ ').strip().split(' ')
        if 0 < len(log_command) < 3:
            if log_command[0] not in Spiders.keys():
                return printc(f'系统：爬虫 {log_command[0]} 不存在', RED)
            spider = Spiders[log_command[0]]
            if len(log_command) == 1:
                spider.logger.display()
            elif len(log_command) == 2:
                if log_command[-1].isdigit():
                    spider.logger.display(int(log_command[-1]))
                else:
                    printc(f'系统：命令 {" ".join(log_command)} 的第2个参数应该是整数', RED)
        else:
            printc('系统：查看日志的命令不正确', RED)

    def find_log(self, spider_name, last_n: str = None):
        if spider_name not in Spiders.keys():
            return printc(f'系统：爬虫 {spider_name} 不存在', RED)
        spider = Spiders[spider_name]
        if last_n:
            if last_n.isdigit():
                last_n = int(last_n)
            else:
                return print(f'系统：{last_n} 并不是规范的整数', RED)
        spider.logger.display(last_n)


if __name__ == '__main__':
    controller = Controller()
    controller.run()
    # controller.spider_config()
