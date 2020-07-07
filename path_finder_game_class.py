from tkinter import *
import pygame
from math import sqrt
import time
import random

# define colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (44, 255, 44)
red = (255, 44, 44)
blue = (44, 44, 255)
light_blue = (91, 200, 255)
light_green = (102, 255, 102)
dark_green = (0, 102, 51)
light_yellow = (255, 255, 125)
light_red = (255, 153, 153)
orange = (255, 153, 42)
pink = (204, 0, 204)


class path_choosing_interface():

    def __init__(self):
        self.passing_var = None
        self.get_algorithm()

    def choose(self, algorithm):
        print('_____________________')
        print('You chose ' + algorithm)
        self.passing_var = algorithm

    def get_algorithm(self):
        root = Tk()
        root.title('Path finderrrz choose')

        info_label = Label(root, text='Choose an algorithm', padx=60,
                           pady=20).grid(row=0, columnspan=2)

        quit_but = Button(root, text='start', padx=60, pady=20,
                          command=root.destroy).grid(row=4, columnspan=2)

        a_star = Button(root, text='A*', padx=40, pady=20,
                        command=lambda: self.choose('A_star')).grid(row=1, column=0)

        # for other algorithms
        dijkstra = Button(root, text='Dijkstra', padx=27, pady=20,
                          command=lambda: self.choose('Dijkstra')).grid(row=1, column=1)
        gbfs = Button(root, text='gbfs', padx=35, pady=20,
                      command=lambda: self.choose('Greedy_best_first_search')).grid(row=2, column=0)
        some_button2 = Button(root, text='fill', padx=40, pady=20,
                              command=lambda: self.choose('fill')).grid(row=2, column=1)

        root.mainloop()


