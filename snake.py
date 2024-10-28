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
    """
    A*算法用于寻找到达目标的最短路径。
    
    参数:
    start -- 起始位置坐标
    goal -- 目标位置坐标
    walls -- 墙壁位置列表，避免路径规划穿过墙壁
    snake -- 蛇身位置列表，避免路径规划穿过蛇身
    
    返回:
    如果找到路径，则返回从起始位置到目标位置的路径列表。
    如果没有找到路径，则返回None。
    """
    # 初始化开放列表和封闭列表
    open_list = []
    closed_list = []
    
    # 创建起始节点和目标节点
    start_node = Node(start)
    goal_node = Node(goal)
    
    # 将起始节点添加到开放列表中
    open_list.append(start_node)

    # 当开放列表不为空时，进行循环
    while open_list:
        # 选择开放列表中f值最小的节点作为当前节点
        current_node = min(open_list, key=lambda node: node.f)
        # 从开放列表中移除当前节点，并将其添加到封闭列表中
        open_list.remove(current_node)
        closed_list.append(current_node.position)

        # 如果当前节点是目标节点，則回溯路径并返回
        if current_node.position == goal:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]

        # 遍历当前节点的相邻节点
        for new_position in [(0, -20), (0, 20), (-20, 0), (20, 0)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # 检查新节点是否在封闭列表、墙壁或蛇身上，如果是，则跳过
            if node_position in closed_list or node_position in walls or node_position in snake:
                continue

            # 创建新节点，并计算其g、h和f值
            neighbor_node = Node(node_position, current_node)
            neighbor_node.g = current_node.g + 1
            neighbor_node.h = ((neighbor_node.position[0] - goal[0]) ** 2) + ((neighbor_node.position[1] - goal[1]) ** 2)
            neighbor_node.f = neighbor_node.g + neighbor_node.h

            # 如果新节点可以添加到开放列表中，则进行添加
            if add_to_open(open_list, neighbor_node):
                open_list.append(neighbor_node)

    # 如果没有找到路径，则返回None
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
    """
    检查蛇是否处于死亡状态。
    
    本函数通过检查蛇头的位置和是否与蛇身或墙壁相撞来判断蛇是否死亡。
    
    返回:
    - True: 如果蛇处于死亡状态。
    - False: 如果蛇没有处于死亡状态。
    """
    # 获取蛇头的位置
    head = snake_list[0]
    
    # 检查蛇头是否超出游戏边界
    if head[0] < 0 or head[0] >= width or head[1] < 0 or head[1] >= height:
        return True
    
    # 检查蛇头是否撞到蛇身或墙壁
    if head in snake_list[1:] or head in walls:
        return True
    
    # 如果以上条件都不满足，蛇未死亡
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
    """
    重置游戏状态。
    
    此函数将游戏中的所有元素（蛇的位置、食物的位置、障碍物、游戏运行状态和分数）重置为初始状态。
    这样做是为了确保每局游戏开始时，玩家都在相同的条件下开始游戏。
    """
    global snake_list, food_list, walls, running, score
    snake_list = [(100, 100), (80, 100), (60, 100)]  # 初始化蛇的位置
    food_list = [(200, 200)]  # 初始化食物的位置
    walls = [(200, 100), (220, 100), (240, 100), (260, 100), (280, 100)]  # 添加障碍物
    score = 0  # 重置分数
    running = True  # 设置游戏为运行状态

# 初始化pygame
# 设置窗口大小，通过窗口大小绘制地图
pygame.init()
width, height = 600, 540  # 调整窗口高度以留出分数区域
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

    # 更新屏幕显示
    pygame.display.flip()
    # 控制游戏速度
    pygame.time.delay(100)

pygame.quit()
sys.exit()
