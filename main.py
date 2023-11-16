"""
@File: main.py
@Author: 顾平安
@Created: 2023/11/5 16:06
@Description: Created in 咸鱼-自动化-AutoXhs.
"""
from controller import Controller

if __name__ == '__main__':
    try:
        controller = Controller()
        controller.run()
    except Exception as e:
        print('抛出异常：', e)
        input('按任意键退出...')
