import sys
import random
import pygame
from pygame.locals import *

# A*寻路算法的节点类
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

def astar(start, goal, walls, snake):
    open_list = []
    closed_list = []
    start_node = Node(start)
    goal_node = Node(goal)
    
    open_list.append(start_node)

    while open_list:
        current_node = min(open_list, key=lambda node: node.f)
        open_list.remove(current_node)
        closed_list.append(current_node.position)

        if current_node.position == goal:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]

        for new_position in [(0, -20), (0, 20), (-20, 0), (20, 0)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            if node_position in closed_list or node_position in walls or node_position in snake:
                continue

            neighbor_node = Node(node_position, current_node)
            neighbor_node.g = current_node.g + 1
            neighbor_node.h = ((neighbor_node.position[0] - goal[0]) ** 2) + ((neighbor_node.position[1] - goal[1]) ** 2)
            neighbor_node.f = neighbor_node.g + neighbor_node.h

            if add_to_open(open_list, neighbor_node):
                open_list.append(neighbor_node)

    return None

def add_to_open(open_list, neighbor_node):
    for node in open_list:
        if neighbor_node.position == node.position and neighbor_node.g >= node.g:
            return False
    return True

def draw_background():
    screen.fill((255, 255, 255))

def draw_snake():
    for segment in snake_list:
        pygame.draw.rect(screen, (0, 128, 0), (segment[0], segment[1], 20, 20))

def draw_food():
    for f in food_list:
        pygame.draw.rect(screen, (255, 0, 0), (f[0], f[1], 20, 20))

def draw_walls():
    for wall in walls:
        pygame.draw.rect(screen, (128, 128, 128), (wall[0], wall[1], 20, 20))

def draw_score():
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, (0, 0, 0))
    screen.blit(score_text, (10, height - 40))

def check_food():
    if snake_list[0] in food_list:
        food_list.remove(snake_list[0])
        snake_list.append(snake_list[-1])  # 增加蛇身
        return True
    return False

def check_dead():
    head = snake_list[0]
    if head[0] < 0 or head[0] >= width or head[1] < 0 or head[1] >= height:
        return True
    if head in snake_list[1:] or head in walls:
        return True
    return False

def add_food():
    while True:
        position = (random.randint(0, (width // 20) - 1) * 20, random.randint(0, (height // 20) - 2) * 20)  # 留出分数区域
        if position not in snake_list and position not in food_list and position not in walls:
            food_list.append(position)
            break

def game_over():
    font = pygame.font.Font(None, 74)
    text = font.render('Game Over', True, (0, 0, 0))
    screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(2000)

def reset_game():
    global snake_list, food_list, walls, running, score
    snake_list = [(100, 100), (80, 100), (60, 100)]
    food_list = [(200, 200)]
    walls = [(200, 100), (220, 100), (240, 100), (260, 100), (280, 100)]  # 添加障碍物
    score = 0  # 重置分数
    running = True

# 初始化pygame
pygame.init()
width, height = 800, 760  # 调整窗口高度以留出分数区域
screen = pygame.display.set_mode((width, height))

# 游戏状态
reset_game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_background()
    draw_snake()
    draw_food()
    draw_walls()
    draw_score()  # 绘制分数

    if check_food():
        add_food()
        score += 1  # 增加分数

    if check_dead():
        game_over()
        reset_game()  # 重新开始游戏

    # 更新蛇的位置
    head = snake_list[0]
    # 在这里添加AI逻辑控制蛇的移动
    food = min(food_list, key=lambda f: (head[0] - f[0])**2 + (head[1] - f[1])**2)
    path = astar(head, food, walls, snake_list)
    if path and len(path) > 1:
        snake_list.insert(0, path[1])
        snake_list.pop()
    else:
        snake_list.insert(0, head)  # 正常移动

    pygame.display.flip()
    pygame.time.delay(100)

pygame.quit()
sys.exit()
