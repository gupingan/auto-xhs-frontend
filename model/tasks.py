import functools
import random
import requests
from obscuror import obscuror
from .spider import *

Spiders = {}
SpidersLock = threading.Lock()


class Handler:
    """
    任务链单元基类
    11月14日：遭遇异常时，则执行下一个单元
    """

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
            except requests.ConnectTimeout as e:
                spider.logger.log({"信息": f'连接超时，{func.__name__}: {e}', '笔记编号': noteId}, level='warning')
            except requests.Timeout as e:
                spider.logger.log({"信息": f'请求超时，{func.__name__}: {e}', '笔记编号': noteId}, level='warning')
            except requests.ConnectionError as e:
                spider.logger.log({"信息": f'连接异常，{func.__name__}: {e}', '笔记编号': noteId}, level='warning')
            except Exception as e:
                spider.logger.log({"信息": f'链异常，{func.__name__}: {e}', '笔记编号': noteId}, level='warning')
            finally:
                if self.next:
                    self.timer(spider)
                    self.next.handle(spider)

        return inner

    def setNext(self, next_):
        self.next: Handler = next_

    @trace
    def handle(self, spider):
        pass

    @staticmethod
    def timer(spider):
        if spider.isRandomIntervalTime:
            time.sleep(random.uniform(1, spider.intervalTime))
        else:
            time.sleep(spider.intervalTime)

    @staticmethod
    def pause(spider):
        while spider.state == 'paused':
            time.sleep(1)

    @staticmethod
    def baseOperate(task, spider, operate: str):
        state = {'follow': '关注', 'collect': '收藏', 'uncollect': '取消收藏', 'like': '点赞'}
        noteId = Handler.getNoteID(spider.searcher.urls)
        if noteId and '-' not in noteId:
            res = spider.api.post(f"{BaseAPI}/note/{operate}", {'noteId': noteId})
            if res['success']:
                spider.logger.log(
                    {"信息": f'对笔记{"作者" if operate == "follow" else ""}进行 {state[operate]} 操作成功',
                     '笔记编号': noteId}, level='success')
            else:
                spider.logger.log(
                    {"信息": f'对笔记{"作者" if operate == "follow" else ""}进行 {state[operate]} 操作失败',
                     '笔记编号': noteId}, level='failure')
            task.timer(spider)

    @staticmethod
    def getNoteID(urls):
        return next((url['noteId'] for url in urls if not url['state']), None)


class UncollectTask(Handler):
    @Handler.trace
    def handle(self, spider):
        Handler.baseOperate(self, spider, 'uncollect')

    def __str__(self):
        return '取消收藏'


class SkipCollectedTask(Handler):
    @Handler.trace
    def handle(self, spider):
        noteId = Handler.getNoteID(spider.searcher.urls)
        if noteId and '-' not in noteId:
            res = spider.api.post(f"{BaseAPI}/note/collected", {'noteId': noteId})
            if res['data'] and self.next:
                spider.logger.log({"信息": '检测到笔记已被收藏，跳过评论', '笔记编号': noteId}, level='success')
                spider.skip_comment_count += 1
                self.next = self.next.next
            self.timer(spider)

    def __str__(self):
        return '跳过已收藏'


class CommentTask(Handler):
    @Handler.trace
    def handle(self, spider):
        comment = random.choice(spider.comments)
        if spider.isRandomRareWord:
            comment = obscuror(comment, spider.rareWordCount, mode=spider.rareWordEngine).result
        noteId = Handler.getNoteID(spider.searcher.urls)
        if noteId and '-' not in noteId:
            data = {'noteId': noteId, 'comment': comment, 'userId': spider.userId}
            res = spider.api.post(f"{BaseAPI}/note/comment", data)
            self.timer(spider)
            if res['data']:
                spider.logger.log({"信息": f'评论`{comment}`成功', '笔记编号': noteId}, level='success')
                spider.success_count += 1
            elif spider.isCheckShield:
                spider.logger.log({"信息": f'评论`{comment}`失败', '笔记编号': noteId}, level='failure')
                spider.failure_count += 1
                if spider.isShieldRetry:
                    self.process_shield(spider, noteId, data)

    def __str__(self):
        return '评论笔记'

    def process_shield(self, spider, noteId, data):
        for i in range(spider.retryCount):
            spider.logger.log({"信息": f'正在进行第 {i + 1} 次重新评论', '笔记编号': noteId})
            comment = random.choice(spider.comments)
            if spider.isRandomRareWord:
                comment = obscuror(comment, spider.rareWordCount, mode=spider.rareWordEngine).result
            data['comment'] = comment
            res = spider.api.post(f"{BaseAPI}/note/comment", data)
            self.timer(spider)
            if res['data']:
                spider.logger.log({"信息": f'第 {i + 1} 次评论成功', '笔记编号': noteId}, level='success')
                spider.success_count += 1
                spider.failure_count -= 1
                break


class CollectTask(Handler):
    @Handler.trace
    def handle(self, spider):
        Handler.baseOperate(self, spider, 'collect')

    def __str__(self):
        return '收藏'


class LikeTask(Handler):
    @Handler.trace
    def handle(self, spider):
        Handler.baseOperate(self, spider, 'like')

    def __str__(self):
        return '点赞'


class FollowTask(Handler):
    @Handler.trace
    def handle(self, spider):
        Handler.baseOperate(self, spider, 'follow')

    def __str__(self):
        return '关注'


class EndTask(Handler):
    @Handler.trace
    def handle(self, spider):
        item = next(((i + 1, note['noteId']) for i, note in enumerate(spider.searcher.urls) if not note['state']), None)
        if item:
            serial_num, noteId = item
            spider.searcher.urls[serial_num - 1]['state'] = True
            spider.finished_count += 1
            spider.logger.log({"信息": f'第 {serial_num} 条笔记的相关任务已完成', '笔记编号': noteId}, level='success')
        # END链额度管控 加了锁防止多线程竞态
        with SpidersLock:
            max_limit = spider.api.get(f'{BaseAPI}/user/limit')['data']
            spider.user.max_limit = max_limit
            if (spiders_count := len(Spiders)) > max_limit:
                for _ in range(spiders_count - max_limit):
                    deleted_spider = Spiders.popitem()
                    if isinstance(deleted_spider[1], Spider):
                        deleted_spider[1].stop()

    def __str__(self):
        return '标记任务完成'
