"""
@File: model.py
@Author: 顾平安
@Created: 2023/11/5 16:10
@Description: Created in 咸鱼-自动化-AutoXhs.
"""
import csv
import functools
import hashlib
import hmac
import random
import re
import threading
import time
import pytz
import requests
from datetime import datetime
from enum import Enum
from tabulate import tabulate
from settings import Settings
from pathlib import Path

banned_words = ('王', '江', '周', '胡', '刘', '李', '吴', '毛', '温', '习', '贺', '贾', '彭', '潭', '轭', '馿',
                '马驰.*新加坡|新加坡.*马驰', '自由光诚', '陈光诚事件', '光诚.*沂南|沂南.*光诚',
                '陈光诚.*使馆|使馆.*陈光诚', '职称英语.*答案|答案.*职称英语', '公务员.*答案|答案.*公务员', '薄瓜瓜',
                '海伍德', '尼尔伍德', 'heywood', 'neil.*wood|wood.*neil', '天线宝宝.*康师傅|康师傅.*天线宝宝',
                '天线宝宝.*方便面|方便面.*天线宝宝', '天线宝宝.*轮胎|轮胎.*天线宝宝', '轮胎.*方便面|方便面.*轮胎',
                '政变', '枪声', '戒严', '3\\.19', '北京事件', '北京.*出事了|出事了.*北京', '北京怎么了', '不厚', '薄督',
                '谷开来', '重庆', '叶城.*砍杀|砍杀.*叶城', '连承敏', '弟弟.*睡|睡.*弟弟',
                '要有光.*要有诚|要有诚.*要有光', '杨杰', '陈刚', '山水文园', '跑官', '移动.*十年兴衰|十年兴衰.*移动',
                '陈坚', '戴坚', '冯珏', '罗川', '马力', '盛勇', '谢岷', '谢文', '杨希', '叶兵', '张斌', '陈瑞卿',
                '高念书', '华如秀', '鲁向东', '曲乃杰', '孙静晔', '涂志森', '于剑鸣', '张晓明', '赵志强', '郑建源',
                '先皇', '太上皇', '蛤蟆', '驾崩', '丘小雄', '公诉', '右派', '增城', '暴动', '宣言', '莫日根',
                '内蒙古.*抗议|抗议.*内蒙古', '西乌旗', '方滨兴', 'moli', '麦当劳', '天府', '人民公园', '广场', '埃及',
                '突尼斯', '茉莉', 'jasmine.*revolution|revolution.*jasmine', '集会', '革命', '齐鲁银行', '公开信',
                '高考时间', '诺贝尔和平奖', '被就业', '小屋', '日记', '鲁昕', '天安.*事件|事件.*天安',
                '1989.*天安門|天安門.*1989', '天安门', '八九', '六四', '六 四', '六\\.四', '平反64', '5月35日',
                '5月35号', '89动乱', '89.*学生动乱|学生动乱.*89', '89.*学生运动|学生运动.*89',
                '64.*学生运动|学生运动.*64', '64.*镇压|镇压.*64', '64.*真相|真相.*64', '64memo', 'tiananmen', '8964',
                '学潮', '罢课', '民运', '学运', '学联', '学自联', '高自联', '工自联', '民联', '民阵', '中国民主党',
                '中国民主正义党', '中国民主运动', '世纪中国基金会', '坦克人', '挡坦克', 'tankman', '木犀地', '维园晚会',
                'blood is on the square', '姜维平', '艾未未', '艾末末', '路青', '发课', '余杰', '辛子陵', '茅于轼',
                '铁流', 'liu.*xiaobo|xiaobo.*liu', '蟹农场', '陈西', '谭作人', '高智晟', '冯正虎', '丁子霖', '唯色',
                '焦国标', '何清涟', '耀邦', '紫阳', '方励之', '严家其', '鲍彤', '鮑彤', '鲍朴', '柴玲', '乌尔凯西',
                '封从德', '炳章', '苏绍智', '陈一谘', '韩东方', '辛灏年', '曹长青', '陈破空', '盘古乐队', '盛雪',
                '伍凡', '魏京生', '司徒华', '黎安友', '防火长城', 'great.*firewall|firewall.*great',
                'gfw.*什么|什么.*gfw', '国家防火墙', '翻墙', '代理', 'vpn.*免费|免费.*vpn', 'vpn.*下载|下载.*vpn',
                'vpn.*世纪|世纪.*vpn', 'hotspot.*shield|shield.*hotspot', '无界', 'ultrasurf', '^freenet', 'safeweb',
                '动态网', '花园网', '^cache', '阅后即焚', '法轮', 'falun', '明慧', 'minghui', '退党', '三退', '九评',
                'nine commentaries', '洪吟', '神韵艺术', '神韵晚会', '人民报', 'renminbao', '纪元', '^dajiyuan',
                'epochtimes', '新唐人', 'ntdtv', 'ndtv', '新生网', '^xinsheng', '正见网', 'zhengjian', '追查国际',
                '真善忍', '法会', '正念', '经文', '天灭', '天怒', '讲真相', '马三家', '善恶有报', '活摘器官',
                '群体灭绝', '中功', '张宏堡', '地下教会', '冤民大同盟', '达赖', '藏独', 'freetibet', '雪山狮子',
                '西藏流亡政府', '青天白日旗', '民进党', '洪哲胜', '独立台湾会', '台湾政论区', '台湾自由联盟',
                '台湾建国运动组织', '台湾.*独立联盟|独立联盟.*台湾', '新疆.*独立|独立.*新疆', '东土耳其斯坦',
                'east.*turkistan|turkistan.*east', '世维会', '迪里夏提', '美国之音', '自由亚洲电台', '记者无疆界',
                '维基解密.*中国|中国.*维基解密', 'facebook', 'twitter', '推特', '新京报', '世界经济导报',
                '中国数字时代', '^ytht', '新语丝', '^creaders', '^tianwang', '中国.*禁闻|禁闻.*中国', '阿波罗网',
                '阿波罗新闻', '大参考', '^bignews', '多维', '看中国', '博讯', '^boxun', 'peacehall', '^hrichina',
                '独立中文笔会', '华夏文摘', '开放杂志', '大家论坛', '华夏论坛', '中国论坛', '木子论坛', '争鸣论坛',
                '大中华论坛', '反腐败论坛', '新观察论坛', '新华通论坛', '正义党论坛', '热站政论网', '华通时事论坛',
                '华语世界论坛', '华岳时事论坛', '两岸三地论坛', '南大自由论坛', '人民之声论坛', '万维读者论坛',
                '你说我说论坛', '东西南北论坛', '东南西北论谈', '知情者', '红太阳的陨落', '和谐拯救危机', '血房',
                '一个孤僻的人', '零八.*宪章|宪章.*零八', '08.*宪章|宪章.*08', '八宪章', '8宪章',
                '零八.*县长|县长.*零八', '08县长', '淋巴县长', '我的最后陈述', '我没有敌人', '河殇', '天葬', '黄祸',
                '我的奋斗', '历史的伤口', '改革.*历程|历程.*改革', '国家的囚徒', 'prisoner of the state',
                '改革年代的政治斗争', '改革年代政治斗争', '关键时刻', '超越红墙', '梦萦未名湖', '一寸山河一寸血',
                '政治局常委内幕', '北国之春', '北京之春', '中国之春', '东方红时空', '纳米比亚', '婴儿汤', '泄题',
                '罢餐', '月月', '代开.*发票|发票.*代开', '钓鱼岛', '^triangle', '女保镖', '玩ps', '玩photoshop',
                'chinese people eating babies', '开枪', '迫害', '酷刑', '邪恶', '洗脑', '网特', '内斗', '党魁',
                '文字狱', '一党专政', '一党独裁', '新闻封锁', '老人政治', '^freedom', '^freechina', '反社会',
                '维权人士', '维权律师', '异见人士', '异议人士', '地下刊物', '高瞻', 'غا', '共产', '共铲党', '共残党',
                '共惨党', '共匪', '赤匪', '中共', '中宣', '真理部', '十八大', '18大', '太子', '上海帮', '团派',
                '北京当局', '裆中央', '九常委', '九长老', '锦涛', '家宝', '影帝', '近平', '回良玉', '汪洋', '张高丽',
                '俞正声', '徐才厚', '郭伯雄', '熙来', '梁光烈', '孟建柱', '戴秉国', '马凯', '令计划', '韩正', '章沁生',
                '陈世炬', '泽民', '贼民', '邓小平', '庆红', '罗干', '假庆淋', 'hujin', 'wenjiabao', 'xijinping',
                'likeqiang', 'zhouyongkang', 'lichangchun', 'wubangguo', 'heguoqiang', 'jiaqinglin', 'jiangzemin',
                'xjp', 'jzm', '色情', '花花公子', 'tits', 'boobs', '^\\s*海峰\\s*$', '^\\s*威视公司\\s*$',
                '^\\s*nuctech\\s*$', '^\\s*逍遥游\\s*$', '^\\s*自由门\\s*$', '^\\s*自由門\\s*$', '^\\s*自由之门\\s*$',
                '^\\s*freegate\\s*$', '^\\s*freegate download\\s*$', '^\\s*download freegate\\s*$',
                '^\\s*自由门下载\\s*$', '^\\s*自由門下載\\s*$', '^\\s*無界瀏覽\\s*$', '^\\s*無界浏览\\s*$',
                '^\\s*动网通\\s*$', '^\\s*dynaweb\\s*$', '^\\s*dongtaiwang\\s*$')

