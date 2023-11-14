import json
from view import *
from .auth import getGPASign
from .timer import *


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
        self.qrcodeViewer = QRCodeViewer()

    def request_login(self, username, password):
        try:
            response = requests.post(
                url=f'{BaseAPI}/user/login',
                data={
                    'uname': username,
                    'upwd': password
                }
            )
            self.user.token = response.json().get('token')
            return bool(response.status_code == 200 and response.json()['success']), response.json()['msg']
        except requests.RequestException:
            return False, '当前无法登录，请检查网络服务'
        except Exception as e:
            return False, f'当前无法登录，{e}'

    def request_ip(self):
        try:
            response = requests.get(url=f'{BaseAPI}/user/locate', headers={
                'Authorization': f'Bearer {self.user.token}',
            })
            return response.json()['data']['ip']
        except Exception as e:
            return f'error: {e}'

    def get_max_limit(self):
        try:
            response = requests.get(
                url=f'{BaseAPI}/user/limit',
                headers={
                    'Authorization': f'Bearer {self.user.token}',
                }
            )
            return response.json()['data']
        except requests.RequestException:
            printc(f'系统：当前网络服务有问题', RED)
            return 0,
        except Exception as e:
            printc(f'系统：{e}', RED)
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
            login_state, login_msg = self.request_login(uname, upwd)
            printc('系统：', BLUE, end='')
            print(f'{login_msg}')
            if login_state:
                break
        if not (logs_folder := Path(f'./日志-{uname}/')).exists():
            logs_folder.mkdir()
        self.user.setUser(uname, upwd)
        self.user.setIP(self.request_ip())
        self.user.setTime(current('str'))
        self.user.setLimit(self.get_max_limit())
        self.user.bind(Settings())
        self.main()

    def main(self):
        os.system('cls')
        self.view.menu()
        while True:
            try:
                option = inputc(f'[{self.user.username}]$ ')
                if option.lower() in ('q', '0', 'exit', 'quit'):
                    again = inputc('系统：确认退出？[y|N]$ ', RED)
                    if again.lower() == 'y':
                        for spider in Spiders.values():
                            if spider.state != 'stopped':
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
                    self.show_real_log()
                    self.view.menu()
                elif option == '7':
                    self.view.show_app_info(self.user, len(Spiders))
                elif not option:
                    pass
                elif option.startswith('log '):
                    option = option.split(' ')
                    if len(option) == 2:
                        self.view.find_log(option[1])
                    elif len(option) == 3:
                        self.view.find_log(option[1], option[2])
                elif option.startswith('show '):
                    option = option.split(' ')
                    if len(option) == 2 and (spider := Spiders.get(option[1])):
                        self.view.show_spider_detail(spider)
                elif option.startswith('note '):
                    self.command_urls(option)
                else:
                    command = self.commands.get(option, lambda: printc('系统：输入有误，请重新输入', RED))
                    if command == self.clear:
                        self.clear(self.view.menu)
                    else:
                        command()
            except KeyboardInterrupt:
                again = inputc('系统：确认退出？[y|N]$ ', RED)
                if again.lower() == 'y':
                    for spider in Spiders.values():
                        spider.stop()
                    printc('系统：', BLUE, end='')
                    return print('已退出程序')

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
                print(f'当前配置项为：{config_items[option][2]}, 直接回车可放弃修改')
                if option == 7:
                    printc('提示：循环搜索数量并不是越高越好（推荐20到80）', CYAN)
                value = inputc(f'[{self.user.username}/进程配置]({config_items[option][3]})$ ')
                if not value or value.lower() == 'n':
                    continue
                elif option in (0, 5, 8, 9, 10, 11, 12, 13, 14, 16, 17, 20):
                    value = bool(value == '1' or value == '开启')
                    if option == 12:
                        if value == self.user.settings.get(config_items[13][0], config_items[13][1]) is True:
                            printc('系统：不能与`再评论再收藏`共同设置为开启，这是无意义的行为', RED)
                            continue
                    if option == 13:
                        if value == self.user.settings.get(config_items[12][0], config_items[12][1]) is True:
                            printc('系统：不能与`跳过已收藏`共同设置为开启，这是无意义的行为', RED)
                            continue
                    if option in (12, 13, 14, 16, 17):
                        if not self.user.settings.get(config_items[11][0], config_items[11][1]):
                            printc('系统：使用某些设置前先必须保证`是否评论`开启', RED)
                            continue
                    if option == 17 and value is True:
                        if not self.user.settings.get(config_items[16][0], config_items[16][1]):
                            printc('系统：使用`屏蔽重试`前先必须保证`检查屏蔽开启`开启', RED)
                            continue
                elif option in (2, 3):
                    items = config_items[option][3].split('|')
                    if value.isdigit() and 0 <= int(value) < len(items):
                        value = items[int(value)].split(' ')[-1]
                    else:
                        printc('系统：输入不规范，配置失败', RED)
                        continue
                elif option in (4, 6, 7, 15, 18, 19):
                    if not value.isdigit():
                        printc('系统：输入不规范，配置失败', RED)
                        continue
                    if option == 4 and not (2 <= int(value) <= 999):
                        printc('系统：任务数量只能设置在[2-999]之间', RED)
                        continue
                    if option == 6 and not (2 <= int(value) <= 999):
                        printc('系统：循环间隔分钟数只能设置在[2-999]之间', RED)
                        continue
                    if option == 7 and not (20 <= int(value) <= 200):
                        printc('系统：每次循环的搜索数量只能设置在[20-200]之间', RED)
                        continue
                    if option == 15 and not (1 <= int(value) <= 99):
                        printc('系统：生僻字数量只能设置在[1-99]之间', RED)
                        continue
                    if option == 18 and not (1 <= int(value) <= 9):
                        printc('系统：重试次数只能设置在[1-9]之间', RED)
                        continue
                    if option == 19 and not (1 <= int(value) <= 999):
                        printc('系统：任务间隔时间只能设置在[1-999]之间', RED)
                        continue
                elif option == 21:
                    if not Path(value.strip('"')).exists():
                        printc('系统：文件不存在，配置失败', RED)
                        continue
                    value = Path(value.strip('"')).absolute()
                self.user.settings.set(config_items[option][0], config_items[option][1], str(value))
                self.user.settings.save()
                self.user.settings.update()
                printc('系统：配置修改成功', GREEN)
            elif option.startswith('log '):
                option = option.split(' ')
                if len(option) == 2:
                    self.view.find_log(option[1])
                elif len(option) == 3:
                    self.view.find_log(option[1], option[2])
            elif option.startswith('show '):
                option = option.split(' ')
                if len(option) == 2 and (spider := Spiders.get(option[1])):
                    self.view.show_spider_detail(spider)
            elif option.startswith('note '):
                self.command_urls(option)
            else:
                command = self.commands.get(option, lambda: printc('系统：输入有误，请重新输入', RED))
                if command == self.clear:
                    config_items, length = self.clear(self.view.show_spider_config)
                    print("请输入序号选择配置项，输入q或者回车返回上一级")
                else:
                    command()

    def create_qrcode(self):
        request_qrcode = QrCode(self.user)
        url, qr_id, code = request_qrcode.info()
        if not (url and qr_id and code):
            return False
        printc('系统：', BLUE, end='')
        print('请在5分钟内使用手机扫描二维码')
        self.qrcodeViewer.url(url)
        self.qrcodeViewer.show()
        printc('系统：', BLUE, end='')
        print('扫码并允许登录后，请输入 y 确认')
        if 'y' != inputc(f'[{self.user.username}](y|N)$ ').lower():
            printc('系统：', BLUE, end='')
            print('已经取消创建进程操作')
            return False, None, None
        success, msg, data = request_qrcode.state(qr_id, code)
        if not success:
            printc(f'系统：扫码登录失败，{msg}', RED)
            return False, None, None
        if success and msg != '登录成功':
            printc(f'系统：扫码登录失败，{msg}', RED)
            return False, None, None
        user_id = data['user_id']
        session = data['session']
        return True, user_id, session

    def add_spider(self):
        """
        创建进程方法
        11月14日：不再使用主入口的异常处理，防止程序退出，而是用方法内的try-except进行处理
        :return:
        """
        try:
            self.user.settings.update()
            if not self.user.settings.check():
                return
            state, user_id, session = self.create_qrcode()
            if not state:
                return
            cookies_obj = Cookies().update_cookie('web_session', session)
            printc('系统：', BLUE, end='')
            print('登录成功，请为进程命名(推荐使用数字)，方便后续激活、暂停等操作')
            while True:
                spider_name = inputc(f'[{self.user.username}/添加进程](回车取消)$ ')
                if not spider_name or spider_name.lower() in ('n', 'q', 'quit', 'exit'):
                    printc('系统：', BLUE, end='')
                    return print('用户自行打断了进程创建的过程')
                if spider_name in Spiders.keys():
                    printc(f'系统：进程 {spider_name} 已存在，请重新命名', RED)
                    continue
                if spider_name in self.user.settings.buildWords:
                    printc(f'系统：名字 {spider_name} 属于内置关键字，不可使用', RED)
                    continue
                if (spider_name not in Spiders.keys()) and (spider_name not in self.commands.keys()):
                    break
            spider = Spider(spider_name, self.user, user_id)
            spider.source(cookies_obj)
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
            gpa_s, gpa_t = getGPASign(self.user.settings.gpaKey, create_api)
            post_data = {
                'count': len(Spiders),
                'info': json.dumps(dict(spider), ensure_ascii=False),
                'gpa_s': gpa_s,
                'gpa_t': gpa_t,
            }
            response = spider.api.post(f"{BaseURL}{create_api}", data=post_data)
            if not response['success']:
                return printc(f'系统：创建进程失败 {response["msg"]}', RED)
            # 送进总字典中
            Spiders[spider_name] = spider
            printc('系统：', BLUE, end='')
            print(f'{response["msg"]} 是否激活进程？(默认不激活)')
            is_activate = inputc(f'[{self.user.username}/添加进程](y|N)$ ')
            if is_activate.lower() == 'y':
                spider.start()
        except Exception as e:
            printc(f'系统：创建进程失败，原因 {e}', RED)

    def show_spiders(self):
        spiders = [(name, RunStates[spider.state], spider.success_count, spider.failure_count, spider.finished_count)
                   for
                   name, spider in Spiders.items()]
        if spiders:
            self.view.show_spiders(spiders)
        else:
            printc('系统：', BLUE, end='')
            print('还没有创建任何进程')

    def operate_spider(self):
        printc('系统：', BLUE, end='')
        print('请输入进程名称进行选择，输入q或者回车返回上一级')
        while True:
            spider_name = inputc(f'[{self.user.username}/操作进程]$ ')
            if not spider_name or spider_name.lower() in ('q', 'exit', 'quit'):
                self.clear(self.view.menu)
                break
            if spider := Spiders.get(spider_name):
                printc('系统：', BLUE, end='')
                print('请用户输入操作序号，回车/q/0可取消')
                print('当前状态：', end='')
                printc(RunStates[spider.state], CYAN)
                print('操作序号：1 激活 | 2 暂停 | 3 恢复 | 4 终止 | 5 删除')
                operate = inputc(f'[{self.user.username}/操作进程](选择操作)$ ')
                if not operate or operate in ('0', 'q'):
                    printc('系统：', BLUE, end='')
                    print(f'用户已取消对进程 {spider_name} 操作')
                    continue
                elif operate == '1':
                    if spider.state in ('running', 'paused'):
                        return printc(f'系统：进程 {spider_name} 已激活过了，不可再激活', RED)
                    spider.start()
                elif operate == '2':
                    if spider.state in ('stopped', 'paused'):
                        return printc(f'系统：进程 {spider_name} 已经暂停或者已经终止，不可再暂停', RED)
                    spider.pause()
                elif operate == '3':
                    if spider.state in ('running', 'stopped'):
                        return printc(f'系统：进程 {spider_name} 正在运行或者已经终止，不可再恢复', RED)
                    spider.resume()
                elif operate == '4':
                    if spider.state == 'stopped':
                        return printc(f'系统：进程 {spider_name} 已经终止，不可再终止', RED)
                    spider.stop()
                elif operate == '5':
                    if spider.state != 'stopped':
                        spider.stop()
                    del Spiders[spider_name]
                    printc('系统：', BLUE, end='')
                    return printc(f'进程 {spider_name} 被移除', YELLOW)
                spiders = [(spider.name, RunStates[spider.state], spider.success_count, spider.failure_count,
                            spider.finished_count)]
                self.view.show_spiders(spiders)
            elif spider_name.startswith('show '):
                operate = spider_name.split(' ')
                if len(operate) == 2 and (spider := Spiders.get(operate[1])):
                    self.view.show_spider_detail(spider)
            elif spider_name.startswith('log '):
                operate = spider_name.split(' ')
                if len(operate) == 2:
                    self.view.find_log(operate[1])
                elif len(operate) == 3:
                    self.view.find_log(operate[1], operate[2])
            elif spider_name.startswith('note '):
                self.command_urls(spider_name)
            else:
                command = self.commands.get(spider_name, lambda: printc(f'系统：进程 {spider_name} 不存在', RED))
                if command == self.clear:
                    printc('系统：', BLUE, end='')
                    self.clear(lambda: print('请输入进程名称进行选择，输入q或者回车返回上一级'))
                else:
                    command()

    def command_urls(self, option):
        operate = option.split(' ')
        if len(operate) == 2 and (spider := Spiders.get(operate[1])):
            self.view.show_spider_urls(spider)
        elif len(operate) == 3 and operate[2].isdigit():
            if spider := Spiders.get(operate[1]):
                self.view.show_spider_urls(spider, start=int(operate[2]))
        elif len(operate) == 4 and operate[2].isdigit() and operate[3].isdigit():
            if spider := Spiders.get(operate[1]):
                self.view.show_spider_urls(spider, start=int(operate[2]) - 1, end=int(operate[3]))

    def show_real_log(self):
        self.view.real_log_help()
        while True:
            log_command = inputc(f'[{self.user.username}/实时日志]$ ').strip().split(' ')
            if log_command[0].lower() in ('q', '', 'exit', 'quit', '0'):
                break
            if log_command[0] in self.commands.keys():
                command = self.commands[log_command[0]]
                if command == self.clear:
                    self.clear(self.view.real_log_help)
                else:
                    command()
                continue
            if log_command[0] == 'show':
                if len(log_command) == 2 and (spider := Spiders.get(log_command[1])):
                    self.view.show_spider_detail(spider)
                continue
            elif log_command[0] == 'log':
                if len(log_command) == 2:
                    self.view.find_log(log_command[1])
                elif len(log_command) == 3:
                    self.view.find_log(log_command[1], log_command[2])
                continue
            elif log_command[0] == 'note':
                self.command_urls(' '.join(log_command))
                continue
            if log_command[0] not in Spiders.keys():
                printc(f'系统：进程 {log_command[0]} 不存在', RED)
                continue
            spider = Spiders[log_command[0]]
            printc('系统：', BLUE, end='')
            print(f'正在接入进程 {spider.name} 的日志对象中...')
            time.sleep(1)
            if len(log_command) == 1:
                spider.logger.tail()
            elif len(log_command) == 2 and log_command[1].isdigit():
                spider.logger.tail(n=int(log_command[1]))
            elif len(log_command) == 3 and log_command[1].isdigit() and log_command[2].isdigit():
                spider.logger.tail(n=int(log_command[1]), interval=int(log_command[2]))
