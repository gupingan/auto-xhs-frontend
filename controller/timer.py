"""
@File: timer.py
@Author: 顾平安
@Created: 2023/11/9 16:36
@Description: Created in frontend.
"""
from datetime import datetime


def current(type_: str = 'datetime', template: str = "%Y-%m-%d %H:%M:%S"):
    now = datetime.now()
    if type_ == 'str':
        return now.strftime(template)
    elif type_ == 'datetime':
        return now
    elif type_ == 'timestamp':
        return now.timestamp()
    return None
