import pygame
import sys
import numpy
from snaky_text import Text
from grid import Grid
from enemy import Enemy
from file_converter import File_Converter
from walls import Walls
import random
from time import sleep
from snake_bite import Snake_Bite
from all_enums import MAP_IDs as MI
from all_enums import ROOM_IDs as RI
from homing_enemy import Homing
from snaky_button import Button

class Snake:
    """Snake!"""
    def __init__(self):
        """Initialize the game!"""
        pygame.init()
        self.dimensions = (1400, 920)
        #35 by 23, mid_square = (11, 17)
        self.screen = pygame.display.set_mode(self.dimensions)
        self.movement = (0, 0)
        self.clock = pygame.time.Clock()
        self.active_frames, self.tick_update, self.current_fps = 0, 0, 50
        self.number_color_combos = 15
        self.color_random = 0
        self.fps_meter = Text(self, f"FPS: {self.current_fps}", 30, (0, 200, 0), 65, 890)
        self.square_size = 40
        self.grid = Grid(self, (self.square_size-1, self.square_size-1), (self.square_size, self.square_size))
        self.file_setup = File_Converter(self)
        self.snake_bite = Snake_Bite(self)
        self.max_enemy_count = 10
        self.snake_delay = [7, 5]
        self.stage = 0
        self.snake_head, self.snake_rect_size, self.snake_squares = [11, 17], (25, 25), [[11, 17]]
        self.snake_map = numpy.full((self.grid.number_rows, self.grid.number_columns), fill_value = MI.CLEAR, dtype=object)
        self.snake_map[11, 17] = MI.SNAKE
        self.room_sets = self.file_setup.file_to_room_sets('Games/Snake/data_storage/wall_squares.txt')
        self.enemy_sets = self.file_setup.file_to_room_sets('Games/Snake/data_storage/enemy_paths.txt', extra_layer=True)
        self.enemy_info = self.file_setup.file_to_room_sets('Games/Snake/data_storage/enemy_info.txt', extra_layer=True)
        self.homer_info = self.file_setup.file_to_room_sets('Games/Snake/data_storage/homer_data.txt')
        self.enemy_info = self.file_setup.refine_enemy_info(self.enemy_info)
        self.food_sets = self.file_setup.file_to_room_sets('Games/Snake/data_storage/food_positions.txt')
        self.game_food_copy = numpy.copy(self.food_sets)
        self.wall_squares, self.enemys, self.room = [], [], [0, 0]
        for x in range(len(self.enemy_sets[self.room[0], self.room[1]])):
            self.enemys.append(Enemy(self, self.enemy_info[self.room[0], self.room[1]][x][1], 
                set_path = True, path=self.file_setup.enemy_nonsense(self.enemy_sets, x), enemy_number=x))
        #print(self.enemys)
        self.wall_squares = self.file_setup.update_wall_squares_set(self.room_sets)
        self.file_setup.map_writeout(self.room_sets, itemid=MI.WALL)
        self.file_setup.map_writeout(self.food_sets, itemid=MI.FOOD)
        self.food_positions = self.file_setup.update_wall_squares_set(self.food_sets)
        #print(self.food_positions)
        #print(self.wall_squares)
        self.walls = Walls(self)
        self.number_squares = 3
        self.changed_frame = True
        self.number_selected = 0
        self.changed_room = False
        self.killed_enemys = numpy.empty((4, 4), dtype=list)
        self.save_changes = False
        self.room_cooldown = 0
        if int(self.homer_info[self.room[0], self.room[1]][0]):
            info = self.homer_info[self.room[0], self.room[1]]
            for x in range(len(info)): info[x] = int(info[x])
            self.homer = Homing(self, info[1], info[4], [info[2], info[3]])
        else: self.homer = False
        self.starter_homer = False
        self.screen_phase = RI.MENU
        self.title = Text(self, "SNek", 70, (0, 0, 0), 700, 200)
        self.start = Button(self, "Start", (0, 255, 0), 700, 500)
        self.held = False
        
    def run_game(self):
        """The constant loop of all events"""
        while True:
            self._check_events()
            if self.screen_phase == RI.GAME:
                for enemy in self.enemys:
                    enemy.check_collisions()
                for enemy in range(len(self.enemys)):
                    if not self.active_frames%(self.enemy_info[self.room[0], self.room[1]][enemy][0]):
                        self.enemys[enemy].move_forward()
                if self.homer:
                    self.homer.check_collisions()
                self._move_snake()
                self._update_fps()
                if self.homer and not self.active_frames%self.homer.frame:
                    self.homer.move_one()
                if self.snake_bite.active and not (self.active_frames-self.snake_bite.started_frame)%5:
                    self.snake_bite.move_one()
                self.active_frames += 1
                self.room_cooldown += 1
            elif self.screen_phase == RI.MENU:
                pass
            if self.changed_frame:
                self._update_screen()
           

    def _check_events(self):
        """Check keyboard and mouse inputs"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._snake_ded()
            elif event.type == pygame.KEYDOWN and self.screen_phase == RI.GAME:
                mouse_pos = pygame.mouse.get_pos()
                self.row_selected = mouse_pos[1]//self.square_size
                self.column_selected = mouse_pos[0]//self.square_size
                if event.key == pygame.K_RIGHT: self.movement = (1, 0)
                elif event.key == pygame.K_LEFT: self.movement = (-1, 0)
                elif event.key == pygame.K_UP: self.movement = (0, -1)
                elif event.key == pygame.K_DOWN: self.movement = (0, 1)
                elif event.key == pygame.K_SPACE:
                    if not self.snake_bite.active and self.active_frames-self.snake_bite.started_frame>30:
                        if len(self.snake_squares)>2: 
                            self.number_squares -= 1
                            self.snake_bite.chomper()
                            self._kill_squares()
                    """r=wallremove, e=add enemy square, o=remove e square, p = slow enemy, q = fast enemy,
                    l=long enemy, a=short enemy, b=add food, n=remove food, h=long homer, g=short homer
                    y=enable homer select, t=toggle homer in room, v=slow homer, c=fast homer"""
                elif event.key in [pygame.K_r, pygame.K_e, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_l,
                    pygame.K_a, pygame.K_b, pygame.K_n, pygame.K_h, pygame.K_g, pygame.K_y, pygame.K_t,
                    pygame.K_v, pygame.K_c]: self.save_changes = True
                if event.key == pygame.K_r: self.walls._remove_wall_square()
                elif event.key == pygame.K_e: self.enemys[self.number_selected].add_enemy_square()
                elif event.key == pygame.K_o: self.enemys[self.number_selected].remove_enemy_square()
                elif event.key == pygame.K_p:
                    self.enemy_info[self.room[0], self.room[1]][self.number_selected][0] += 1
                elif event.key == pygame.K_q:
                    self.enemy_info[self.room[0], self.room[1]][self.number_selected][0] -= 1
                elif event.key == pygame.K_l:
                    self.enemys[self.number_selected].number_red += 1
                    self.enemy_info[self.room[0], self.room[1]][self.number_selected][1] += 1
                    self.enemys[self.number_selected].generate_proper_indexes()
                elif event.key == pygame.K_a:
                    self.enemys[self.number_selected].number_red -= 1
                    self.enemy_info[self.room[0], self.room[1]][self.number_selected][1] -= 1
                    self.enemys[self.number_selected].generate_proper_indexes()
                elif event.key == pygame.K_b:
                    if [self.row_selected, self.column_selected] not in self.food_positions:
                        self.food_positions.append([self.row_selected, self.column_selected])
                        for array in [self.food_sets, self.game_food_copy]:
                            if array[self.room[0], self.room[1]]:
                                array[self.room[0], self.room[1]].append(self.row_selected)
                                array[self.room[0], self.room[1]].append(self.column_selected)
                            else: array[self.room[0], self.room[1]] = [self.row_selected, self.column_selected]
                elif event.key == pygame.K_n:
                    if [self.row_selected, self.column_selected] in self.food_positions:
                        self.food_positions.remove([self.row_selected, self.column_selected])
                        for array in [self.food_sets, self.game_food_copy]:
                            array[self.room[0], self.room[1]] = []
                            for x in self.food_positions:
                                array[self.room[0], self.room[1]].append(x[0])
                                array[self.room[0], self.room[1]].append(x[1])
                elif event.key == pygame.K_h:
                    self.homer_info[self.room[0], self.room[1]][1] = int(self.homer_info[self.room[0],
                    self.room[1]][1])+1
                    if self.homer: 
                        self.homer.number_active += 1
                        self.homer.kill_squares()
                elif event.key == pygame.K_g:
                    self.homer_info[self.room[0], self.room[1]][1] = int(self.homer_info[self.room[0],
                    self.room[1]][1])-1
                    if self.homer: 
                        self.homer.number_active -= 1
                        self.homer.kill_squares()
                elif event.key == pygame.K_y: self.starter_homer = not self.starter_homer
                elif event.key == pygame.K_t: 
                    if int(self.homer_info[self.room[0], self.room[1]][0]):
                        self.homer_info[self.room[0], self.room[1]][0] = 0
                    else: self.homer_info[self.room[0], self.room[1]][0] = 1
                elif event.key == pygame.K_v: 
                    self.homer_info[self.room[0], self.room[1]][4] = int(self.homer_info[self.room[0],
                    self.room[1]][4])+1
                    if self.homer: self.homer.frame += 1
                elif event.key == pygame.K_c:
                    self.homer_info[self.room[0], self.room[1]][4] = int(self.homer_info[self.room[0],
                    self.room[1]][4])-1
                    if self.homer: self.homer.frame -= 1
                elif event.__dict__['unicode'] in '0123456789':
                    try: self.number_selected = int(event.__dict__['unicode'])
                    except: pass
            elif pygame.mouse.get_pressed()[0]:
                if self.screen_phase == RI.GAME and not self.held:
                    self.save_changes = True
                    if not self.starter_homer: self.walls._add_wall_square()
                    else: 
                        self.homer_info[self.room[0], self.room[1]][2] = self.row_selected
                        self.homer_info[self.room[0], self.room[1]][3] = self.column_selected
                        info = self.homer_info[self.room[0], self.room[1]]
                        for x in range(len(info)): info[x] = int(info[x])
                        self.homer = Homing(self, info[1], info[4], [info[2], info[3]])
                elif self.screen_phase == RI.MENU:
                    if self.start.check_collision():
                        self.held = True
                        self.screen_phase = RI.GAME
            elif self.held and not pygame.mouse.get_pressed()[0]: self.held = False
               
    def _move_snake(self):
        '''Every given frame amount, move the snake one square in the specified direction
            and then clear the square behind if needed, and check food status'''
        if not (self.active_frames % self.snake_delay[self.stage]):
            if self.movement[0]: self._move_one(0)
            elif self.movement[1]: self._move_one(1)
            self._kill_squares()
            self._food_check()
            if len(self.snake_squares)>5: self.stage = 1
            else: self.stage = 0

    def _move_one(self, dir):
        """Move the snake along the x or y axis, x: dir=0, y: dir=1, updating appropriate lists"""
        affected_coords_init = [self.snake_head[dir], self.snake_head[not dir]+self.movement[dir]]
        affected_coords = self._check_border_crossing(affected_coords_init, dir)
        if self.snake_map[affected_coords[dir], affected_coords[not dir]] in [MI.CLEAR, MI.FOOD]:
            self.changed_frame = True
            self.snake_head[not dir] = affected_coords[1]
            self.snake_head[dir] = affected_coords[0]
            self.snake_map[affected_coords[dir], affected_coords[not dir]] = MI.SNAKE
            self.snake_squares.append(self.snake_head.copy())
        elif not (len(self.snake_squares)>1 and (affected_coords == self.snake_squares[-2] or 
            [affected_coords[1], affected_coords[0]] == self.snake_squares[-2])): 
                self._snake_ded()

    def _check_border_crossing(self, affected_coords, dir):
        """If the movement crosses the border, change the target coords accordingly"""
        if affected_coords[1]<0:
            #Crossing top or left border, based on dir
            affected_coords[1] = self.grid.columnrow[dir]-1 
            if self.room[not dir] > 0:
                affected_coords = self._checking_walls(affected_coords, dir)
            else: affected_coords = self._shift_to_open_square(affected_coords, dir)
        elif affected_coords[1]>=self.grid.columnrow[dir]:
            #Crossing bottom or right border, based on dir
            affected_coords[1] = 0
            if self.room[not dir] < len(self.room_sets)-1: 
                affected_coords = self._checking_walls(affected_coords, dir)
            else: affected_coords = self._shift_to_open_square(affected_coords, dir)
        return(affected_coords)

    def _checking_walls(self, affected_coords, dir):
        """Move to the next room if clear, or shift the snake to prevent instant death if blocked twice"""
        temp_check = self.file_setup.update_wall_squares_set(self.room_sets, current_room=False, 
                room = (self.room[0]+self.movement[1],self.room[1]+self.movement[0]))
        if [affected_coords[dir], affected_coords[not dir]] not in temp_check:
            if self.room_cooldown>self.snake_delay[self.stage]:
                self.room_cooldown = 0
                self._kill_squares(reset=True, remainder = 1) 
                self._next_room_setup((self.room[0]+self.movement[1], self.room[1]+self.movement[0]))
            else:
                affected_coords = [self.snake_head[dir], self.snake_head[not dir]-self.movement[dir]]
        else: 
            affected_coords = self._shift_to_open_square(affected_coords, dir)
        return(affected_coords)

    def _shift_to_open_square(self, affected_coords, dir):
        """In the odd scenario where the snake would hit a wall in the next room, but coming out the
            opposite side of the room would also hit a wall, shift the snake to the nearest open space
            on that wall. If there are none, tough luck"""
        #self.room_cooldown = 0
        if self.snake_map[affected_coords[dir], affected_coords[not dir]] == MI.WALL:
            for x in range(int(self.dimensions[not dir]/self.square_size)):
                if affected_coords[0]+x<self.dimensions[not dir]/self.square_size and (
                    self.snake_map[affected_coords[dir]+(not dir)*x, affected_coords[not dir]+(dir)*x] == MI.CLEAR):          
                    affected_coords[0]+=x
                    break
                elif affected_coords[0]-x>=0 and (self.snake_map[affected_coords[dir]-(not dir)*x, 
                        affected_coords[not dir]-dir*x] == MI.CLEAR):
                    affected_coords[0]-=x
                    break
        return(affected_coords)

    def _next_room_setup(self, new_room):
        """Switch the wall squares, enemys, food_positions, and background as a new room is entered"""
        self.room = new_room
        #print(self.room)
        self.snake_map = numpy.full((self.grid.number_rows, self.grid.number_columns), 
                fill_value = MI.CLEAR, dtype=object)
        self.homer = False
        if int(self.homer_info[self.room[0], self.room[1]][0]):
            info = self.homer_info[self.room[0], self.room[1]]
            for x in range(len(info)): info[x] = int(info[x])
            self.homer = Homing(self, info[1], info[4], [info[2], info[3]])
        self.file_setup.map_writeout(self.room_sets, itemid=MI.WALL)
        self.file_setup.map_writeout(self.game_food_copy, itemid=MI.FOOD)
        self.wall_squares = self.file_setup.update_wall_squares_set(self.room_sets)
        self.food_positions = self.file_setup.update_wall_squares_set(self.game_food_copy)
        self.enemys = []
        for x in range(len(self.enemy_sets[self.room[0], self.room[1]])):
            deleted = self.killed_enemys[self.room[0], self.room[1]]
            if type(deleted)!=list or (type(deleted)==list and x not in deleted):
                temp_list = self.file_setup.enemy_nonsense(self.enemy_sets, x)
                self.enemys.append(
                Enemy(self, self.enemy_info[self.room[0], self.room[1]][x][1], 
                set_path=True, path=temp_list, enemy_number=x))
        self.grid.initialize_background(self.room[0]*4+self.room[1])

    def _kill_squares(self, reset = False, remainder=1):
        """Remove the oldest snake square if the length has been exceeded"""
        initial_length = len(self.snake_squares)
        if reset:
            self.changed_frame = True
            for x in range(initial_length-(remainder-1)):
                deleted_square = self.snake_squares.pop(0)
                if self.snake_map[deleted_square[0], deleted_square[1]]!=MI.WALL:
                    self.snake_map[deleted_square[0], deleted_square[1]] = MI.CLEAR
        elif len(self.snake_squares) > self.number_squares:
            self.changed_frame = True
            deleted_square = self.snake_squares.pop(0)
            if self.snake_map[deleted_square[0], deleted_square[1]]!=MI.WALL:
                self.snake_map[deleted_square[0], deleted_square[1]] = MI.CLEAR
        
    def _food_check(self):
        """Check the snake head position, and determine if the food has been eaten"""
        if self.snake_head in self.food_positions:
            self.number_squares += 1
            self.food_positions.remove(self.snake_head)
            self.game_food_copy[self.room[0], self.room[1]] = []
            for x in self.food_positions:
                self.game_food_copy[self.room[0], self.room[1]].append(x[0])
                self.game_food_copy[self.room[0], self.room[1]].append(x[1])

    def _update_fps(self):
        """Update clock, then update fps and visual every 100 frames"""
        self.clock.tick(50)
        self.tick_update += 1
        if self.tick_update >= 100:
            self.current_fps = self.clock.get_fps()
            self.tick_update = 0
            self.fps_meter._prep_text(f"FPS: {round(self.current_fps)}")

    def _update_snake(self, x, coord_list, color):
        """Center each snake square in the appropriate spot, then finagle to make it look better"""
        adjustment = [0, 0]
        index = coord_list.index(x)
        if x != coord_list[-1]:
            for dir in range(2):
                if coord_list[index+1][dir]!=coord_list[index][dir]:
                    if x!=coord_list[0]:
                        if coord_list[index-1][not dir]==coord_list[index][not dir]:
                            adjustment[not dir] += 12
                        else:
                            for y in range(2): adjustment[y] += 6
                    else: adjustment[not dir] += 12
        if x == coord_list[-1]: 
            for y in range(2): adjustment[y]+=10
        square_stats = [self.snake_rect_size[0]+adjustment[0], self.snake_rect_size[1]+adjustment[1]]
        close_rect = pygame.Rect(self.grid.grid_array[x[0], x[1]].left, self.grid.grid_array[x[0], x[1]].top,
            square_stats[0], square_stats[1])
        close_rect.center = self.grid.grid_array[x[0], x[1]].center
        pygame.draw.rect(self.screen, color, close_rect)
        outer_color = [0, 0, 0]
        for x in range(3):
            if color[x]: outer_color[x] = color[x]-100
        pygame.draw.rect(self.screen, outer_color, close_rect, width = 2)

    def _update_screen(self):
        """Update the screen with the new frame"""
        self.changed_frame = False
        self.screen.fill((255, 255, 255))
        if self.screen_phase == RI.GAME:
            for row_number in range(len(self.grid.grid_array)):
                for column_number in range(len(self.grid.grid_array[0])):
                    square = self.snake_map[row_number, column_number]
                    if square==MI.WALL: 
                        pygame.draw.rect(self.screen, (50, 50, 50), self.grid.grid_array[row_number, column_number])
                        continue
                    elif square==MI.FOOD:
                        pygame.draw.rect(self.screen, (255, 0, 0), self.grid.grid_array[row_number, column_number])
                    else: 
                        self.grid.random_color_pattern(row_number, column_number)
                        if square == MI.SNAKE:
                            self._update_snake([row_number, column_number], self.snake_squares, (0, 255, 0))
            for enemy in self.enemys:
                for x in enemy.list_of_active_squares():
                    if type(x) == list: 
                        self._update_snake(x, enemy.list_of_active_squares(), (0, 0, 0))
                        #pygame.draw.rect(self.screen, (0, 0, 0), self.grid.grid_array[x[0], x[1]])
            if self.homer:
                for x in self.homer.enemy_squares:
                    self._update_snake(x, self.homer.enemy_squares, (255, 0, 0))
            self.snake_bite.draw_bite()
        elif self.screen_phase == RI.MENU:
            self.title.draw_text()
            self.start.draw_button()
        self.fps_meter.draw_text()
        pygame.display.flip()

    def _snake_ded(self):
        if self.save_changes:
            print("Saving")
            self.file_setup.write_out_to_file('Games/Snake/data_storage/wall_squares.txt', self.room_sets)
            self.file_setup.write_out_to_file('Games/Snake/data_storage/enemy_paths.txt', self.enemy_sets)
            self.file_setup.write_out_to_file('Games/Snake/data_storage/enemy_info.txt', self.enemy_info)
            self.file_setup.write_out_to_file('Games/Snake/data_storage/food_positions.txt', self.food_sets)
            self.file_setup.write_out_to_file('Games/Snake/data_storage/homer_data.txt', self.homer_info)
        sys.exit()

if __name__ == '__main__':
    snake = Snake()
    snake.run_game()