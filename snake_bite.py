import pygame

class Snake_Bite:

    def __init__(self, snake, range = 3):
        """Initialize the biting of the snake!"""
        self.snake = snake
        self.rect = pygame.Rect(0, 0, 10, 10)
        self.screen = self.snake.screen
        self.active = False
        self.range = range
        self.coords = [0, 0]
        self.squares_moved = 0
        self.started_frame = self.snake.active_frames
        self.grid = self.snake.grid
        self.bites = 0

    def chomper(self):
        '''Begin the biting!'''
        if len(self.snake.snake_squares)>2:
            self.bites += 1
            self.started_frame = self.snake.active_frames - 1
            self.active = True
            self.squares_moved = 0
            self.movement = self.determ_start()
            self.rect.center = self.grid.grid_array[self.coords[0], self.coords[1]].center
        
    def determ_start(self):
        '''Based on the snake's direction, place the snake bite in front of the snake head'''
        for x in range(2):
            difference = self.snake.snake_squares[-1][x]-self.snake.snake_squares[-2][x]
            if difference:
                result = [0, 0]
                result[x] = difference
                self.coords = [self.snake.snake_head[0]+result[0], self.snake.snake_head[1]+result[1]]
                return(result)

    def move_one(self):
        """Move the bite one square forward until it excceeds the range"""
        if self.squares_moved<=self.range:
            self.coords = [self.coords[0]+self.movement[0], self.coords[1]+self.movement[1]]
            self.rect.center = self.grid.grid_array[self.coords[0], self.coords[1]].center
            self.squares_moved+=1
        else:
            self.active = False
            self.squares_moved = 0
        self.snake.changed_frame = True

    def draw_bite(self):
        """Draw the square in the correct spot in the grid"""
        if self.active:
            pygame.draw.rect(self.screen, (0, 0, 255), self.rect)