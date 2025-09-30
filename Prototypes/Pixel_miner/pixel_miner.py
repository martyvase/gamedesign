import pygame
import random
import sys

# === Константы ===
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
CHUNK_SIZE = 8

# Цвета (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (100, 200, 100)
BROWN = (139, 69, 19)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
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

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE // 2
        self.height = TILE_SIZE
        self.color = RED
        self.speed = 5
        self.inventory = {COAL: 0, IRON: 0, GOLD: 0, DIAMOND: 0}

class World:
    def __init__(self):
        self.chunks = {}
        self.generated_chunks = []

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
        surface_level = 0

        for local_y in range(CHUNK_SIZE):
            world_y = chunk_y * CHUNK_SIZE + local_y
            for local_x in range(CHUNK_SIZE):
                height_var = int(random.uniform(-1, 1))
                stone_level = surface_level + 2 + height_var

                if world_y > stone_level:
                    block = STONE
                    ore_chance = random.random()
                    if ore_chance < 0.02: block = COAL
                    elif ore_chance < 0.035: block = IRON
                    elif ore_chance < 0.042: block = GOLD
                    elif ore_chance < 0.045: block = DIAMOND
                    chunk_data[local_y][local_x] = block
                elif world_y == surface_level:
                    chunk_data[local_y][local_x] = DIRT
                elif world_y > surface_level:
                    chunk_data[local_y][local_x] = DIRT

        return chunk_data

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mine_x, mine_y = int(player.x), int(player.y + 1)
                    block_type = world.get_block(mine_x, mine_y)
                    if block_type != EMPTY:
                        world.set_block(mine_x, mine_y, EMPTY)
                        if block_type in player.inventory:
                            player.inventory[block_type] += 1

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1

        player.x += dx * player.speed * 0.1
        player.y += dy * player.speed * 0.1

        camera_x = player.x * TILE_SIZE - SCREEN_WIDTH // 2
        camera_y = player.y * TILE_SIZE - SCREEN_HEIGHT // 2

        screen.fill(BLACK)

        # Отрисовка мира
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

        # Отрисовка игрока и UI
        player_screen_x = player.x * TILE_SIZE - camera_x
        player_screen_y = player.y * TILE_SIZE - camera_y
        pygame.draw.rect(screen, player.color, (player_screen_x, player_screen_y, player.width, player.height))

        inventory_text = f"Уголь: {player.inventory[COAL]} | Железо: {player.inventory[IRON]} | Золото: {player.inventory[GOLD]} | Алмазы: {player.inventory[DIAMOND]}"
        text_surface = font.render(inventory_text, True, WHITE)
        screen.blit(text_surface, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
