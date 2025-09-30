import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Breaker")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

BRICK_COLORS = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE]
BRICK_WIDTH = 80
BRICK_HEIGHT = 30
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_GAP = 5

class Brick:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color
        self.visible = True
    
    def draw(self, surface):
        if self.visible:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 2)

class Game:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        # Ракетка
        self.paddle_width = 100
        self.paddle_height = 20
        self.paddle_x = WIDTH // 2 - self.paddle_width // 2
        self.paddle_y = HEIGHT - 40
        self.paddle_speed = 8
        
        # Мяч
        self.ball_radius = 10
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_dx = 5 * random.choice([-1, 1])
        self.ball_dy = -5
        
        # Игровые параметры
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.level_complete = False
        
        # Создание блоков
        self.create_bricks()
    
    def create_bricks(self):
        self.bricks = []
        start_x = (WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_GAP))) // 2
        
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
                y = 50 + row * (BRICK_HEIGHT + BRICK_GAP)
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                brick = Brick(x, y, color)
                self.bricks.append(brick)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (self.game_over or self.level_complete):
                    self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def update(self):
        if self.game_over or self.level_complete:
            return
        
        # Управление ракеткой
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.paddle_x > 0:
            self.paddle_x -= self.paddle_speed
        if keys[pygame.K_RIGHT] and self.paddle_x < WIDTH - self.paddle_width:
            self.paddle_x += self.paddle_speed
        
        # Движение мяча
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Отскок от стен
        if self.ball_x <= self.ball_radius or self.ball_x >= WIDTH - self.ball_radius:
            self.ball_dx = -self.ball_dx
        
        if self.ball_y <= self.ball_radius:
            self.ball_dy = -self.ball_dy
        
        # Проверка столкновения с ракеткой
        paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height)
        if (self.ball_y + self.ball_radius >= self.paddle_y and 
            self.ball_x >= self.paddle_x and 
            self.ball_x <= self.paddle_x + self.paddle_width and
            self.ball_dy > 0):
            
            hit_pos = (self.ball_x - self.paddle_x) / self.paddle_width
            self.ball_dx = 8 * (hit_pos - 0.5)
            self.ball_dy = -abs(self.ball_dy)
        
        # Проверка столкновения с блоками
        ball_rect = pygame.Rect(self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, 
                               self.ball_radius * 2, self.ball_radius * 2)
        
        for brick in self.bricks:
            if brick.visible and ball_rect.colliderect(brick.rect):
                brick.visible = False
                self.score += 10
                
                if abs(ball_rect.centerx - brick.rect.centerx) > abs(ball_rect.centery - brick.rect.centery):
                    self.ball_dx = -self.ball_dx
                else:
                    self.ball_dy = -self.ball_dy
                break
        
        # Проверка проигрыша (мяч упал)
        if self.ball_y >= HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball_x = WIDTH // 2
                self.ball_y = HEIGHT // 2
                self.ball_dx = 5 * random.choice([-1, 1])
                self.ball_dy = -5
        
        # Проверка завершения уровня
        if all(not brick.visible for brick in self.bricks):
            self.level_complete = True
    
    def draw(self):
        screen.fill(BLACK)
        
        # Отрисовка ракетки
        pygame.draw.rect(screen, BLUE, (self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height))
        
        # Отрисовка мяча
        pygame.draw.circle(screen, RED, (int(self.ball_x), int(self.ball_y)), self.ball_radius)
        
        # Отрисовка блоков
        for brick in self.bricks:
            brick.draw(screen)
        
        # Отрисовка счета и жизней
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Счет: {self.score}", True, WHITE)
        lives_text = font.render(f"Жизни: {self.lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 120, 10))
        
        # Сообщения
        if self.game_over:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("ИГРА ОКОНЧЕНА", True, RED)
            restart_text = font.render("Нажмите R для рестарта", True, WHITE)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
        
        elif self.level_complete:
            font = pygame.font.Font(None, 72)
            win_text = font.render("УРОВЕНЬ ПРОЙДЕН!", True, GREEN)
            restart_text = font.render("Нажмите R для нового уровня", True, WHITE)
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
