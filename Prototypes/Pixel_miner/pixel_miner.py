import pygame
import random
import sys

# === Константы ===
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
CHUNK_SIZE = 16

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (100, 200, 100)
BROWN = (139, 69, 19)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 0, 139)

# Типы блоков
EMPTY = 0
DIRT = 1
STONE = 2
COAL = 3
IRON = 4
GOLD = 5
DIAMOND = 6

BLOCK_COLORS = {
    EMPTY: BLACK, DIRT: BROWN, STONE: GRAY,
    COAL: (50, 50, 50), IRON: (200, 200, 200),
    GOLD: YELLOW, DIAMOND: DARK_BLUE
}

# === Игрок ===
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE // 2
        self.height = TILE_SIZE
        self.color = RED
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.inventory = {COAL: 0, IRON: 0, GOLD: 0, DIAMOND: 0}

    def move(self, world, keys):
        self.vx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -0.1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = 0.1

        # Прыжок
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
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
        for dx in [0, 0.9]:
            for dy in [0, 0.9]:
                block = world.get_block(int(px + dx), int(py + dy))
                if block != EMPTY:
                    return True
        return False


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

                    # Пещеры
                    if random.random() < 0.05:
                        block = EMPTY

                    chunk_data[local_y][local_x] = block

        return chunk_data


# === Функции ===
def mine_block(world, player, direction):
    dx, dy = direction
    target_x = int(player.x + dx)
    target_y = int(player.y + dy)
    block_type = world.get_block(target_x, target_y)
    if block_type != EMPTY:
        world.set_block(target_x, target_y, EMPTY)
        if block_type in player.inventory:
            player.inventory[block_type] += 1


def mine_block_at(world, player, mouse_pos, camera_x, camera_y):
    # координаты блока под мышкой
    world_x = (mouse_pos[0] + camera_x) // TILE_SIZE
    world_y = (mouse_pos[1] + camera_y) // TILE_SIZE

    # ограничение: можно ломать только блоки рядом с игроком
    if abs(world_x - int(player.x)) <= 1 and abs(world_y - int(player.y)) <= 1:
        block_type = world.get_block(world_x, world_y)
        if block_type != EMPTY:
            world.set_block(world_x, world_y, EMPTY)
            if block_type in player.inventory:
                player.inventory[block_type] += 1


# === Главная функция ===
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pixel Miner")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 20)

    world = World()
    player = Player(SCREEN_WIDTH // 2 // TILE_SIZE, 0)

    camera_x, camera_y = 0, 0
    running = True
    while running:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    mine_block(world, player, (0, -1))
                elif event.key == pygame.K_DOWN:
                    mine_block(world, player, (0, 1))
                elif event.key == pygame.K_LEFT:
                    mine_block(world, player, (-1, 0))
                elif event.key == pygame.K_RIGHT:
                    mine_block(world, player, (1, 0))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mine_block_at(world, player, event.pos, camera_x, camera_y)

        # Движение игрока
        player.move(world, keys)

        # Камера
        camera_x = player.x * TILE_SIZE - SCREEN_WIDTH // 2
        camera_y = player.y * TILE_SIZE - SCREEN_HEIGHT // 2

        # Отрисовка
        screen.fill(BLACK)
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
                            color = BLOCK_COLORS.get(block_type, BLACK)
                            if block_type != EMPTY:
                                pygame.draw.rect(screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                                pygame.draw.rect(screen, (50, 50, 50), (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        # Игрок
        player_screen_x = player.x * TILE_SIZE - camera_x
        player_screen_y = player.y * TILE_SIZE - camera_y
        pygame.draw.rect(screen, player.color, (player_screen_x, player_screen_y, player.width, player.height))

        # Инвентарь
        inventory_text = f"Уголь: {player.inventory[COAL]} | Железо: {player.inventory[IRON]} | Золото: {player.inventory[GOLD]} | Алмазы: {player.inventory[DIAMOND]}"
        text_surface = font.render(inventory_text, True, WHITE)
        screen.blit(text_surface, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
