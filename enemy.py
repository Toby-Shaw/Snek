import pygame
import numpy
from all_enums import MAP_IDs as MI

class Enemy:

    def __init__(self, snake, number_red, set_path=False, path=None, enemy_number = 0):
        """Initialize an enemy snake, either with a path or none"""
        self.snake = snake
        self.grid = self.snake.grid
        self.enemy_number = enemy_number
        if not set_path:
            self.path_length = 10
            #self.enemy_squares = numpy.empty(self.path_length, dtype=object)
            self.enemy_squares = []
        else:
            if type(path) == list:
                self.path_length = len(path)
                self.enemy_squares = []
                for x in range(self.path_length):
                    self.enemy_squares.append(path[x])
            else: 
                self.enemy_squares = []
                self.path_length = 10
                for x in range(self.path_length):
                    self.enemy_squares.append([])
        #print(self.enemy_squares)
        self.number_red = number_red
        self.generate_proper_indexes()

    def generate_proper_indexes(self):
        self.proper_indexes = []
        for x in range(self.number_red):
            self.proper_indexes.append(x)

    def move_forward(self):
        """Update the enemy so the active squares are 1 farther along their path"""
        for x in range(self.number_red):
            if self.proper_indexes[x] < self.path_length-1:
                self.proper_indexes[x] += 1
            else: self.proper_indexes[x] = 0 
        self.snake.changed_frame = True

    def check_collisions(self):
        """Check if the enemy is colliding with the snake, and cut/kill it if so"""
        active_indexes = self.list_of_active_squares()
        self.room = self.snake.room
        for active in active_indexes:
            if type(active)==list and self.snake.snake_map[active[0], active[1]]==MI.SNAKE:
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
                    if active_indexes.index(active) == self.number_red-1:
                        self.number_red = 0
                        self.proper_indexes = []
                    else:
                        self.number_red -= 1
                        self.proper_indexes.pop(-1)
                    if len(self.proper_indexes) == 0:
                        if type(self.snake.killed_enemys[self.room[0], self.room[1]])==list:
                            self.snake.killed_enemys[self.room[0], self.room[1]].append(self.enemy_number)
                        else: self.snake.killed_enemys[self.room[0], self.room[1]] = [self.enemy_number]

    def list_of_active_squares(self):
        """Return a list of the active enemy square coordinates"""
        list_out = []
        for x in self.proper_indexes:
            if len(self.enemy_squares)>=self.number_red:
                if self.enemy_squares[x]:
                    list_out.append(self.enemy_squares[x])
            else:
                self.enemy_squares.append([])
        return(list_out)
    
    def add_enemy_square(self):
        """Add an enemy square to the list of options, as long as the path length is long enough"""
        row_selected = self.snake.row_selected
        column_selected = self.snake.column_selected
        self.room = self.snake.room
        self.enemy_sets = self.snake.enemy_sets
        self.snake.changed_frame = True
        self.path_length += 1
        #This extra logic accounts for empty path spots, so that they are removed/moved around
        #Though it will not work if path spots are not on the end, and instead nested within. Take care!
        for x in range(len(self.enemy_squares)):
            if not self.enemy_squares[x]:
                self.enemy_squares[x] = [row_selected, column_selected]
                break
            elif self.enemy_squares[-1]:
                self.enemy_squares.append([row_selected, column_selected])
                break
        self.enemy_sets[self.room[0], self.room[1]][self.enemy_number] = []
        for x in self.enemy_squares:
            if x:
                self.enemy_sets[self.room[0], self.room[1]][self.enemy_number].append(x[0])
                self.enemy_sets[self.room[0], self.room[1]][self.enemy_number].append(x[1])

    def remove_enemy_square(self):
        """Update values, then remove the selected enemy_square and update the overall data_set"""
        row_selected = self.snake.row_selected
        column_selected = self.snake.column_selected
        self.room = self.snake.room
        self.enemy_sets = self.snake.enemy_sets
        self.snake.changed_frame = True
        # Reset indexes to prevent illegal index numbers
        self.generate_proper_indexes()
        if [row_selected, column_selected] in self.enemy_squares:
            self.path_length -= 1
            self.enemy_squares.remove([row_selected, column_selected])
            self.enemy_sets[self.room[0], self.room[1]][self.enemy_number] = []
            for x in self.enemy_squares:
                if x:
                    self.enemy_sets[self.room[0], self.room[1]][self.enemy_number].append(x[0])
                    self.enemy_sets[self.room[0], self.room[1]][self.enemy_number].append(x[1])
    
    def enemy_ded(self):
        self.snake.changed_frame = True
        self.path_length = 0
        self.generate_proper_indexes()
        self.enemy_squares = []