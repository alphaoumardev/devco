# # n number of nodes in the graph
# # g adjacency list representing graph
# from turtledemo.planet_and_moon import G
#
# visited = [False] * Graph.size()
# def dfs(Graph, v):
#     stack = [v]
#     while len(stack) > 0:
#         v = stack.pop()
#         if not visited[v]:
#             visit(v)
#             visited[v] = True
#             for w in Graph.neighbours(v):
#                 if not visited[w]:
#                     stack.append(w)
#
#     start_node = 0
#     dfs(start_node, v)


import random

# Define the dimensions of the maze
width = 20
height = 10

# Create a grid to represent the maze
maze = [[0 for _ in range(width)] for _ in range(height)]

# Define directions (up, down, left, right)
directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]


def is_valid(x, y):
    return 0 <= x < width and 0 <= y < height


def generate_maze(x, y):
    maze[y][x] = 1  # Mark the current cell as visited

    random.shuffle(directions)  # Randomize the order of directions

    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy

        if is_valid(new_x, new_y) and maze[new_y][new_x] == 0:
            # Carve a path and recursively visit the next cell
            maze[y + dy // 2][x + dx // 2] = 1
            generate_maze(new_x, new_y)


# Start the maze generation from the top-left corner
generate_maze(0, 0)

# Print the generated maze
for row in maze:
    print(" ".join(["#" if cell == 1 else " " for cell in row]))
