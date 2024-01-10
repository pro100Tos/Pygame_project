import pygame
import os
import sys
import random
import sqlite3
from copy import deepcopy


size_player = p_width, p_height = 30, 40

conn = sqlite3.connect("coins.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS coins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        x INTEGER,
        y INTEGER
    )
''')
conn.commit()


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()

count_coin = 0

def print_collected_coins():
    print(f"Coins Collected: {count_coin}")
    conn.close()
    sys.exit()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, coins_group)
        original_image = load_image("monetca.png", colorkey=-1)
        self.image = pygame.transform.scale(original_image, (30, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_db = x // tile_width
        self.y_db = y // tile_height
        add_coin_to_db(self.x_db, self.y_db)
        self.collected = False

    def update(self):
        if not self.collected:
            if pygame.sprite.spritecollide(self, all_sprites, False):
                self.collected = True
                coins_group.remove(self)

def check_coin_collection(player):
    global count_coin
    collected_coins = pygame.sprite.spritecollide(player, coins_group, True)
    count_coin += len(collected_coins)
    for coin in collected_coins:
        x_db = coin.x_db
        y_db = coin.y_db
        # код для удаления монеты с экрана, если нужно
        all_sprites.remove(coin)

def generate_coins_around_walls():
    for _ in range(NUMBER_OF_COINS):
        rand_x = random.randint(1, WIDTH - 2)  # Генерация координат в пределах ширины минус 2
        rand_y = random.randint(1, HEIGHT - 2)  # Генерация координат в пределах высоты минус 2
        if level[rand_y][rand_x] == '.':
            Coin(rand_x * tile_width, rand_y * tile_height)

def add_coin_to_db(x, y):
    conn = sqlite3.connect("coins.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO coins (x, y) VALUES (?, ?)", (x, y))
    conn.commit()
    conn.close()

def load_image(name, colorkey=None):
    fullname = os.path.join('images_data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    elif colorkey is None:
        image = image.convert_alpha()
    return image


def load_image_data_tile(name, colorkey=None):
    fullname = os.path.join('data_tile', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data_tile/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            elif level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == '*':
                Ladder('ladder', x, y)
            elif level[y][x] == '%':
                Block('block', x, y)
            elif level[y][x] == '$':
                Coin(x * tile_width, y * tile_height)
                add_coin_to_db(x, y)  # Добавление монетки в базу данных

    # Генерация случайных местоположений монет
    for _ in range(10):
        rand_x = random.randint(0, len(level[0]) - 1)
        rand_y = random.randint(0, len(level) - 1)
        while level[rand_y][rand_x] != '.':
            rand_x = random.randint(0, len(level[0]) - 1)
            rand_y = random.randint(0, len(level) - 1)
        Coin(rand_x * tile_width, rand_y * tile_height)
        add_coin_to_db(rand_x, rand_y)

    return x, y


def navigation(level):
    n = len(level)
    m = len(level[0])
    tile_mas1 = ".*"
    tile_mas2 = "%#*"
    main_data = [[[] for j in range(m)] for i in range(n)]
    for i in range(n):
        for j in range(m):
            level_clone = deepcopy(level)
            mas_for_main_data = [[[] for x in range(m)] for y in range(n)]
            mas_for_main_data[i][j] = []
            mas = [(i, j)]
            while len(mas) > 0:
                active_mas = []
                for z in mas:
                    y = z[0]
                    x = z[1]
                    reserv_MFMD = mas_for_main_data[y][x][:]
                    if x > 0:
                        if level_clone[y][x - 1] in tile_mas1 and level_clone[y + 1][x - 1] in tile_mas2:
                            active_mas.append((y, x - 1))
                            reserv_MFMD.append("left")
                            mas_for_main_data[y][x - 1] = reserv_MFMD[:]
                    reserv_MFMD = mas_for_main_data[y][x][:]
                    if x < m - 1:
                        if level_clone[y][x + 1] in tile_mas1 and level_clone[y + 1][x + 1] in tile_mas2:
                            active_mas.append((y, x + 1))
                            reserv_MFMD.append("right")
                            mas_for_main_data[y][x + 1] = reserv_MFMD[:]
                    reserv_MFMD = mas_for_main_data[y][x][:]
                    try:
                        if level_clone[y][x] in tile_mas1 and level_clone[y + 1][x] in tile_mas1:
                            active_mas.append((y + 1, x))
                            reserv_MFMD.append("down")
                            mas_for_main_data[y + 1][x] = reserv_MFMD[:]
                    except Exception:
                        pass
                    reserv_MFMD = mas_for_main_data[y][x][:]
                    try:
                        if level_clone[y][x] == "*" and level_clone[y - 1][x] in tile_mas1:
                            active_mas.append((y - 1, x))
                            reserv_MFMD.append("up")
                            mas_for_main_data[y - 1][x] = reserv_MFMD[:]
                    except Exception:
                        pass
                    level_clone[y] = level_clone[y][:x] + "0" + level_clone[y][x + 1:]
                mas.clear()
                mas = active_mas
            main_data[i][j] = deepcopy(mas_for_main_data)
    return main_data


class Hero(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = load_image("idle.png", colorkey=-1)
        self.animCount = 0
        self.state = load_image("idle.png", colorkey=-1)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 63
        self.run = [load_image("Push1.png", colorkey=-1), load_image("Push2.png", colorkey=-1),
                    load_image("Push3.png", colorkey=-1), load_image("Push4.png", colorkey=-1),
                    load_image("Push5.png", colorkey=-1), load_image("Push6.png", colorkey=-1),
                    load_image("Push7.png", colorkey=-1), load_image("Push8.png", colorkey=-1),
                    load_image("Push9.png", colorkey=-1), load_image("Push10.png", colorkey=-1),
                    load_image("Push11.png", colorkey=-1), load_image("Push12.png", colorkey=-1),
                    load_image("Push13.png", colorkey=-1), load_image("Push14.png", colorkey=-1),
                    load_image("Push15.png", colorkey=-1), load_image("Push16.png", colorkey=-1),]
        self.left = False
        self.right = False

    def draw_run(self):
        key_pressed_is = pygame.key.get_pressed()
        self.left = False
        self.right = False

        if level[(self.rect.y + 41) // 25][(self.rect.x + 15) // 30] == ".":
            self.rect.y += 3
        else:
            if key_pressed_is[pygame.K_LEFT]:
                self.rect.x -= 3
                self.left = True
            if key_pressed_is[pygame.K_RIGHT]:
                self.rect.x += 3
                self.right = True
            if key_pressed_is[pygame.K_UP] and level[(self.rect.y + 35) // 25][(self.rect.x + 15) // 30] == "*":
                self.rect.y -= 3
                check_coin_collection(self)
            if key_pressed_is[pygame.K_DOWN] and level[(self.rect.y + 41) // 25][(self.rect.x + 15) // 30] == "*":
                self.rect.y += 3
                check_coin_collection(self)
        check_coin_collection(self)

    def update(self):
        if self.animCount + 1 >= 32:
            self.animCount = 0
        if self.left:
            self.image = self.run[self.animCount // 2]
            self.image = pygame.transform.scale(self.image, size_player)
            self.image = pygame.transform.flip(self.image, True, False)
            self.animCount += 1
        elif self.right:
            self.image = self.run[self.animCount // 2]
            self.image = pygame.transform.scale(self.image, size_player)
            self.animCount += 1
        else:
            self.image = self.state
            self.image = pygame.transform.scale(self.image, size_player)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, *group, hero):
        super().__init__(*group)
        self.image = load_image("goblin_run1.png", colorkey=-1)
        self.animCount = 0
        self.state = load_image("goblin_run1.png", colorkey=-1)
        self.run = [load_image("goblin_run1.png", colorkey=-1), load_image("goblin run2.png", colorkey=-1),
                    load_image("goblin run3.png", colorkey=-1), load_image("goblin run4.png", colorkey=-1),
                    load_image("goblin run5.png", colorkey=-1), load_image("goblin run6.png", colorkey=-1)]
        self.image = pygame.transform.scale(self.image, size_player)
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 510
        self.hero = hero
        self.left = False
        self.right = False


    def update(self):
        self.left = False
        self.right = False
        if level[(self.rect.y + 41) // 25][(self.rect.x + 15) // 30] == ".":
            self.rect.y += 1
        else:
            location_enemy = ((self.rect.y + 41) // 25, (self.rect.x + 15) // 30)
            location_hero = ((self.hero.rect.y + 41) // 25, (self.hero.rect.x + 15) // 30)
            try:
                move = navigation_data[location_enemy[0] - 1][location_enemy[1]][location_hero[0] - 1][location_hero[1]][0]
            except Exception:
                move = ""
            if move == "right":
                self.rect.x += 1
                self.right = True
            if move == "left":
                self.rect.x -= 1
                self.left = True
            if move == "up":
                self.rect.y -= 1
            if move == "down":
                self.rect.y += 1
            if self.animCount + 1 >= 30:
                self.animCount = 0
            if self.left:
                self.image = self.run[self.animCount // 5]
                self.image = pygame.transform.scale(self.image, size_player)
                self.image = pygame.transform.flip(self.image, True, False)
                self.animCount += 1
            elif self.right:
                self.image = self.run[self.animCount // 5]
                self.image = pygame.transform.scale(self.image, size_player)
                self.animCount += 1
            else:
                self.image = self.state
                self.image = pygame.transform.scale(self.image, size_player)

            for coin in coins_group:
                # Проверка расстояния между героем и монетой
                distance = pygame.math.Vector2(coin.rect.center).distance_to(pygame.math.Vector2(self.rect.center))
                if 0 < distance < 50:  # расстояние = 50 пикселей
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_g:
                            coins_group.remove(coin)
                            remove_coin_from_db(coin.x_db, coin.y_db)
                            #  увеличиваем счетчик собранных монет
                            global count_coin
                            count_coin += 1
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Wall(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)


class Ladder(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)


class Block(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('runner')
    size = width, height = 840, 600
    screen = pygame.display.set_mode(size)

    running = True
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 5000)

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    hero = Hero()
    all_sprites.add(hero)
    enemy = Enemy(hero=hero)
    all_sprites.add(enemy)

    tile_images = {
        'wall': load_image_data_tile('brick_2.png'),
        'ladder': load_image_data_tile('ladder.png'),
        'block': load_image_data_tile('block.png')
    }

    tile_width, tile_height = 30, 25

    title = True
    level = load_level('map.txt')
    navigation_data = navigation(level)
    level_x, level_y = generate_level(level)
    tiles_group.draw(screen)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print_collected_coins()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    check_coin_collection(hero)

        clock.tick(32)
        if not running:
            print_collected_coins()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.USEREVENT:
                all_sprites.add(Enemy(hero=hero))

        all_sprites.update()
        coins_group.update()
        pygame.display.flip()

        screen.fill((0, 0, 0))

        all_sprites.draw(screen)

        hero.draw_run()
        all_sprites.update()

        pygame.display.flip()

    pygame.quit()



