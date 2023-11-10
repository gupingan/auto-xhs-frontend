import threading
import time
from datetime import datetime
from pathlib import Path
from .types import NoteType, SortType
from .api import API
from .user import User
from .logger import CSVLogger

BaseAPI = "http://127.0.0.1:5000/api"
BaseURL = "http://127.0.0.1:5000"


class Spider(threading.Thread):
    def __init__(self, name, user: User = None, userId: str = None):
        super().__init__()
        # 爬虫信息
        self.name = name
        self.state = "stopped"
        self.userId = userId
        self.success_count = 0
        self.failure_count = 0
        self.skip_comment_count = 0
        self.finished_count = 0
        self.tasks = []
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 爬虫绑定
        self.user = user
        self.api = API(self.user.token)
        self.logger_path = Path(f"./日志-{self.user.username}/{self.name}.csv")
        fieldnames = ["时间", "级别", '笔记编号', "信息"]
        self.logger = CSVLogger(str(self.logger_path), fieldnames)
        self.searcher = None
        self.session = None
        self.cookies = None
        # 爬虫配置
        self.searchKey = self.user.settings.get('SearchConfig', 'search-key')
        self.sortType = self.user.settings.get('SearchConfig', 'sort-type')
        self.noteType = self.user.settings.get('SearchConfig', 'note-type')
        self.singleTaskCount = int(self.user.settings.get('SearchConfig', 'task-count'))
        self.taskCount = self.singleTaskCount * len(self.searchKey.split('|'))
        self.cyclicMode = self.user.settings.get('SearchConfig', 'cyclic-mode')
        self.intervalMinute = int(self.user.settings.get('SearchConfig', 'interval-minute'))
        self.cyclicSearchCount = self.user.settings.get('SearchConfig', 'cyclic-search-count')
        self.isLike = self.user.settings.get('TaskConfig', 'is-like')
        self.isCollect = self.user.settings.get('TaskConfig', 'is-collect')
        self.isFollow = self.user.settings.get('TaskConfig', 'is-follow')
        self.isComment = self.user.settings.get('TaskConfig', 'is-comment')
        self.isSkipCollect = self.user.settings.get('TaskConfig', 'is-skip-collect')
        self.isAgainCommentCollect = self.user.settings.get('TaskConfig', 'is-again-comment-collect')
        self.isRandomRareWord = self.user.settings.get('TaskConfig', 'is-random-rare-word')
        self.rareWordCount = int(self.user.settings.get('TaskConfig', 'rare-word-count'))
        self.isCheckShield = self.user.settings.get('TaskConfig', 'is-check-shield')
        self.isShieldRetry = self.user.settings.get('TaskConfig', 'is-shield-retry')
        self.retryCount = int(self.user.settings.get('TaskConfig', 'retry-count'))
        self.isRandomIntervalTime = self.user.settings.get('TimeConfig', 'is-random-interval-time')
        self.intervalTime = int(self.user.settings.get('TimeConfig', 'task-interval-time'))
        self.commentPath = self.user.settings.get('TimeConfig', 'comment-path')
        # 爬虫初始化
        self.daemon = True
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.stop_event = threading.Event()

    def __iter__(self):
        yield '名称', self.name
        yield '小红书编号', self.userId
        yield '搜索词', self.searchKey.split('|')
        yield '笔记类型', self.noteType
        yield '排序类型', self.sortType
        yield '循环模式', '开启' if self.cyclicMode else '关闭'
        yield '生僻字引擎', f'GPA-Append {self.rareWordCount} {"开启" if self.isRandomRareWord else "关闭"}'
        yield '检查屏蔽', '开启' if self.isCheckShield else '关闭'
        yield '屏蔽重试', f'开启(最多{self.retryCount}次)' if self.isShieldRetry else '关闭'
        yield '日志文件路径', str(self.logger_path.absolute())
        if Path(self.commentPath).exists():
            with open(self.commentPath, 'r', encoding='utf8') as fr:
                comments = fr.read()
        else:
            comments = ''
        yield '评论文件路径', self.commentPath
        yield '评论素材', comments.split('\n')
        yield '总任务量', self.taskCount
        yield 'session', self.session
        yield '是否点赞', '开启' if self.isLike else '关闭'
        yield '是否关注', '开启' if self.isFollow else '关闭'
        yield '是否收藏', '开启' if self.isCollect else '关闭'
        yield '再评论再收藏', '开启' if self.isAgainCommentCollect else '关闭'
        yield '跳过已收藏', '开启' if self.isSkipCollect else '关闭'

    def append_task(self, task):
        self.tasks.append(task)

    def source(self, cookies):
        self.session = cookies.get_cookie('web_session')
        self.cookies = str(cookies)
        self.api.headers['Cookies'] = self.cookies
        self.searcher = Searcher(self)

    def run(self):
        self.state = 'running'
        self.logger.log({"信息": "进程已经激活，开始运行"})
        self.execute()
        self.logger.log({"信息": "进程已经运行完毕"})
        self.state = 'stopped'

    def execute(self):
        self.load_task()
        self.searcher.run()
        if not self.searcher.urls:
            return self.logger.log({"信息": "进程无有效链接，退出中..."})
        cyclic_count = 1
        while not self.stop_event.is_set():
            self.load_task()
            self.pause_event.wait()
            self.tasks[0].handle(self)
            time.sleep(1)
            if all(map(lambda x: x['state'], self.searcher.urls)):
                if self.cyclicMode:
                    cyclic_count += 1
                    self.logger.log({'信息': f'正在准备第 {cyclic_count} 次循环搜索'})
                    time.sleep(self.intervalMinute * 60)
                    self.searcher.update()
                else:
                    break

    def load_task(self):
        if not self.tasks:
            return self.logger.log({"信息": "进程未部署任务，退出中..."})
        for i in range(0, len(self.tasks) - 1):
            self.tasks[i].setNext(self.tasks[i + 1])
        if self.tasks:
            self.tasks[-1].setNext(None)

    def pause(self):
        self.state = "paused"
        self.pause_event.clear()

    def resume(self):
        self.state = "running"
        self.pause_event.set()

    def stop(self):
        self.state = "stopped"
        self.stop_event.set()
        self.pause_event.set()


