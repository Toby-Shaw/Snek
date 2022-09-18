import numpy
import pygame
from all_enums import MAP_IDs as MI

class Walls:

    def __init__(self, snake):
        self.snake = snake
        self.wall_squares = self.snake.wall_squares
        self.square_size = self.snake.square_size

    def _pull_values(self):
        self.wall_squares = self.snake.wall_squares
        self.room = self.snake.room
        self.room_sets = self.snake.room_sets
        self.snake_map = self.snake.snake_map

    def _push_values(self):
        self.snake.room_sets = self.room_sets
        self.snake.wall_squares = self.wall_squares

    def _add_wall_square(self):
        '''Add a impassable wall space where the mouse cursor is pressed'''
        self._pull_values()
        mouse_pos = pygame.mouse.get_pos()
        row_selected = mouse_pos[1]//self.snake.square_size
        column_selected = mouse_pos[0]//self.snake.square_size
        if [row_selected, column_selected] not in self.wall_squares and ([row_selected, column_selected]
            not in self.snake.snake_squares):
            self.snake.changed_frame = True
            self.wall_squares.append([row_selected, column_selected]) 
            self.snake.snake_map[row_selected, column_selected] = MI.WALL
            if self.room_sets[self.room[0], self.room[1]]:
                self.room_sets[self.room[0], self.room[1]].append(row_selected)
                self.room_sets[self.room[0], self.room[1]].append(column_selected)
            else: self.room_sets[self.room[0], self.room[1]] = [row_selected, column_selected]
        self._push_values()
    
    def _remove_wall_square(self):
        """Delete the wall square that the cursor is over"""
        self._pull_values()
        row_selected = self.snake.row_selected
        column_selected = self.snake.column_selected
        if [row_selected, column_selected] in self.wall_squares:
            self.changed_frame = True
            self.wall_squares.remove([row_selected, column_selected])
            self.room_sets[self.room[0], self.room[1]] = []
            for x in self.wall_squares:
                self.room_sets[self.room[0], self.room[1]].append(x[0])
                self.room_sets[self.room[0], self.room[1]].append(x[1])
            self.snake.snake_map[row_selected, column_selected] = MI.CLEAR
        self._push_values()
    