# import random

# def generate_maze(width, height):
#     maze = [['#' for _ in range(width)] for _ in range(height)]

#     def is_valid(x, y):
#         return 0 <= x < width and 0 <= y < height

#     def carve_path(x, y):
#         directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
#         random.shuffle(directions)
#         for dx, dy in directions:
#             new_x, new_y = x + 2 * dx, y + 2 * dy
#             if is_valid(new_x, new_y) and maze[new_y][new_x] == '#':
#                 maze[y + dy][x + dx] = '.'
#                 maze[new_y][new_x] = '.'
#                 carve_path(new_x, new_y)

#     start_x, start_y = random.randrange(1, width, 2), random.randrange(1, height, 2)
#     maze[start_y][start_x] = ' '
#     carve_path(start_x, start_y)

#     return maze

# def print_maze(maze):
#     for row in maze:
#         print("".join(row))

# if __name__ == "__main__":
#     width, height = 50, 50
#     maze = generate_maze(width, height)
#     print_maze(maze)

import random


MAP_WIDTH = 100
MAP_HEIGHT = 100

from tunneling import TunnelingAlgorithm
ta = TunnelingAlgorithm()
level = ta.generateLevel(MAP_WIDTH, MAP_HEIGHT)

for row in level:
    print(row)
