from enum import Enum


class SortType(Enum):
    综合 = "general"
    最热 = "popularity_descending"
    最新 = "time_descending"


class NoteType(Enum):
    综合 = 0
    视频 = 1
    图文 = 2
    先图文后视频 = 3