class Searcher:
    def __init__(self, spider: Spider):
        self.spider = spider
        self.api = API(self.spider.user.token, cookies=self.spider.cookies)
        self.search_keys = self.spider.searchKey.split('|')
        self.sort_type = SortType[self.spider.sortType].value
        self.note_type = NoteType[self.spider.noteType].value
        self.needs = self.spider.singleTaskCount
        self.update_count = self.spider.cyclicSearchCount
        self.urls: list = []

    def run(self):
        try:
            data = {
                'keywords': self.search_keys,
                'sort_type': self.sort_type,
                'note_type': self.note_type,
                'needs': self.needs,
            }
            response = self.api.post(f'{BaseAPI}/note/search', data)
            self.urls = response['data']
            self.spider.taskCount = len(self.urls)
            self.spider.logger.log({'信息': f'搜索器采集了 {self.spider.taskCount} 条笔记'})
        except Exception as e:
            self.spider.logger.log({'信息': f'搜索器获取数据异常: {e}'}, level='error')

    def update(self):
        try:
            data = {
                'keywords': self.search_keys,
                'sort_type': self.sort_type,
                'note_type': self.note_type,
                'needs': self.update_count,
            }
            response = self.api.post(f'{BaseAPI}/note/search', data)
            noteIds = map(lambda x: x['noteId'], self.urls)
            update_count = 0
            for note in response['data']:
                if note['noteId'] not in noteIds:
                    update_count += 1
                    self.urls.append(note)
            self.spider.taskCount = len(self.urls)
            self.spider.logger.log({'信息': f'本次循环增加了 {update_count} 条新笔记'})
        except Exception as e:
            self.spider.logger.log({'信息': f'搜索器更新数据异常: {e}'}, level='error')
