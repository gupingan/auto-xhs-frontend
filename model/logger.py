import csv
import os
import threading
import time

from tabulate import tabulate
from datetime import datetime
from .colors import *


class CSVLogger:
    def __init__(self, file_name, fieldnames, mode="a"):
        self.file_name = file_name
        self.fieldnames = fieldnames
        self.mode = mode
        self.__init_csv()
        self._stop_event = threading.Event()

    def __init_csv(self):
        """
        Initialize the csv file
        11月14日 增加对文件权限的检测
        :return:
        """
        try:
            with open(self.file_name, mode="w", newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
        except PermissionError:
            print(f"PermissionError:请关闭已打开的CSV文件-{self.file_name}", RED)

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
        table_data = data[1:]
        if last_n:
            table_data = table_data[-last_n:]
        for row_index in range(len(table_data)):
            self.level_handler(row_index, table_data)
            table_data[row_index][2] = CSVLogger.truncate_string(
                table_data[row_index][2], 24
            )
            table_data[row_index][3] = CSVLogger.truncate_string(
                table_data[row_index][3], 20
            )
        print(f'日志数量： {len(table_data)} 条')
        print(tabulate(table_data, headers=self.fieldnames, tablefmt='grid'))

    def stop(self):
        self._stop_event.set()

    def tail(self, n=8, interval=3):
        try:
            while not self._stop_event.is_set():
                os.system('clear' if os.name == 'posix' else 'cls')
                with open(self.file_name, 'r', encoding='utf-8-sig') as f:
                    csv_data = f.readlines()
                    lines = list(map(lambda x: x.split(','), csv_data[1:][-n:]))
                    rows = len(lines)
                    for row in range(rows):
                        self.level_handler(row, lines)
                        lines[row][2] = CSVLogger.truncate_string(lines[row][2], 24)
                        lines[row][3] = CSVLogger.truncate_string(lines[row][3], 20)
                    print(tabulate(lines, headers=self.fieldnames, tablefmt='orgtbl'))
                print()
                printc('注意：不要复制！否则日志会消失！请出去通过log命令找到你需要的再复制', RED)
                printc('提示：你能按下 ctrl+c 退出监控模式，假如日志消失，按下任意键则显示', CYAN)
                time.sleep(interval)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            printc(f'系统：{e}', RED)
        finally:
            printc('系统：', BLUE, end='')
            print("监控进程结束....")

    def level_handler(self, i, lines):
        if lines[i][1] == 'failure':
            lines[i][1] = f'{RED}failure{RESET}'
        elif lines[i][1] == 'success':
            lines[i][1] = f'{GREEN}success{RESET}'
        elif lines[i][1] == 'warning':
            lines[i][1] = f'{YELLOW}warning{RESET}'


if __name__ == '__main__':
    logger = CSVLogger('../日志-adminer/10086.csv', ['日志', '级别', '笔记编号', '信息'])
    logger.tail()
