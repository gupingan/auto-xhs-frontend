import getpass
from model import *


class View:
    def __init__(self):
        self.settings = Settings()

    def help(self):
        commands = [
            (' 1', 'clear', '清空屏幕并显示当前的菜单'),
            (' 2', 'cls', '同上'),
            (' 3', 'menu', '显示功能的主菜单'),
            (' 4', 'main|home', '同上'),
            (' 5', 'exit|quit', '退出当前输入状态'),
            (' 6', 'log 进程名', '查看对应进程的全部日志'),
            (' ', 'log 进程名 [n]', '查看对应进程的最新n行日志'),
            (' 7', 'show 进程名', '查看对应进程的详细信息和状况'),
            (' 8', 'note 进程名', '查看对应进程的所有笔记信息'),
            (' ', 'note 进程名 [n]', '查看对应进程的前n条笔记信息'),
            (' ', 'note 进程名 [a] [b]', '查看对应进程的从第a到b条笔记信息'),
        ]
        printc('帮助：', BLUE)
        print('\t操作十分简单，注意看提示')
        print('\t注意输入指令/命令之后系统所反馈的信息')
        printc('[1] 快速入门：', GREEN)
        print('\t修改配置 > 添加进程 > 操作进程(去激活)')
        printc('[2] 指令：', GREEN)
        print(tabulate(commands, tablefmt='plain'))

    def validate_input(self, username, password):
        min_length = 4
        max_length = 20
        username_pattern = r'^\w+$'  # 仅允许英文字符、数字和下划线
        password_pattern = r'^[\w!@#$%^&*()-+=]+$'  # 仅允许常见密码字符
        if not (min_length <= len(username) <= max_length) or not re.match(username_pattern, username):
            printc('系统：', BLUE, end='')
            print(f"用户名仅支持英文字符、数字和下划线，长度应在 {min_length}-{max_length} 个字符之间。")
            return False
        if not (min_length <= len(password) <= max_length) or not re.match(password_pattern, password):
            printc('系统：', BLUE, end='')
            print(f"密码仅支持常见密码字符，长度应在 {min_length}-{max_length} 个字符之间。")
            return False
        return True

    def login(self):
        printc("GPA终端登录系统", CYAN + BOLD)
        printc("账 号: ", YELLOW, end="")
        username = input()
        password = getpass.getpass(f"{YELLOW}密 码：{RESET}")
        return username, password

    def menu(self):
        printc('菜  单'.center(25), BRIGHT_CYAN)
        menu_data = [
            ["1 修改配置", "2 添加进程"],
            ["3 查看进程", "4 操作进程"],
            ["5 修改进程", "6 实时日志"],
            ["7 应用信息", "q 退出程序"]
        ]
        print(tabulate(menu_data, tablefmt='fancy_grid'))

    def show_app_info(self, user, used_limit):
        printc('应用信息'.center(42), BRIGHT_CYAN)
        user_data = [
            ["用户名", user.username, '额度', f'{used_limit} / {user.max_limit}'],
            ['IP地址', user.ip, '登陆时间', user.login_time],
            ['版本', f'auto-xhs v{self.settings.version}', "版本号", self.settings.version_number],
        ]
        print(tabulate(user_data, tablefmt='plain'))

    def show_spider_config(self):
        self.settings.update()
        config_items = [
            ("SearchConfig", "is-multy", "多搜索词", "0 关闭|1 开启"),
            ("SearchConfig", "search-key", "搜索词", "多搜索词请使用|间隔"),
            ("SearchConfig", "sort-type", "排序类型", "0 综合|1 最热|2 最新"),
            ("SearchConfig", "note-type", "笔记类型", "0 综合|1 视频|2 图文|3 先图文后视频"),
            ("SearchConfig", "task-count", "任务数量", "输入整数"),
            ("SearchConfig", "cyclic-mode", "循环模式", "0 关闭|1 开启"),
            ("SearchConfig", "interval-minute", "循环间隔分钟数", "输入整数"),
            ("SearchConfig", "cyclic-search-count", "循环搜索数量", "输入整数"),
            ("TaskConfig", "is-like", "是否点赞", "0 关闭|1 开启"),
            ("TaskConfig", "is-collect", "是否收藏", "0 关闭|1 开启"),
            ("TaskConfig", "is-follow", "是否关注", "0 关闭|1 开启"),
            ("TaskConfig", "is-comment", "是否评论", "0 关闭|1 开启"),
            ("TaskConfig", "is-skip-collect", "跳过已收藏", "0 关闭|1 开启"),
            ("TaskConfig", "is-again-comment-collect", "再评论再收藏", "0 关闭|1 开启"),
            ("TaskConfig", "is-random-rare-word", "是否随机生僻字", "0 关闭|1 开启"),
            ("TaskConfig", "rare-word-count", "生僻字数量", "输入整数"),
            ("TaskConfig", "is-check-shield", "是否检查屏蔽", "0 关闭|1 开启"),
            ("TaskConfig", "is-shield-retry", "是否屏蔽后重试", "0 关闭|1 开启"),
            ("TaskConfig", "retry-count", "重试次数", "输入整数"),
            ("TimeConfig", "task-interval-time", "任务间隔时间", "输入整数"),
            ("TimeConfig", "is-random-interval-time", "是否随机间隔时间", "0 关闭|1 开启"),
            ("TimeConfig", "comment-path", "评论路径", "请粘贴文件的绝对路径")
        ]
        config_meanings = tuple((meaning for _, _, meaning, _ in config_items))
        config_values = list((self.settings.get(section, option) for section, option, _, _ in config_items))
        state = {False: '关闭', True: '开启'}
        for i, config_value in enumerate(config_values):
            if isinstance(config_value, bool):
                config_values[i] = state[config_value]
        config_values[21] = f"{View.truncate_string(Path(config_values[21]).name, 24)}" if Path(
            config_values[21]).exists() else '不合法文件'
        configs = zip(config_meanings, config_values)
        headers = ('序号', '设置项', '值')
        print(tabulate(configs, headers=headers, showindex=True, tablefmt="fancy_grid"))
        return config_items, len(config_items)

    def show_spiders(self, spiders: list):
        headers = ('序号', '名字', '状态', '成功评论', '失败评论', '已完成')
        print(tabulate(spiders, headers=headers, showindex=True, tablefmt="fancy_grid"))
        printc('提示：', BLUE, end='')
        print('你可以使用命令`show 名字`查看指定进程的更详细资料')

    def real_log_help(self):
        printc('系统：', BLUE, end='')
        print('输入q或者回车返回上一级')
        print('      [进程名] [最新数量（默认8）] [多少秒刷新（默认3）]')
        print('最新数量 推荐 3~20，刷新秒数不要过短过长 推荐 3~10 ')
        print('      示例：10086 表示每3秒刷新进程10086的最新8条日志')
        print('      示例：10086 10 表示每3秒刷新进程10086的最新10条日志')
        print('      示例：10086 10 6 表示每6秒刷新进程10086的最新10条日志')

    def get_spider_info(self, spider):
        return [
            ('名称', spider.name, '状态', RunStates[spider.state]),
            ('小红书编号', spider.userId, '生僻字引擎',
             f'GPA-Append {spider.rareWordCount} {"开启" if spider.isRandomRareWord else "关闭"}'),
            ('搜索词', spider.searchKey.replace('|', '、'), '循环模式',
             f'开启 每隔{spider.intervalMinute}分钟搜寻{spider.cyclicSearchCount}条' if spider.cyclicMode else '关闭'),
            ('检查屏蔽', '开启' if spider.isCheckShield else '关闭', '屏蔽重试',
             f'开启(最多{spider.retryCount}次)' if spider.isShieldRetry else '关闭'),
            ('总进度', f'{spider.finished_count} / {spider.taskCount}', '跳过已收藏', spider.skip_comment_count),
            ('评论成功量', spider.success_count, '评论失败量', spider.failure_count),
        ]

    def show_spider_detail(self, spider):
        detail_info1 = self.get_spider_info(spider)
        printc('【1】基本信息：', BRIGHT_CYAN)
        print(tabulate(detail_info1, tablefmt="fancy_grid"))
        printc('Session：', BLUE, end='')
        print(spider.session)
        printc('日志文件路径：', YELLOW, end='')
        print(spider.logger_path.absolute())
        printc('评论文件路径：', GREEN, end='')
        print(spider.commentPath)
        printc('【2】任务信息：', BRIGHT_CYAN)
        print('    搜索笔记 > ', end='')
        print(' > '.join([str(task) for task in spider.tasks]))
        if spider.isRandomIntervalTime:
            print(f'    每个任务环节之间间隔 1 ~ {spider.intervalTime} 秒')
        else:
            print(f'    每个任务环节之间间隔 {spider.intervalTime} 秒')

        saySkipCollect = '并且需要跳过已收藏的不评论。' if spider.isSkipCollect else ''
        sayAgainCommentCollect = '同时评论前需要取消已收藏的，然后再评论再收藏。' if spider.isAgainCommentCollect else ''
        printc('【3】简述：', BRIGHT_CYAN, end='')
        if spider.noteType == '先图文后视频':
            print(
                f'进程 {spider.name} 由用户 {spider.user.username} 在 {spider.create_time} 创建，该进程搜索的目标'
                f'先是排序{spider.sortType}的与{spider.searchKey.replace("|", "、")}相关的图文笔记，然后就是视频笔记，'
                f'总任务量是{spider.taskCount}个，需要{"点赞、" if spider.isLike else ""}{"关注、" if spider.isFollow else ""}'
                f'{"收藏、" if spider.isCollect else ""}{"评论，" if spider.isComment else ""}' + saySkipCollect + sayAgainCommentCollect)
        else:
            print(
                f'进程 {spider.name} 由用户 {spider.user.username} 在 {spider.create_time} 创建，该进程搜索的目标'
                f'是排序{spider.sortType}的与{spider.searchKey.replace("|", "、")}相关的{spider.noteType}笔记，'
                f'总任务量是{spider.taskCount}个，需要{"点赞、" if spider.isLike else ""}{"关注、" if spider.isFollow else ""}'
                f'{"收藏、" if spider.isCollect else ""}、{"评论，" if spider.isComment else ""}' + saySkipCollect + sayAgainCommentCollect)

    def show_spider_urls(self, spider, start: int = -1, end: int = None):
        urls = spider.searcher.urls
        headers = ["序号", "笔记ID", "类型", "状态"]
        state = {False: '未完成', True: '已完成'}
        data = [(i + 1, View.truncate_string(note['noteId'], 24), note['type'], state[note['state']]) for i, note in
                enumerate(urls)]
        if not end:
            if start > 0:
                print(tabulate(data[:start], headers=headers, tablefmt='fancy_grid'))
            elif start < 0:
                print(tabulate(data, headers=headers, tablefmt='fancy_grid'))
        else:
            if end > start:
                print(tabulate(data[start:end], headers=headers, tablefmt='fancy_grid'))

    def find_log(self, spider_name, last_n: str = None):
        if spider_name not in Spiders.keys():
            return printc(f'系统：进程 {spider_name} 不存在', RED)
        spider = Spiders[spider_name]
        if last_n:
            if last_n.isdigit():
                last_n = int(last_n)
            else:
                return print(f'系统：{last_n} 并不是规范的整数', RED)
        spider.logger.display(last_n)

    @staticmethod
    def truncate_string(s, max_len):
        if len(s) > max_len:
            half_len = (max_len - 3) // 2
            return s[:half_len] + '...' + s[-half_len:]
        return s