states = {
    'running': '运行中',
    'paused': '已暂停',
    'stopped': '已终止'
}

Spiders = {}
SpidersLock = threading.Lock()


def generateGPAValues(secret_key, api_path):
    gpa_t = int(time.mktime(datetime.now(pytz.utc).timetuple()))
    message = f"{api_path}:{gpa_t}"
    gpa_s = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return gpa_s, gpa_t


class CSVLogger:
    def __init__(self, file_name, fieldnames, mode="a"):
        self.file_name = file_name
        self.fieldnames = fieldnames
        self.mode = mode
        self.__init_csv()

    def __init_csv(self):
        with open(self.file_name, mode="w", newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()

    def log(self, data: dict, level: str = "info"):
        with open(self.file_name, mode=self.mode, newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            data["时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["级别"] = level
            writer.writerow(data)

    def read_csv(self):
        with open(self.file_name, mode='r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            data = [row for row in reader]
        return data

    @staticmethod
    def truncate_string(s, max_len):
        if len(s) > max_len:
            half_len = (max_len - 3) // 2
            return s[:half_len] + '...' + s[-half_len:]
        return s

    def display(self, last_n=None):
        data = self.read_csv()
        headers = data[0]
        table_data = data[1:]
        if last_n:
            table_data = table_data[-last_n:]
        for row_index in range(len(table_data)):
            table_data[row_index][2] = CSVLogger.truncate_string(
                table_data[row_index][2], 24
            )
            table_data[row_index][3] = CSVLogger.truncate_string(
                table_data[row_index][3], 15
            )
        print(f'日志数量： {len(table_data)} 条')
        print(tabulate(table_data, headers=headers, tablefmt='grid'))


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


class User:
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.settings = Settings()
        self.token = None
        self.max_limit = 0

    def set(self, username: str, password: str):
        self.username = username
        self.password = password


class QrCode:
    def __init__(self, user: User = None):
        self.user = user
        self.settings = Settings()
        self.info_api = f'{self.settings.baseAPI}/qrcode/info'
        self.state_api = f'{self.settings.baseAPI}/qrcode/state'
        self.api = API(self.user.token)

    def get_info(self):
        try:
            response = self.api.get(self.info_api)
            return response['data']['url'], response['data']['qr_id'], response['data']['code']
        except Exception as e:
            print(f'系统：获取二维码信息失败，错误信息：{e}')
            return None, None, None

    def get_state(self, qr_id, code):
        try:
            params = {'qrId': qr_id, 'code': code}
            response = self.api.get(self.state_api, params)
            return response['success'], response['msg'], response['data']
        except Exception as e:
            print(f'系统：获取二维码状态失败，错误信息：{e}')
            return None, None, None


class SortType(Enum):
    综合 = "general"
    最热 = "popularity_descending"
    最新 = "time_descending"


class NoteType(Enum):
    综合 = 0
    视频 = 1
    图文 = 2
    先图文后视频 = 3


class Spider(threading.Thread):
    def __init__(self, name, user: User = None, userId: str = None):
        super().__init__()
        # 爬虫信息
        self.name = name
        self.state = "stopped"
        self.userId = userId
        self.success_count = 0
        self.failure_count = 0
        self.not_note_count = 0
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
        if not self.tasks:
            return self.logger.log({"信息": "进程未部署任务，退出中..."})
        for i in range(0, len(self.tasks) - 1):
            self.tasks[i].setNext(self.tasks[i + 1])
        if self.tasks:
            self.tasks[-1].setNext(None)
        self.searcher.run()
        if not self.searcher.urls:
            return self.logger.log({"信息": "进程无有效链接，退出中..."})
        i = 0
        while not self.stop_event.is_set():
            self.pause_event.wait()
            i += 1
            self.tasks[0].handle(self)
            time.sleep(1)
            if all(map(lambda x: x['state'], self.searcher.urls)):
                if self.cyclicMode:
                    self.logger.log({'信息': f'正在进行第 {i} 次循环'})
                    time.sleep(self.intervalMinute * 60)
                    self.searcher.update()
                else:
                    break

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
        self.settings = Settings()
        self.search_keys = self.spider.searchKey.split('|')
        self.sort_type = SortType[self.spider.sortType].value
        self.note_type = NoteType[self.spider.noteType].value
        self.needs = self.spider.singleTaskCount
        self.urls: list = []

    def run(self):
        try:
            data = {
                'keywords': self.search_keys,
                'sort_type': self.sort_type,
                'note_type': self.note_type,
                'needs': self.needs,
            }
            response = self.api.post(f'{self.settings.baseAPI}/note/search', data)
            self.urls = response['data']
            self.spider.taskCount = len(self.urls)
        except Exception as e:
            self.spider.logger.log({'信息': f'搜索器获取数据异常: {e}'}, level='error')

    def update(self):
        try:
            data = {
                'keywords': self.search_keys,
                'sort_type': self.sort_type,
                'note_type': self.note_type,
                'needs': 20,
            }
            response = self.api.post(f'{self.settings.baseAPI}/note/search', data)
            noteIds = map(lambda x: x['noteId'], self.urls)
            for note in response['data']:
                if note['noteId'] not in noteIds:
                    self.urls.append(note)
            self.spider.taskCount = len(self.urls)
        except Exception as e:
            self.spider.logger.log({'信息': f'搜索器更新数据异常: {e}'}, level='error')


class Handler:
    @staticmethod
    def trace(func):
        @functools.wraps(func)
        def inner(self, spider, *args, **kwargs):
            noteId = Handler.getNoteID(spider.searcher.urls)
            try:
                self.pause(spider)
                result = func(self, spider, *args, **kwargs)
                self.pause(spider)
                return result
            except Exception as e:
                spider.logger.log({"信息": f'链异常，{func.__name__}: {e}', '笔记编号': noteId}, level='error')
            finally:
                if self.next:
                    self.timer(spider)
                    self.next.handle(spider)

        return inner

    def setNext(self, next_):
        self.next: Handler = next_

    @trace
    def handle(self, spider: Spider):
        pass

    @staticmethod
    def timer(spider: Spider):
        if spider.isRandomIntervalTime:
            time.sleep(random.uniform(1, spider.intervalTime))
        else:
            time.sleep(spider.intervalTime)

    @staticmethod
    def pause(spider: Spider):
        while spider.state == 'paused':
            time.sleep(1)

    @staticmethod
    def base(self, spider, operate: str):
        noteId = Handler.getNoteID(spider.searcher.urls)
        if noteId and '-' not in noteId:
            res = spider.api.post(f"{spider.user.settings.baseAPI}/note/{operate}", {'noteId': noteId})
            if res['success']:
                spider.logger.log({"信息": f'{operate} 操作成功', '笔记编号': noteId})
            else:
                spider.logger.log({"信息": f'{operate} 操作失败', '笔记编号': noteId}, level='error')
            self.timer(spider)

    @staticmethod
    def getNoteID(urls):
        return next((url['noteId'] for url in urls if not url['state']), None)


class UncollectTask(Handler):
    @Handler.trace
    def handle(self, spider: Spider):
        Handler.base(self, spider, 'uncollect')

    def __str__(self):
        return '取消收藏'


class SkipCollectedTask(Handler):
    @Handler.trace
    def handle(self, spider: Spider):
        noteId = Handler.getNoteID(spider.searcher.urls)
        if noteId and '-' not in noteId:
            res = spider.api.post(f"{spider.user.settings.baseAPI}/note/collected", {'noteId': noteId})
            if res['data']:
                if self.next:
                    spider.logger.log({"信息": f'跳过已收藏', '笔记编号': noteId})
                    self.next = self.next.next
                self.timer(spider)

    def __str__(self):
        return '跳过已收藏'


class CommentTask(Handler):
    @Handler.trace
    def handle(self, spider: Spider):
        if not Path(spider.commentPath).exists():
            if self.next:
                self.next = self.next.next
                spider.logger.log({"信息": f'评论文件不存在，跳过评论环节'})
            else:
                spider.logger.log({"信息": f'评论文件不存在，无法评论'})
        else:
            with open(spider.commentPath, 'r', encoding='utf8') as fr:
                comments = fr.read()
            comments = [comment for comment in comments.split('\n') if comment]
            comment = random.choice(comments)
            comment = CommentTask.check_comment(comment)  # 检测敏感
            if spider.isRandomRareWord:  # 生僻字追加
                comment = f"{comment}{CommentTask.generate_rare_chars(spider.rareWordCount)}"
            noteId = Handler.getNoteID(spider.searcher.urls)
            if noteId and '-' in noteId:
                spider.not_note_count += 1
            if noteId and '-' not in noteId:
                data = {'noteId': noteId, 'comment': comment, 'userId': spider.userId}
                res = spider.api.post(f"{spider.user.settings.baseAPI}/note/comment", data)
                self.timer(spider)
                if res['data']:
                    spider.logger.log({"信息": f'评论`{comment}`成功', '笔记编号': noteId})
                    spider.success_count += 1
                elif spider.isCheckShield:
                    spider.logger.log({"信息": f'评论`{comment}`失败', '笔记编号': noteId}, level='error')
                    spider.failure_count += 1
                    if spider.isShieldRetry:
                        for i in range(spider.retryCount):
                            spider.logger.log({"信息": f'正在进行第 {i + 1} 次重新评论', '笔记编号': noteId})
                            res = spider.api.post(f"{spider.user.settings.baseAPI}/note/comment", data)
                            self.timer(spider)
                            if res['data']:
                                spider.logger.log({"信息": f'第 {i + 1} 次评论成功', '笔记编号': noteId})
                                spider.success_count += 1
                                spider.failure_count -= 1
                                break

    def __str__(self):
        return '评论笔记'

    @staticmethod
    def replace_with_asterisks(match):
        word = match.group()
        return '*' * len(word)

    @staticmethod
    def check_comment(comment):
        pattern = '|'.join(banned_words)
        comment = re.sub(pattern, CommentTask.replace_with_asterisks, comment)
        return comment

    @staticmethod
    def generate_rare_chars(num_chars):
        rare_chars = set()
        while len(rare_chars) < num_chars:
            char = chr(random.randint(0x4E00, 0x9FFF))
            rare_chars.add(char)
        return ''.join(rare_chars)


class CollectTask(Handler):
    @Handler.trace
    def handle(self, spider: Spider):
        Handler.base(self, spider, 'collect')

    def __str__(self):
        return '收藏'


class LikeTask(Handler):
    @Handler.trace
    def handle(self, spider: Spider):
        Handler.base(self, spider, 'like')

    def __str__(self):
        return '点赞'


class FollowTask(Handler):
    @Handler.trace
    def handle(self, spider: Spider):
        Handler.base(self, spider, 'follow')

    def __str__(self):
        return '关注'


class EndTask(Handler):
    @Handler.trace
    def handle(self, spider: Spider):
        item = next(((i + 1, note['noteId']) for i, note in enumerate(spider.searcher.urls) if not note['state']), None)
        if item:
            serial_num, noteId = item
            spider.searcher.urls[serial_num - 1]['state'] = True
            spider.finished_count += 1
            spider.logger.log({"信息": f'第 {serial_num} 个笔记已完成', '笔记编号': noteId})
        # END链额度管控 加了锁防止多线程竞态
        with SpidersLock:
            max_limit = spider.api.get(f'{spider.user.settings.baseAPI}/user/limit')['data']
            spider.user.max_limit = max_limit
            if (spiders_count := len(Spiders)) > max_limit:
                for _ in range(spiders_count - max_limit):
                    deleted_spider = Spiders.popitem()
                    if isinstance(deleted_spider[1], Spider):
                        deleted_spider[1].stop()

    def __str__(self):
        return '标记任务完成'


if __name__ == "__main__":
    pass
