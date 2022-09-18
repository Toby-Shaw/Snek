import pygame

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
    
    def kill_squares(self):
        if len(self.enemy_squares)>self.number_active:
            self.enemy_squares.pop(0)
            self.snake.changed_frame = True
