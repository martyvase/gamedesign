import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арканоид на Python")

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

# Игровые объекты
class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 20
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 40
        self.speed = 8
        
    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < WIDTH - self.width:
            self.x += self.speed

class Ball:
    def __init__(self):
        self.radius = 10
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx = 5 * random.choice([-1, 1])
        self.dy = -5
        
    def draw(self):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)
        
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        # Отскок от стен
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.dx = -self.dx
        if self.y <= self.radius:
            self.dy = -self.dy
            
    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx = 5 * random.choice([-1, 1])
        self.dy = -5

class Brick:
    def __init__(self, x, y, color):
        self.width = 80
        self.height = 30
        self.x = x
        self.y = y
        self.color = color
        self.visible = True
        
    def draw(self):
        if self.visible:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# Создание объектов
paddle = Paddle()
ball = Ball()

# Создание блоков
bricks = []
for row in range(5):
    for col in range(10):
        brick = Brick(col * 82 + 10, row * 35 + 50, random.choice(COLORS))
        bricks.append(brick)

# Счет
score = 0
font = pygame.font.Font(None, 36)

# Игровой цикл
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Управление
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle.move("left")
    if keys[pygame.K_RIGHT]:
        paddle.move("right")
    
    # Движение мяча
    ball.move()
    
    # Проверка столкновения с ракеткой
    if (ball.y + ball.radius >= paddle.y and 
        ball.x >= paddle.x and 
        ball.x <= paddle.x + paddle.width):
        ball.dy = -abs(ball.dy)  # Всегда отскакивает вверх
        # Меняем угол в зависимости от места попадания
        hit_pos = (ball.x - paddle.x) / paddle.width
        ball.dx = 8 * (hit_pos - 0.5)  # -4 до +4
    
    # Проверка столкновения с блоками
    for brick in bricks:
        if (brick.visible and 
            ball.x + ball.radius >= brick.x and 
            ball.x - ball.radius <= brick.x + brick.width and
            ball.y + ball.radius >= brick.y and 
            ball.y - ball.radius <= brick.y + brick.height):
            
            brick.visible = False
            ball.dy = -ball.dy
            score += 10
    
    # Проверка проигрыша
    if ball.y >= HEIGHT:
        ball.reset()
        score = max(0, score - 5)  # Штраф за пропуск мяча
    
    # Проверка выигрыша
    if all(not brick.visible for brick in bricks):
        win_text = font.render("Вы выиграли! Счет: " + str(score), True, GREEN)
        screen.blit(win_text, (WIDTH//2 - 150, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
    
    # Отрисовка
    screen.fill(BLACK)
    paddle.draw()
    ball.draw()
    for brick in bricks:
        brick.draw()
    
    # Отображение счета
    score_text = font.render("Счет: " + str(score), True, WHITE)
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
sys.exit()