import configparser
from pathlib import Path


class Settings:
    def __init__(self, defaults=None, filename='settings.ini'):
        self.gpaKey = '&71)26eb3h5j%6n*fk9%w*zvimf0ccl-2p9$ifo()n$pq!xyu9'
        self.version_number = 4
        self.version = '2.2'
        self.xhsBaseURL = "https://www.xiaohongshu.com/explore/"
        self.buildWords = ('clear', 'cls', 'menu', 'main', 'home', 'exit',
                           'quit', 'log', 'show', 'note')
        self.config = configparser.ConfigParser(defaults=defaults)
        self.home = Path.home()
        self.ini_file = Path(filename)
        if not self.ini_file.exists():
            self.create()
        self.config.read(self.ini_file, encoding="utf8")

    def update(self):
        self.config.read(self.ini_file, encoding="utf8")

    def get(self, section, option, fallback=None):
        result = self.config.get(section, option, fallback=fallback)
        if result == 'True':
            return True
        if result == 'False':
            return False
        return result

    def set(self, section, option, value):
        self.config.set(section, option, str(value))

    def create(self):
        self.config['SearchConfig'] = {
            'is-multy': 'False',
            'search-key': '',
            'sort-type': '最新',
            'note-type': '先图文后视频',
            'task-count': '200',
            'cyclic-mode': 'True',
            'interval-minute': '30',
            'cyclic-search-count': '20',
        }
        self.config['TaskConfig'] = {
            'is-like': 'False',
            'is-collect': 'True',
            'is-follow': 'False',
            'is-comment': 'True',
            'is-skip-collect': 'True',
            'is-again-comment-collect': 'False',
            'is-random-rare-word': 'False',
            'rare-word-count': '1',
            'is-check-shield': 'True',
            'is-shield-retry': 'False',
            'retry-count': '3',
        }
        self.config['TimeConfig'] = {
            'task-interval-time': '8',
            'is-random-interval-time': 'True',
            'comment-path': '',
        }
        with open(self.ini_file, 'w', encoding='utf8') as configfile:
            self.config.write(configfile)

    def save(self):
        with open(self.ini_file, 'w', encoding='utf8') as configfile:
            self.config.write(configfile)

    def check(self):
        if self.get('TaskConfig', 'is-again-comment-collect') == self.get('TaskConfig', 'is-skip-collect') is True:
            print('系统：`跳过已收藏`不能与`再评论再收藏`同时开启，这是无意义的行为')
            return False
        if self.get('TaskConfig', 'is-skip-collect') or \
                self.get('TaskConfig', 'is-again-comment-collect') or \
                self.get('TaskConfig', 'is-random-rare-word') or \
                self.get('TaskConfig', 'is-check-shield') or \
                self.get('TaskConfig', 'is-shield-retry'):
            if not self.get('TaskConfig', 'is-comment'):
                print('系统：使用某些设置前先必须保证`是否评论`开启')
                return False
        if self.get('TaskConfig', 'is-shield-retry'):
            if not self.get('TaskConfig', 'is-check-shield'):
                print('系统：使用`屏蔽重试`前先必须保证`检查屏蔽开启`开启')
                return False
        if not (2 <= int(self.get('SearchConfig', 'task-count')) <= 999):
            print('系统：任务数量只能设置在[2-999]之间')
            return False
        if not (2 <= int(self.get('SearchConfig', 'interval-minute')) <= 999):
            print('系统：循环间隔分钟数只能设置在[2-999]之间')
            return False
        if not (20 <= int(self.get('SearchConfig', 'cyclic-search-count')) <= 200):
            print('系统：每次循环的搜索数量只能设置在[20-200]之间')
            return False
        if not (1 <= int(self.get('TaskConfig', 'rare-word-count')) <= 99):
            print('系统：生僻字数量只能设置在[1-99]之间')
            return False
        if not (1 <= int(self.get('TaskConfig', 'retry-count')) <= 9):
            print('系统：重试次数只能设置在[1-9]之间')
            return False
        if not (1 <= int(self.get('TimeConfig', 'task-interval-time')) <= 999):
            print('系统：任务间隔时间只能设置在[1-999]之间')
            return False
        if not self.get('SearchConfig', 'search-key'):
            print('系统：请先在配置中设置搜索词')
            return False
        if not self.get('TimeConfig', 'comment-path'):
            print('系统：请先在配置中设置评论文件的路径')
            return False
        if not Path(self.get('TimeConfig', 'comment-path')).exists():
            print('系统：评论素材文件不存在，请检查路径是否正确！')
            return False
        return True

    def print_set(self):
        for section, section_v in self.config.items():
            for k, v in section_v.items():
                print(f"self.settings.set(\"{section}\", \"{k}\", f\"\")")

    def print_get(self):
        for section, section_v in self.config.items():
            for k, v in section_v.items():
                print(f"self.settings.get(\"{section}\", \"{k}\")")
