#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import shutil

def clear_screen():
    """Очистка экрана в зависимости от ОС"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_header():
    """Вывод заголовка"""
    clear_screen()
    print("=" * 60)
    print("          УСТАНОВЩИК PIXEL MINER")
    print("           (Windows/macOS/Linux)")
    print("=" * 60)
    print()

def check_python():
    """Проверяет наличие Python"""
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f" Python обнаружен: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Python не обнаружен!")
        return False

def check_pip():
    """Проверяет наличие pip"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print(" Pip обнаружен")
        return True
    except subprocess.CalledProcessError:
        print(" Pip не обнаружен!")
        return False

def install_pygame():
    """Устанавливает pygame"""
    print(" Установка библиотеки pygame...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pygame"], 
                      check=True)
        print(" Pygame успешно установлен")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Ошибка установки pygame: {e}")
        return False

def create_game_files():
    """Создает файлы игры"""
    print(" Создание файлов игры...")
    
    # Основной файл игры
    game_code = '''import pygame
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
'''
    
    with open("pixel_miner.py", "w", encoding="utf-8") as f:
        f.write(game_code)

def create_launch_scripts():
    """Создает скрипты для запуска под разные ОС"""
    system = platform.system()
    
    if system == "Windows":
        # BAT файл для Windows
        bat_content = '''@echo off
chcp 65001 >nul
echo Запуск Pixel Miner...
python pixel_miner.py
pause
'''
        with open("start_game.bat", "w", encoding="utf-8") as f:
            f.write(bat_content)
        print(" Создан start_game.bat")
        
    else:
        # Shell скрипт для macOS/Linux
        sh_content = '''#!/bin/bash
echo "Запуск Pixel Miner..."
python3 pixel_miner.py
read -p "Нажмите Enter для выхода..."
'''
        with open("start_game.sh", "w", encoding="utf-8") as f:
            f.write(sh_content)
        
        # Делаем скрипт исполняемым
        os.chmod("start_game.sh", 0o755)
        print(" Создан start_game.sh")

def create_desktop_shortcut():
    """Создает ярлык/скрипт запуска на рабочем столе"""
    system = platform.system()
    desktop_path = ""
    
    try:
        if system == "Windows":
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_content = f'''@echo off
chcp 65001 >nul
cd "{os.getcwd()}"
python pixel_miner.py
pause'''
            shortcut_file = os.path.join(desktop_path, "Pixel Miner.bat")
            with open(shortcut_file, "w") as f:
                f.write(shortcut_content)
                
        elif system == "Darwin":  # macOS
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_content = f'''#!/bin/bash
cd "{os.getcwd()}"
python3 pixel_miner.py
'''
            shortcut_file = os.path.join(desktop_path, "Pixel Miner.command")
            with open(shortcut_file, "w") as f:
                f.write(shortcut_content)
            os.chmod(shortcut_file, 0o755)
            
        else:  # Linux
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_content = f'''#!/bin/bash
cd "{os.getcwd()}"
python3 pixel_miner.py
'''
            shortcut_file = os.path.join(desktop_path, "Pixel Miner.sh")
            with open(shortcut_file, "w") as f:
                f.write(shortcut_content)
            os.chmod(shortcut_file, 0o755)
        
        print(f" Ярлык создан на рабочем столе")
        
    except Exception as e:
        print(f" Не удалось создать ярлык: {e}")

def show_instructions():
    """Показывает инструкции по запуску"""
    system = platform.system()
    
    print("\n" + "=" * 60)
    print("УСТАНОВКА ЗАВЕРШЕНА!")
    print("=" * 60)
    
    if system == "Windows":
        print("\n ДЛЯ ЗАПУСКА ИГРЫ:")
        print("1. Дважды щелкните по 'Pixel Miner.bat' на рабочем столе")
        print("2. Или запустите 'start_game.bat' в папке игры")
        print("3. Или выполните: python pixel_miner.py")
        
    elif system == "Darwin":  # macOS
        print("\n🎮 ДЛЯ ЗАПУСКА ИГРЫ:")
        print("1. Дважды щелкните по 'Pixel Miner.command' на рабочем столе")
        print("2. Или запустите 'start_game.sh' в папке игры")
        print("3. Или выполните: python3 pixel_miner.py")
        print("\n Если возникли проблемы с запуском:")
        print("   - Откройте Terminal")
        print("   - Перейдите в папку игры: cd 'путь/к/папке'")
        print("   - Выполните: chmod +x start_game.sh")
        print("   - Запустите: ./start_game.sh")
        
    else:  # Linux
        print("\n ДЛЯ ЗАПУСКА ИГРЫ:")
        print("1. Дважды щелкните по 'Pixel Miner.sh' на рабочем столе")
        print("2. Или запустите 'start_game.sh' в папке игры")
        print("3. Или выполните: python3 pixel_miner.py")
    
    print("\n УПРАВЛЕНИЕ:")
    print("   WASD или Стрелки - Движение")
    print("   Пробел - Добыть блок")
    print("   ESC или Закрыть окно - Выход")

def main():
    print_header()
    
    # Проверка Python
    if not check_python():
        print("\n Установите Python с https://python.org")
        input("Нажмите Enter для выхода...")
        return
    
    # Проверка pip
    if not check_pip():
        print("\n Pip не установлен. Переустановите Python")
        input("Нажмите Enter для выхода...")
        return
    
    # Установка pygame
    if not install_pygame():
        print("\n Не удалось установить pygame")
        input("Нажмите Enter для выхода...")
        return
    
    # Создание файлов
    create_game_files()
    create_launch_scripts()
    create_desktop_shortcut()
    
    show_instructions()
    
    # Предложение запустить игру
    launch = input("\n Запустить игру сейчас? (y/n): ").lower().strip()
    if launch == 'y':
        print("Запуск игры...")
        try:
            if platform.system() == "Windows":
                subprocess.Popen([sys.executable, "pixel_miner.py"])
            else:
                subprocess.Popen([sys.executable, "pixel_miner.py"])
        except Exception as e:
            print(f"Ошибка при запуске: {e}")
    
    input("\nНажмите Enter для завершения...")

if __name__ == "__main__":
    main()