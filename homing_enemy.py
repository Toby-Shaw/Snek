import pygame
from all_enums import MAP_IDs as MI

class Homing:

    def __init__(self, snake, number_active, frame_update, start_pos):
        self.snake = snake
        self.number_active = number_active
        self.frame = frame_update
        self.enemy_squares = [start_pos]

    def move_one(self):
        target = self.snake.snake_head
        point = self.enemy_squares[-1]
        y = abs(point[0]-target[0])
        x = abs(point[1]-target[1])
        yy = point[0]-target[0]
        xx = point[1]-target[1]
        movement = [0, 0]
        if x>=y: 
            if xx<0: movement = [0, 1]
            elif xx>0: movement = [0, -1]
        else: 
            if yy<0: movement = [1, 0]
            elif yy>0: movement = [-1, 0]
        self.enemy_squares.append([point[0]+movement[0], point[1]+movement[1]])
        self.kill_squares()
        self.kill_squares()
    
    def kill_squares(self):
        if len(self.enemy_squares)>self.number_active:
            self.enemy_squares.pop(0)
            self.snake.changed_frame = True

    def check_collisions(self):
        """Check if snake has attacked or if it's cutting time"""
        self.room = self.snake.room
        for active in self.enemy_squares:
            if self.snake.snake_map[active[0], active[1]]==MI.SNAKE:
                if[active[0], active[1]]==self.snake.snake_head:
                    self.snake._snake_ded()
                else:
                    #print("cut!")
                    cutting_point = self.snake.snake_squares.index(active)
                    remainder = len(self.snake.snake_squares)-cutting_point
                    self.snake._kill_squares(reset=True, remainder=remainder)
                    self.snake.number_squares = remainder-1
                    self.snake.changed_frame = True
                    break
            elif self.snake.snake_bite.active:
                if[active[0], active[1]]==self.snake.snake_bite.coords:
                    self.snake.snake_bite.active = False
                    self.snake.snake_bite.squares_moved = 0
                    if self.enemy_squares.index(active) == self.number_active-1:
                        self.number_active = 0
                        self.snake.homer = False
                        self.kill_squares()
                        self.kill_squares()
                        self.kill_squares()
                    else:
                        self.number_active -= 1
                        self.kill_squares()
                    if self.number_active == 0:
                        self.snake.homer = False
