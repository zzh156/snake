import sys
import random
import pygame
from pygame.examples.cursors import image
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
    # screen.blit("snake.jpg",(0,0))


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

def draw_level():
    font = pygame.font.Font(None, 48)
    level_text = font.render(f'Level: {level}', True, (0, 0, 0))
    screen.blit(level_text, (10, height - 80))

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
    score_text = font.render(f'Score: {score}', True, (0, 0, 0))
    restart_text = font.render('Press R to Restart', True, (0, 0, 0))
    
    screen.fill((255, 255, 255))  # 填充背景
    screen.blit(text, (width // 2 - text.get_width() // 2, height // 3))
    screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2))
    screen.blit(restart_text, (width // 2 - restart_text.get_width() // 2, height // 2 + 50))
    
    pygame.display.flip()

    # 等待玩家按下 R 键重新开始
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_r:
                    waiting = False  # 退出等待状态以重新开始

def reset_game():
    global snake_list, food_list, walls, running, score, speed, level
    snake_list = [(100, 100), (80, 100), (60, 100)]
    food_list = [(200, 200)]
    walls = generate_walls(level)  # 根据关卡生成墙
    score = 0  # 重置分数
    speed = base_speed  # 重置速度
    level = 1  # 重置关卡
    running = True

def generate_walls(level):
    walls = []
    # 根据关卡增加障碍物
    if level == 1:
        walls = [(200, 100), (220, 100), (240, 100)]
    elif level == 2:
        walls = [(random.randint(0, (width // 20) - 1) * 20, random.randint(0, (height // 20) - 1) * 20) for _ in range(8)]
    elif level == 3:
        walls = [(random.randint(0, (width // 20) - 1) * 20, random.randint(0, (height // 20) - 1) * 20) for _ in range(18)]
    # 确保障碍物不与蛇或食物重叠
    walls = [pos for pos in walls if pos not in snake_list and pos not in food_list]
    return walls


def choose_mode_and_difficulty():
    global mode, speed, base_speed
    while True:
        draw_background()
        image = pygame.image.load("snake.jpg")
        # 获取窗口尺寸
        window_width, window_height = screen.get_size()

        # 计算缩放比例以保持图片宽高比
        scale_factor = min(window_width / image.get_width(), window_height / image.get_height())

        # 根据缩放比例调整图片大小
        new_image_size = (int(image.get_width() * scale_factor), int(image.get_height() * scale_factor))
        scaled_image = pygame.transform.scale(image, new_image_size)

        # 计算图片居中的位置
        image_x = (window_width - new_image_size[0]) // 2
        image_y = 0

        # 绘制背景图片
        screen.blit(scaled_image, (image_x, image_y))

        font = pygame.font.Font(None, 74)
        text = font.render('Choose Mode:', True, (0, 0, 0))
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 3))

        manual_text = font.render('1. Manual', True, (0, 0, 0))
        ai_text = font.render('2. AI', True, (0, 0, 0))
        screen.blit(manual_text, (width // 2 - manual_text.get_width() // 2, height // 2))
        screen.blit(ai_text, (width // 2 - ai_text.get_width() // 2, height // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_1:
                    mode = 'manual'
                    choose_difficulty()
                    return
                elif event.key == K_2:
                    mode = 'ai'
                    choose_difficulty()
                    return

def choose_difficulty():
    global base_speed, speed
    while True:
        draw_background()
        font = pygame.font.Font(None, 74)
        text = font.render('Choose Difficulty:', True, (0, 0, 0))
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 3))
        
        easy_text = font.render('1. Easy', True, (0, 0, 0))
        medium_text = font.render('2. Medium', True, (0, 0, 0))
        hard_text = font.render('3. Hard', True, (0, 0, 0))
        screen.blit(easy_text, (width // 2 - easy_text.get_width() // 2, height // 2))
        screen.blit(medium_text, (width // 2 - medium_text.get_width() // 2, height // 2 + 50))
        screen.blit(hard_text, (width // 2 - hard_text.get_width() // 2, height // 2 + 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_1:
                    base_speed = 100  # 基础速度
                    speed = base_speed
                    return
                elif event.key == K_2:
                    base_speed = 75  # 中等速度
                    speed = base_speed
                    return
                elif event.key == K_3:
                    base_speed = 50  # 高速
                    speed = base_speed
                    return

# 初始化pygame
pygame.init()
width, height = 800, 760  # 调整窗口高度以留出分数区域
screen = pygame.display.set_mode((width, height))

# 游戏状态
base_speed = 100  # 默认基础速度
level = 1  # 当前关卡
reset_game()
mode = 'manual'  # 默认模式
direction = (20, 0)  # 默认向右移动

choose_mode_and_difficulty()  # 选择游戏模式和难度

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if mode == 'manual':
            if event.type == pygame.KEYDOWN:
                if event.key == K_UP:
                    direction = (0, -20)
                elif event.key == K_DOWN:
                    direction = (0, 20)
                elif event.key == K_LEFT:
                    direction = (-20, 0)
                elif event.key == K_RIGHT:
                    direction = (20, 0)

    draw_background()
    draw_snake()
    draw_food()
    draw_walls()
    draw_score()  # 绘制分数
    draw_level()  # 绘制当前关卡

    if check_food():
        add_food()
        score += 1  # 增加分数
        speed = max(50, base_speed - score * 2)  # 随得分提升速度

    if check_dead():
        game_over()
        reset_game()  # 重新开始游戏

    # 关卡提升
    if score >= 10 and level == 1:  # 第一个关卡
        level = 2
        walls = generate_walls(level)  # 更新障碍物
        print("Level up! Now at level: 2")
    elif score >= 20 and level == 2:  # 第二个关卡
        level = 3
        walls = generate_walls(level)  # 更新障碍物
        print("Level up! Now at level: 3")

    # 更新蛇的位置
    if mode == 'manual':
        head = snake_list[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        snake_list.insert(0, new_head)
        snake_list.pop()  # 移动蛇身
    elif mode == 'ai':
        head = snake_list[0]
        food = min(food_list, key=lambda f: (head[0] - f[0])**2 + (head[1] - f[1])**2)
        path = astar(head, food, walls, snake_list)
        if path and len(path) > 1:
            snake_list.insert(0, path[1])
            snake_list.pop()
        else:
            snake_list.insert(0, head)  # 正常移动

    pygame.display.flip()
    pygame.time.delay(speed)

pygame.quit()
sys.exit()