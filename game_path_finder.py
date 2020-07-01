import pygame
from interface_path_finder import get_algorithm
from math import sqrt
import time

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
'''

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
crashed = False

pygame.init()

display_width = 800
display_height = 800
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Path finderrrz')
clock = pygame.time.Clock()
block_size = 20
block_shrink = 2


def draw_grid(reset_grid_states=True):
    grid = []
    if reset_grid_states:
        grid_states = {}

    for x in range(display_width//block_size):
        for y in range(display_height//block_size):
            rect = pygame.Rect(x*block_size, y*block_size,
                               block_size, block_size)
            grid.append(rect)

            # dict for state of rectangles. True = passable, False = wall
            if reset_grid_states:
                grid_states[(x, y)] = 1

            pygame.draw.rect(game_display, black, rect, 1)
    if reset_grid_states:
        return grid, grid_states


def get_rect_by_mouse(rects):
    pos = pygame.mouse.get_pos()
    for rect in rects:
        if(rect.collidepoint(pos)):
            new_rect = pygame.Rect(
                rect.x, rect.y, block_size, block_size)
    return new_rect, pos


def redraw_start_end(start_pos, end_pos):
    # redraw start and end position

    if type(start_pos) == tuple:
        new_rect = pygame.Rect(
            start_pos[0]*block_size, start_pos[1]*block_size, block_size, block_size)
        pygame.draw.rect(game_display, light_yellow, new_rect)
    if type(end_pos) == tuple:
        new_rect = pygame.Rect(
            end_pos[0]*block_size, end_pos[1]*block_size, block_size, block_size)
        pygame.draw.rect(game_display, red, new_rect)


def redraw_surrounding(grid_states):
    for cell_pos in grid_states.keys():
        state = grid_states[cell_pos]

        coords = (
            cell_pos[0]*block_size+(block_shrink//2), cell_pos[1]*block_size+(block_shrink//2))

        # redraw walls
        if state == False:
            new_rect = pygame.Rect(
                coords[0], coords[1], block_size-block_shrink, block_size-block_shrink)
            pygame.draw.rect(game_display, black, new_rect)
        # redraw water

        if int(state) == 3:
            new_rect = pygame.Rect(
                coords[0], coords[1], block_size-block_shrink, block_size-block_shrink)
            pygame.draw.rect(game_display, blue, new_rect)


def main(algorithm):
    print('___________\n')
    start_set = start_pos = False
    end_set = end_pos = False
    # need just some starting values for if
    start_pos = -1
    end = -1
    drawing = False

    # these are only needed once. no need to redraw. Uses cpu so not redrawn
    game_display.fill(white)
    rects, grid_states = draw_grid()

    # running loop
    global crashed
    while not crashed:
        # EVENTS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                crashed = True

            # draw wall
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False

            # place water
            if pygame.key.get_pressed()[pygame.K_w]:
                new_rect, pos = get_rect_by_mouse(rects)
                pygame.draw.rect(game_display, blue, new_rect)
                water_pos = (pos[0]//block_size, pos[1]//block_size)
                # set cost for water to 3
                grid_states[water_pos] = 3

            # place start_pos
            if pygame.key.get_pressed()[pygame.K_s]:
                new_rect, pos = get_rect_by_mouse(rects)
                pygame.draw.rect(game_display, light_yellow, new_rect)
                start_pos = (pos[0]//block_size, pos[1]//block_size)

                # needed if pos is changed
                game_display.fill(white)
                draw_grid(reset_grid_states=False)
                redraw_start_end(start_pos, end_pos)
                redraw_surrounding(grid_states)

                print(f'start was set to {start_pos}')

            # place end_pos
            if pygame.key.get_pressed()[pygame.K_e] and not end_set:
                new_rect, pos = get_rect_by_mouse(rects)
                pygame.draw.rect(game_display, red, new_rect)
                end_pos = (pos[0]//block_size, pos[1]//block_size)

                # needed if pos is changed
                game_display.fill(white)
                draw_grid(reset_grid_states=False)
                redraw_start_end(start_pos, end_pos)
                redraw_surrounding(grid_states)

                print(f'end was set to {end_pos}')

            # reset to start
            if pygame.key.get_pressed()[pygame.K_r]:
                algorithm = get_algorithm().lower()
                main(algorithm)

            # change algorithm
            if pygame.key.get_pressed()[pygame.K_c]:
                algorithm = get_algorithm().lower()

            # clear path finding
            if pygame.key.get_pressed()[pygame.K_l]:
                game_display.fill(white)
                draw_grid(reset_grid_states=False)
                redraw_start_end(start_pos, end_pos)
                redraw_surrounding(grid_states)

            # delete a cell
            if pygame.key.get_pressed()[pygame.K_d]:
                pos = pygame.mouse.get_pos()
                coords = (pos[0]//block_size, pos[1]//block_size)
                grid_states[coords] = True
                game_display.fill(white)
                draw_grid(reset_grid_states=False)
                redraw_start_end(start_pos, end_pos)
                redraw_surrounding(grid_states)

            # start path finding
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and start_pos and end_pos:
                start_time = time.time()

                shortest_path, water_walk = a_star(
                    start_pos=start_pos, end_pos=end_pos, algorithm=algorithm)

                if not shortest_path:
                    print('You cancelled the algorithm.')
                    continue

                print(
                    f'Finding path with {algorithm} took {time.time()-start_time}')

                # comment out this block to see tried nodes
                game_display.fill(white)
                draw_grid(reset_grid_states=False)
                redraw_surrounding(grid_states)

                try:
                    # show shortest path
                    for node in shortest_path:
                        pygame.event.get()
                        color = green
                        for water_node in water_walk:
                            if node == water_node.position:
                                color = (204, 0, 204)

                        new_rect = pygame.Rect(
                            node[0]*block_size+(block_shrink//2), node[1]*block_size+(block_shrink//2), block_size-block_shrink, block_size-block_shrink)
                        pygame.draw.rect(game_display, color, new_rect)

                    redraw_start_end(start_pos, end_pos)

                except Exception as e:
                    print('There is no path to the end.')
                    # print(f'You failed because {e}')
            # pygame.time.wait(50)

        # LOGIC
        if drawing:
            # clicked rectangles become walls
            new_rect, pos = get_rect_by_mouse(rects)
            coords = (pos[0]//block_size, pos[1]//block_size)
            grid_states[coords] = False
            if coords == end or coords == start_pos:
                print('NO!')
            else:
                pygame.draw.rect(game_display, black, new_rect)

        pygame.display.update()
        clock.tick(60)  # in fps


# _____________________A STAR ____________________________


        class Node():
            def __init__(self, parent=None, position=None):
                self.parent = parent
                self.position = position

                # rating functions
                self.f = 0
                self.g = 0
                self.h = 0

            def __eq__(self, other):
                return self.position == other.position

        def a_star(start_pos, end_pos, algorithm, visualize=True):
            global crashed
            start_node = Node(None, start_pos)
            end_node = Node(None, end_pos)
            open_list = [start_node]
            closed_list = []
            water_walk = []
            path = []

            while len(open_list) > 0:
                # call this or get lag of doom
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        crashed = True

                if crashed:
                    return False, False

                # get node with lowest f value
                open_list.sort(key=lambda node: node.f)
                current_node = open_list[0]

                # update lists
                open_list.remove(current_node)
                closed_list.append(current_node)

                # check for finish
                if current_node == end_node:

                    print(
                        f'Total cost: {int(current_node.f)}')
                    while current_node is not None:
                        path.append(current_node.position)
                        current_node = current_node.parent

                    return path[::-1], water_walk

                # generate children
                for new_pos in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    found_double = False
                    # get node posi
                    new_node_pos = (
                        current_node.position[0] + new_pos[0], current_node.position[1] + new_pos[1])

                    # check if node in map
                    if new_node_pos not in grid_states.keys():
                        continue

                    # check if nod is wall
                    cost = int(grid_states[new_node_pos])
                    if not cost:
                        continue

                    for closed_node in closed_list:
                        if new_node_pos == closed_node.position:
                            found_double = True

                    if found_double:
                        continue

                    # create new Node || Node(<parent>, <pos>)
                    new_node = Node(current_node, new_node_pos)

                    # might need to take sqrt here when not all nodes have cost of 1
                    new_node.g = current_node.g + cost

                    # euclidean distance
                    if algorithm == 'dijkstra':
                        new_node.h = 0

                    elif algorithm == 'a_star':
                        new_node.h = int(sqrt(((new_node.position[0]-end_node.position[0])
                                               ** 2)+((new_node.position[1]-end_node.position[1])**2)))/1.47

                    elif algorithm == 'greedy_best_first_search':
                        new_node.h = int(sqrt(((new_node.position[0]-end_node.position[0]) ** 2)+(
                            (new_node.position[1]-end_node.position[1])**2)))*100

                    new_node.f = new_node.g+new_node.h

                    for open_node in open_list:
                        if new_node.position == open_node.position:

                            found_double = True

                    if found_double:
                        continue

                    # append recruits for open_list
                    open_list.append(new_node)

                    if cost == 3:
                        water_walk.append(new_node)

                if visualize:
                    # # draw open and closed list
                    # for open_node in open_list:
                    #     color = green
                    #     new_rect = pygame.Rect(
                    #         open_node.position[0]*block_size+(block_shrink//2), open_node.position[1]*block_size+(block_shrink//2), block_size-block_shrink, block_size-block_shrink)
                    #     pygame.draw.rect(game_display, color, new_rect)

                    for closed_node in closed_list:
                        color = dark_green
                        # color water_walk diffent
                        if closed_node in water_walk:
                            color = light_blue

                        new_rect = pygame.Rect(
                            closed_node.position[0]*block_size+(block_shrink//2), closed_node.position[1]*block_size+(block_shrink//2), block_size-block_shrink, block_size-block_shrink)
                        pygame.draw.rect(game_display, color, new_rect)

                    # redraw start and end
                    new_rect = pygame.Rect(
                        start_pos[0]*block_size, start_pos[1]*block_size, block_size, block_size)
                    pygame.draw.rect(game_display, light_yellow, new_rect)

                    new_rect = pygame.Rect(
                        end_pos[0]*block_size, end_pos[1]*block_size, block_size, block_size)
                    pygame.draw.rect(game_display, red, new_rect)

                    pygame.display.update()
                    clock.tick(60)  # in fps

                    # time.sleep(0.1)

        # DRAW
        pygame.display.update()
        clock.tick(60)  # in fps

    pygame.quit()


algorithm = get_algorithm().lower()
# algorithm = 'dijkstra'
main(algorithm)
