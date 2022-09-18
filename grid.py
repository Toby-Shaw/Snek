import pygame
import numpy
import random

class Grid:
    def __init__(self, snake, rect_size, spacing):
        """Divide the screen into squares"""
        self.snake = snake
        self.screen = snake.screen
        self.sd = snake.dimensions
        self.rect_size = rect_size
        self.spacing = spacing
        self.lcolor_multiplier = 230/(max(self.sd[0], self.sd[1])/max(self.spacing[0], self.spacing[1]))
        self.scolor_multiplier = 230/((self.sd[0]/self.spacing[0])*(self.sd[1]/self.spacing[1]))
        self.input_color_random = numpy.empty(self.snake.number_color_combos, dtype=object)
        self.option_list = [230, 200, 170, 140, 110]
        self.reserve_list = numpy.empty(self.snake.number_color_combos, dtype=object)
        for x in range(self.snake.number_color_combos):
            indexes = random.sample((0, 1, 2, 3, 4), 3)
            self.reserve_list[x] = indexes
        self._make_grid()
        self.initialize_background(self.snake.color_random)

    def _make_grid(self):
        self.number_columns = self.sd[0]//self.spacing[0]
        self.number_rows = self.sd[1]//self.spacing[1]
        self.columnrow = [self.number_columns, self.number_rows]
        self.grid_array = numpy.empty((self.number_rows, self.number_columns), dtype=pygame.Rect)
        for chosen_row in range(self.number_rows):
            for chosen_column in range(self.number_columns):
                self.grid_array[chosen_row, chosen_column] = pygame.Rect(chosen_column*self.spacing[0], 
                        chosen_row*self.spacing[1], self.rect_size[0], self.rect_size[1])

    def random_color_pattern(self, row_number, column_number):
        try: self.screen.fill(self.fast_calc[row_number*self.number_columns+column_number], 
                self.grid_array[row_number, column_number])
        except: 
            self.screen.fill((200, 200, 200), 
                    self.grid_array[row_number, column_number])
            #print('oh well')

    def initialize_background(self, input):
        self.fast_calc = []
        for row in range(self.number_rows):
            for column in range(self.number_columns):
                write_out = [[200], [200], [200]]
                if 0 in self.reserve_list[input]:
                    write_out[self.reserve_list[input].index(0)] = 230-row*self.lcolor_multiplier
                if 1 in self.reserve_list[input]:
                    write_out[self.reserve_list[input].index(1)] = 230-column*self.lcolor_multiplier
                if 2 in self.reserve_list[input]:
                    write_out[self.reserve_list[input].index(2)] = round(230-row/(column+1)*self.lcolor_multiplier)
                if 3 in self.reserve_list[input]:
                    write_out[self.reserve_list[input].index(3)] = round(230-column/(row+1)*self.lcolor_multiplier)
                if 4 in self.reserve_list[input]:
                    write_out[self.reserve_list[input].index(4)] = 230-row*column*self.scolor_multiplier
                for x in range(3):
                    write_out[x] = round(write_out[x], 2)
                self.fast_calc.append(write_out)

