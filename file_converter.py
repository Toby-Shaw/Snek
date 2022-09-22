import numpy

class File_Converter:
    def __init__(self, snake):
        self.snake = snake
        
    def file_to_room_sets(self, file_name, extra_layer=False):
        """From a file, convert all numbers into a list of coordinates"""
        f = open(file_name, 'r')
        string = str(f.read())
        self.read_squares = string.split()
        flag = [0, 0]
        list_container = numpy.empty((3, 3), dtype=object)
        for x in range(len(self.read_squares)):
            if not list_container[flag[0], flag[1]] and self.read_squares[x]!='||':
                list_container[flag[0], flag[1]] = [self.read_squares[x]]
            elif self.read_squares[x] != '||':
                list_container[flag[0], flag[1]].append(self.read_squares[x])
            else: 
                if flag[1]<list_container.shape[1]-1:
                    flag[1] += 1
                else: 
                    flag[1] = 0
                    flag[0] += 1
        if extra_layer:
            one_split = numpy.copy(list_container)
            list_container = numpy.empty((3, 3), dtype=object)
            for row in range(len(one_split)):
                for column in range(len(one_split[0])):
                    list_container[row, column] = []
                    for x in range(self.snake.max_enemy_count):
                        list_container[row, column].append([])
                    number = 0
                    if type(one_split[row, column])==list:
                        for x in one_split[row, column]:
                            if x != '|':
                                list_container[row, column][number].append(x)
                            else: number += 1
        return(list_container)

    def update_wall_squares_set(self, total_storage, current_room=True, room=None):
        """Update a list to reflect the new room, pulling data from the specified container list"""
        if current_room: self.room = self.snake.room
        else: self.room = room
        wanted_list = []
        if type(total_storage[self.room[0], self.room[1]])==list:
            for x in range((len(total_storage[self.room[0], self.room[1]])-1)):
                if not x % 2:
                    wanted_list.append([int(total_storage[self.room[0], self.room[1]][x]), 
                        int(total_storage[self.room[0], self.room[1]][x+1])])
        return(wanted_list)

    def map_writeout(self, total_storage, current_room=True, room=None, itemid = -1):
        """Pull from the container list to update the snake_map with wall or food info"""
        if current_room: self.room = self.snake.room
        else: self.room = room
        if type(total_storage[self.room[0], self.room[1]])==list:
            for x in range((len(total_storage[self.room[0], self.room[1]])-1)):
                if not x % 2:
                    self.snake.snake_map[int(total_storage[self.room[0], self.room[1]][x]), 
                        int(total_storage[self.room[0], self.room[1]][x+1])] = itemid
        #print(self.snake.snake_map)

    def enemy_nonsense(self, total_storage, enemy_number):
        """Return the wanted enemy path from the storage and with the enemy_number in proper format"""
        self.room = self.snake.room
        wanted_list = []
        if type(total_storage[self.room[0], self.room[1]])==list:
            for x in range(len(total_storage[self.room[0], self.room[1]][enemy_number])-1):
                #print(total_storage[self.room[0], self.room[1]][enemy_number][x])
                if not x % 2:
                    wanted_list.append([int(total_storage[self.room[0], self.room[1]][enemy_number][x]), 
                        int(total_storage[self.room[0], self.room[1]][enemy_number][x+1])])
        return(wanted_list)

    def refine_enemy_info(self, enemy_info):
        """If enemy_info sets are empty, set them as equal to the first enemy's info"""
        for row in range(len(enemy_info)):
            for column in range(len(enemy_info[0])):
                for info_pair in range(len(enemy_info[row, column])):
                    if len(enemy_info[row, column][info_pair])==0:
                        enemy_info[row, column][info_pair] = enemy_info[row, column][0]
                    for x in range(len(enemy_info[row, column][info_pair])):
                        enemy_info[row, column][info_pair][x] = int(enemy_info[row, column][info_pair][x])
        return(enemy_info)

    def write_out_to_file(self, file_name, array):
        """Go down to scalars, and write them one by one to the specific file, or at least attempt to"""
        file = open(file_name, 'w')
        write_out = ''
        for room in array:
            for coordinate_set in room:
                try:
                    try:
                        if type(coordinate_set[0])==list:
                            for set in coordinate_set:
                                if len(set)>0:
                                    for x in set:
                                        write_out += f'{str(x)} '
                                    write_out += '| '
                        else: 
                            for scalar in coordinate_set:
                                write_out += f'{str(scalar)} '
                    except:
                        for scalar in coordinate_set:
                            write_out += f'{str(scalar)} '
                except: pass
                write_out += '|| '
        file.write(str(write_out))