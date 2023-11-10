"""
@File: __init__.py.py
@Author: 顾平安
@Created: 2023/11/9 14:30
@Description: Created in frontend.
"""
from .api import *
from .types import *
from .tasks import *
from .cookies import *
from .qrcode import *
from .user import *
from .logger import *
from .colors import *

RunStates = {
    'running': '运行中',
    'paused': '已暂停',
    'stopped': '已终止'
}
