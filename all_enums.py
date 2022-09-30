from enum import Enum

class MAP_IDs(Enum):
    WALL = 10
    SNAKE = 1
    FOOD = 2
    CLEAR = 0

class ROOM_IDs(Enum):
    MENU = 0
    GAME = 1
    PAUSE = 2
    ENDSCREEN = 3