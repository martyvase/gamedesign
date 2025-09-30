import pygame
import random
import sys
import math

# === Константы ===
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 30
CHUNK_SIZE = 16

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GRAY = (150, 150, 150)
RED = (200, 50, 50)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (135, 206, 235)
EYE_WHITE = (255, 255, 255)
EYE_BLACK = (0, 0, 0)
HIGHLIGHT = (0, 255, 0)

# Типы блоков
EMPTY = 0
DIRT = 1
STONE = 2
COAL = 3
IRON = 4
GOLD = 5
DIAMOND = 6

BLOCK_COLORS = {
    EMPTY: LIGHT_BLUE,  # небо
    DIRT: BROWN,
    STONE: GRAY,
    COAL: (50, 50, 50),
    IRON: (200, 200, 200),
    GOLD: YELLOW,
    DIAMOND: DARK_BLUE
}


# === Игрок ===
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y # теперь прямо на y=0
        self.width = TILE_SIZE
        self.height = TILE_SIZE * 1
        self.color = RED

        # Физика
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True

        # Инвентарь
        self.inventory = {DIRT: 10, COAL: 0, IRON: 0, GOLD: 0, DIAMOND: 0}  # стартовая земля

        # Направление добычи
        self.mine_dir = (1, 0)

    def move(self, world, keys):
        self.vx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -0.1
            self.facing_right = False
            self.mine_dir = (-1, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = 0.1
            self.facing_right = True
            self.mine_dir = (1, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.mine_dir = (0, -1)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.mine_dir = (0, 1)

        # Прыжок
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = -0.3
            self.on_ground = False

        # Гравитация
        self.vy += 0.01
        if self.vy > 0.3:
            self.vy = 0.3

        # Движение по X
        self.x += self.vx
        if self.check_collision(world):
            self.x -= self.vx

        # Движение по Y
        self.y += self.vy
        if self.check_collision(world):
            self.y -= self.vy
            self.vy = 0
            self.on_ground = True

    def check_collision(self, world):
        px, py = int(self.x), int(self.y)
        for dx in [0, 0.8]:
            for dy in [1, 1.5]:
                block = world.get_block(int(px + dx), int(py + dy))
                if block != EMPTY:
                    return True
        return False

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x * TILE_SIZE - camera_x
        screen_y = self.y * TILE_SIZE - camera_y

        # Тело
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))

        # Голова (верхняя часть тела)
        head_h = self.height // 2
        head_rect = pygame.Rect(screen_x, screen_y, self.width, head_h)

        # Глаза
        eye_size = self.width // 5
        offset_x = 5 if self.facing_right else -5
        eye_y = head_rect.y + head_h // 3

        left_eye = pygame.Rect(head_rect.x + self.width // 4, eye_y, eye_size, eye_size)
        right_eye = pygame.Rect(head_rect.x + self.width * 3 // 4 - eye_size, eye_y, eye_size, eye_size)

        pygame.draw.rect(screen, EYE_WHITE, left_eye)
        pygame.draw.rect(screen, EYE_WHITE, right_eye)

        # Зрачки (сдвигаются в сторону взгляда)
        pupil_size = eye_size // 2
        pygame.draw.rect(screen, EYE_BLACK,
                         (left_eye.x + offset_x // 2, left_eye.y, pupil_size, pupil_size))
        pygame.draw.rect(screen, EYE_BLACK,
                         (right_eye.x + offset_x // 2, right_eye.y, pupil_size, pupil_size))
       



# === Мир ===
class World:
    def __init__(self):
        self.chunks = {}

    def get_block(self, world_x, world_y):
        chunk_x = world_x // CHUNK_SIZE
        chunk_y = world_y // CHUNK_SIZE
        local_x = world_x % CHUNK_SIZE
        local_y = world_y % CHUNK_SIZE

        chunk = self.chunks.get((chunk_x, chunk_y))
        if chunk is None:
            chunk = self.generate_chunk(chunk_x, chunk_y)
            self.chunks[(chunk_x, chunk_y)] = chunk
        return chunk[local_y][local_x]

    def set_block(self, world_x, world_y, block_type):
        chunk_x = world_x // CHUNK_SIZE
        chunk_y = world_y // CHUNK_SIZE
        local_x = world_x % CHUNK_SIZE
        local_y = world_y % CHUNK_SIZE

        if (chunk_x, chunk_y) in self.chunks:
            self.chunks[(chunk_x, chunk_y)][local_y][local_x] = block_type

    def generate_chunk(self, chunk_x, chunk_y):
        chunk_data = [[EMPTY for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        surface_level = 2

        for local_y in range(CHUNK_SIZE):
            world_y = chunk_y * CHUNK_SIZE + local_y
            for local_x in range(CHUNK_SIZE):
                if world_y < surface_level:
                    continue  # воздух
                elif world_y == surface_level:
                    chunk_data[local_y][local_x] = DIRT
                else:
                    block = STONE
                    ore_chance = random.random()
                    if ore_chance < 0.02: block = COAL
                    elif ore_chance < 0.035: block = IRON
                    elif ore_chance < 0.042: block = GOLD
                    elif ore_chance < 0.045: block = DIAMOND
                    chunk_data[local_y][local_x] = block

        # === добавляем большие пещеры ===
        if random.random() < 0.2:  # шанс пещеры в чанке
            cave_x = random.randint(4, CHUNK_SIZE - 4)
            cave_y = random.randint(4, CHUNK_SIZE - 4)
            cave_radius = random.randint(3, 6)
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    dist = math.sqrt((x - cave_x) ** 2 + (y - cave_y) ** 2)
                    if dist < cave_radius:
                        chunk_data[y][x] = EMPTY

        return chunk_data


# === Подсветка блока ===
def get_mouse_block(mouse_pos, camera_x, camera_y):
    world_x = (mouse_pos[0] + camera_x) // TILE_SIZE
    world_y = (mouse_pos[1] + camera_y) // TILE_SIZE
    return int(world_x), int(world_y)


def highlight_block(screen, player, camera_x, camera_y, world, mouse_pos=None):
    if mouse_pos:
        mx, my = get_mouse_block(mouse_pos, camera_x, camera_y)
        if abs(mx - int(player.x)) <= 2 and abs(my - int(player.y)) <= 2:
            block_type = world.get_block(mx, my)
            if block_type != EMPTY:
                screen_x = mx * TILE_SIZE - camera_x
                screen_y = my * TILE_SIZE - camera_y
                pygame.draw.rect(screen, HIGHLIGHT, (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 3)
                return (mx, my)
    return None


# === Интерфейс ===
def draw_ui(screen, player):
    font = pygame.font.SysFont('Arial', 20)
    inventory_text = (
        f"Земля: {player.inventory[DIRT]} | "
        f"Уголь: {player.inventory[COAL]} | "
        f"Железо: {player.inventory[IRON]} | "
        f"Золото: {player.inventory[GOLD]} | "
        f"Алмазы: {player.inventory[DIAMOND]}"
    )
    text_surface = font.render(inventory_text, True, WHITE)
    screen.blit(text_surface, (10, 10))


# === Главная функция ===
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pixel Miner - Fixed")
    clock = pygame.time.Clock()

    world = World()
    player = Player(SCREEN_WIDTH // 1 // TILE_SIZE, 0)

    camera_x, camera_y = 0, 0
    running = True
    mouse_highlight = None

    while running:
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_highlight:
                mx, my = mouse_highlight
                if event.button == 1:  # ЛКМ — сломать
                    world.set_block(mx, my, EMPTY)
                elif event.button == 3 and player.inventory[DIRT] > 0:  # ПКМ — поставить землю
                    if world.get_block(mx, my) == EMPTY:
                        world.set_block(mx, my, DIRT)
                        player.inventory[DIRT] -= 1

        # Движение игрока
        player.move(world, keys)

        # Камера
        camera_x = player.x * TILE_SIZE - SCREEN_WIDTH // 2
        camera_y = player.y * TILE_SIZE - SCREEN_HEIGHT // 2

        # Отрисовка
        screen.fill(LIGHT_BLUE)
        start_chunk_x = int(camera_x // TILE_SIZE) // CHUNK_SIZE
        end_chunk_x = int((camera_x + SCREEN_WIDTH) // TILE_SIZE) // CHUNK_SIZE + 1
        start_chunk_y = int(camera_y // TILE_SIZE) // CHUNK_SIZE
        end_chunk_y = int((camera_y + SCREEN_HEIGHT) // TILE_SIZE) // CHUNK_SIZE + 1

        for chunk_x in range(start_chunk_x, end_chunk_x):
            for chunk_y in range(start_chunk_y, end_chunk_y):
                for local_y in range(CHUNK_SIZE):
                    for local_x in range(CHUNK_SIZE):
                        world_x = chunk_x * CHUNK_SIZE + local_x
                        world_y = chunk_y * CHUNK_SIZE + local_y
                        screen_x = world_x * TILE_SIZE - camera_x
                        screen_y = world_y * TILE_SIZE - camera_y

                        if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
                            block_type = world.get_block(world_x, world_y)
                            if block_type != EMPTY:
                                color = BLOCK_COLORS.get(block_type, BLACK)
                                pygame.draw.rect(screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                                pygame.draw.rect(screen, (70, 70, 70),
                                                 (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        # Игрок
        player.draw(screen, camera_x, camera_y)

        # Подсветка
        mouse_highlight = highlight_block(screen, player, camera_x, camera_y, world, mouse_pos)

        # UI
        draw_ui(screen, player)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