class Node():
    def __init__(self, rect=None, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.rect = rect
        # rating functions
        self.f = 0
        self.g = 0
        self.h = 0
        self.cost = 0

    def __eq__(self, other):
        return self.position == other.position


class path_finder():
    '''
    mouse click -> wall
    w -> water (cost = 3)
    r -> reset map and algorithm
    c -> change algorithm only
    s -> start point
    e -> end point
    l -> clear drawn path
    d -> delete cell
    SPACE -> start path finding
    m -> random walls 100 
    n -> random water 50 that are not walls
    '''

    def __init__(self, algorithm):
        self.start_pos = False
        self.end_pos = False
        self.run = True
        self.algorithm = str(algorithm).lower()
        self.water_cost = 4
        self.display_width = 800
        self.display_height = 800
        self.game_display = pygame.display.set_mode(
            (self.display_width, self.display_height))

        self.clock = pygame.time.Clock()
        self.block_size = 20
        self.block_shrink = 2

        self.draw_grid()

        pygame.init()
        pygame.display.set_caption('Path finderrrz')
        self.run_game()

    def draw_grid(self, reset_node_states=True):
        if reset_node_states == True:
            self.nodes = []

        self.max_x = self.display_width//self.block_size
        self.max_y = self.display_height//self.block_size
        for x in range(self.max_x):
            for y in range(self.max_y):
                rect = pygame.Rect(x*self.block_size, y*self.block_size,
                                   self.block_size, self.block_size)

                if (reset_node_states == True):
                    new_node = Node(rect=rect, position=(x, y))
                    new_node.cost = 1
                    self.nodes.append(new_node)
                pygame.draw.rect(self.game_display, black, rect, 1)

    def set_node(self, state, rect_pos=None):
        pos = pygame.mouse.get_pos()
        coords = (pos[0]//self.block_size, pos[1]//self.block_size)
        cost = 1

        if state == 'wall':
            color = black
            cost = -1

        elif state == 'water':
            color = blue
            cost = self.water_cost

        elif state == 'closed':
            if rect_pos == self.start_pos or rect_pos == self.end_pos:
                return
            color = dark_green

            # color water_walk diffent
            for water in self.water_walk:
                if rect_pos == water.position:
                    color = light_blue
                    break

            pos = (rect_pos[0]*self.block_size,
                   rect_pos[1]*self.block_size)

        elif state == 'path':
            if rect_pos == self.start_pos or rect_pos == self.end_pos:
                return
            color = light_green
            # color water_walk diffent
            for water in self.water_walk:
                if rect_pos == water.position:
                    color = pink
                    break

            pos = (rect_pos[0]*self.block_size,
                   rect_pos[1]*self.block_size)

        elif state == 'maze':
            if rect_pos == self.start_pos or rect_pos == self.end_pos:
                return
            color = black
            cost = -1
            pos = (rect_pos[0]*self.block_size,
                   rect_pos[1]*self.block_size)
            rect_pos = None

        elif state == 'sea':
            if rect_pos == self.start_pos or rect_pos == self.end_pos:
                return
            color = blue
            cost = self.water_cost
            pos = (rect_pos[0]*self.block_size,
                   rect_pos[1]*self.block_size)
            rect_pos = None

        elif state == 'open':
            if rect_pos == self.start_pos or rect_pos == self.end_pos:
                return
            color = light_red
            # color water_walk diffent
            for water in self.water_walk:
                if rect_pos == water.position:
                    color = orange
                    break

            pos = (rect_pos[0]*self.block_size,
                   rect_pos[1]*self.block_size)

        elif state == 'start':
            if self.start_pos:
                # delete old start
                color = white
                new_rect = pygame.Rect(
                    self.start_pos[0]*self.block_size+(self.block_shrink//2), self.start_pos[1]*self.block_size+(self.block_shrink//2), self.block_size-self.block_shrink, self.block_size-self.block_shrink)
                pygame.draw.rect(self.game_display, color, new_rect)

            color = light_yellow
            cost = 0
            self.start_pos = coords

        elif state == 'end':
            if self.end_pos:
                # delete old end
                color = white
                new_rect = pygame.Rect(
                    self.end_pos[0]*self.block_size+(self.block_shrink//2), self.end_pos[1]*self.block_size+(self.block_shrink//2), self.block_size-self.block_shrink, self.block_size-self.block_shrink)
                pygame.draw.rect(self.game_display, color, new_rect)

            color = red
            cost = 0
            self.end_pos = coords

        elif state == 'delete':
            color = white
            cost = 1

        for node in self.nodes:
            if node.rect.collidepoint(pos):
                new_rect = pygame.Rect(
                    node.rect.x+(self.block_shrink//2), node.rect.y+(self.block_shrink//2), self.block_size-self.block_shrink, self.block_size-self.block_shrink)
                if not rect_pos:
                    node.cost = cost
                break

        pygame.draw.rect(self.game_display, color, new_rect)

    def redraw_start_end(self):
        if self.start_pos:
            # kann man das noch sinnvoll lesen? nein. hab ich bock all variablen kürzere namen zu geben? nein.
            new_rect = pygame.Rect(
                self.start_pos[0]*self.block_size+(self.block_shrink//2), self.start_pos[1]*self.block_size+(self.block_shrink//2), self.block_size-self.block_shrink, self.block_size-self.block_shrink)

            pygame.draw.rect(self.game_display, light_yellow, new_rect)

        if self.end_pos:
            new_rect = pygame.Rect(
                self.end_pos[0]*self.block_size+(self.block_shrink//2), self.end_pos[1]*self.block_size+(self.block_shrink//2), self.block_size-self.block_shrink, self.block_size-self.block_shrink)

            pygame.draw.rect(self.game_display, red, new_rect)

    def redraw_surrounding(self):
        for node in self.nodes:
            # redraw walls
            if (node.cost == -1):
                new_rect = pygame.Rect(
                    node.rect.x+(self.block_shrink//2), node.rect.y+(self.block_shrink//2), self.block_size-self.block_shrink, self.block_size-self.block_shrink)
                pygame.draw.rect(self.game_display, black, new_rect)
            # redraw water
            elif node.cost == self.water_cost:
                new_rect = pygame.Rect(
                    node.rect.x+(self.block_shrink//2), node.rect.y+(self.block_shrink//2), self.block_size-self.block_shrink, self.block_size-self.block_shrink)
                pygame.draw.rect(self.game_display, blue, new_rect)

    def run_game(self):
        self.game_display.fill(white)
        self.draw_grid()

        while self.run:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.run = False

                # draw wall
                if (1, 0, 0) == pygame.mouse.get_pressed():
                    self.set_node('wall')

                # place water
                elif (0, 0, 1) == pygame.mouse.get_pressed():
                    self.set_node('water')

                # set start position
                elif pygame.key.get_pressed()[pygame.K_s]:
                    self.set_node('start')

                # set end position
                elif pygame.key.get_pressed()[pygame.K_e]:
                    self.set_node('end')

                # restart
                elif pygame.key.get_pressed()[pygame.K_r]:
                    my_algorithm = str(
                        path_choosing_interface().passing_var).lower()
                    path_finder(my_algorithm)

                # change algorithm
                elif pygame.key.get_pressed()[pygame.K_c]:
                    self.algorithm = str(
                        path_choosing_interface().passing_var).lower()

                # clear path finding
                elif pygame.key.get_pressed()[pygame.K_l]:

                    self.game_display.fill(white)
                    self.draw_grid(reset_node_states=False)
                    self.redraw_start_end()
                    self.redraw_surrounding()

                # delete a cell
                elif pygame.key.get_pressed()[pygame.K_d]:
                    self.set_node('delete')

                # create random maze with k blocks:
                elif pygame.key.get_pressed()[pygame.K_m]:
                    maze_stones = random.choices(self.nodes, k=100)
                    for stone in maze_stones:
                        self.set_node('maze', rect_pos=stone.position)

                elif pygame.key.get_pressed()[pygame.K_n]:
                    possible_waters = [
                        node for node in self.nodes if node.cost != -1]
                    water_places = random.choices(possible_waters, k=50)
                    for water in water_places:
                        self.set_node('sea', rect_pos=water.position)

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.start_pos and self.end_pos:
                    self.a_star()

            pygame.display.update()
            self.clock.tick(60)  # in fps

    # _____________________A STAR ____________________________
    def a_star(self, visualize=True):
        start_node = Node(parent=None, position=self.start_pos)
        end_node = Node(parent=None, position=self.end_pos)
        open_list = [start_node]
        closed_list = []
        self.water_walk = []
        self.path = []

        while len(open_list) > 0:
            # call this or get lag of doom
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

            if not self.run:
                return

            # get node with lowest f value
            open_list.sort(key=lambda node: node.f)
            current_node = open_list[0]

            # update lists
            open_list.remove(current_node)
            closed_list.append(current_node)

            # check for finish
            if current_node == end_node:
                total_cost = int(current_node.f)

                while current_node is not None:
                    self.path.append(current_node.position)
                    current_node = current_node.parent

                for cell in self.path:
                    self.set_node('path', rect_pos=cell)
                    self.redraw_start_end()
                print(
                    f'Total cost: {total_cost} with {len(self.path)} used nodes')
                return

            # generate children
            for new_pos in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                found_double = False

                new_node_pos = (
                    current_node.position[0] + new_pos[0], current_node.position[1] + new_pos[1])

                # check if in map
                if (new_node_pos[0] >= self.max_x) or (new_node_pos[0] < 0) or (new_node_pos[1] >= self.max_y) or (new_node_pos[1] < 0):
                    continue

                # check if wall
                for cell in self.nodes:
                    if cell.position == new_node_pos:
                        cost = cell.cost
                        if cost == -1:
                            found_double = True
                            break

                for closed_node in closed_list:
                    if new_node_pos == closed_node.position:
                        found_double = True
                        break

                if found_double:
                    continue

                # create new Node || Node(<parent>, <pos>)
                new_node = Node(parent=current_node, position=new_node_pos)

                # might need to take sqrt here when not all nodes have cost of 1
                new_node.g = current_node.g + cost

                # euclidean distance
                if self.algorithm == 'dijkstra':
                    new_node.h = 0

                elif self.algorithm == 'a_star':
                    new_node.h = int(sqrt(((new_node.position[0]-end_node.position[0])
                                           ** 2)+((new_node.position[1]-end_node.position[1])**2)))/1.47

                elif self.algorithm == 'greedy_best_first_search':
                    new_node.h = int(sqrt(((new_node.position[0]-end_node.position[0]) ** 2)+(
                        (new_node.position[1]-end_node.position[1])**2)))*100

                new_node.f = new_node.g+new_node.h

                for open_node in open_list:
                    if new_node == open_node:

                        found_double = True

                if found_double:
                    continue

                # append recruits for open_list
                open_list.append(new_node)

                if cost == self.water_cost:
                    self.water_walk.append(new_node)

            if visualize:
                # for open_node in open_list:
                #     self.set_node('open', rect_pos=open_node.position)

                self.set_node('closed', closed_list[-1].position)

                # for closed_node in closed_list:
                #     self.set_node('closed', rect_pos=closed_node.position)

                # self.redraw_start_end()
                pygame.display.update()
                self.clock.tick(60)  # in fps

        print('NO SOLUTION!')
        pygame.display.update()
        self.clock.tick(60)  # in fps


if __name__ == '__main__':
    # set algorithm wtih tkinter
    my_algorithm = path_choosing_interface().passing_var
    # init game
    path_finder(my_algorithm)
