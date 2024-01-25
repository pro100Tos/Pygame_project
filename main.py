import pygame, os, sys
import random
import sqlite3
from copy import deepcopy


class ImageButtton:
    def __init__(self, x, y, width, height, text, image_path, hover_image_path=None, sound_path=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

        self.image = load_image(image_path, colorkey=-1)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.hover_image = self.image

        if hover_image_path:
            self.hover_image = load_image(hover_image_path, colorkey=-1)
            self.hover_image = pygame.transform.scale(self.hover_image, (width, height))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.sound = None

        if sound_path:
            self.sound = load_sound(sound_path)

        self.is_hovered = False

    def draw(self, screen):
        current_image = self.hover_image if self.is_hovered else self.image
        screen.blit(current_image, self.rect.topleft)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.sound:
                self.sound.play()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))


def show_buttons(buttons, screen):
    for button in buttons:
        button.check_hover(pygame.mouse.get_pos())
        button.draw(screen)


def work_buttons(buttons, event):
    for button in buttons:
        button.handle_event(event)


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

coins_group = pygame.sprite.Group()

count_coin = 0


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, coins_group)
        original_image = load_image("gift.jpg", colorkey=-1)
        self.image = pygame.transform.scale(original_image, (30, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_db = x // tile_width
        self.y_db = y // tile_height
        add_coin_to_db(self.x_db, self.y_db)
        self.collected = False


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


def delete_coin_data_in_db():
    conn = sqlite3.connect("coins.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM coins")
    conn.commit()
    conn.close()


def load_sound(name):
    fullname = os.path.join('sounds_data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с музыкой '{fullname}' не найден")
        sys.exit()
    sound = pygame.mixer.Sound(fullname)
    return sound


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
            elif level[y][x] == '!':
                level[y] = level[y][:x] + "." + level[y][x + 1:]
                cords_enemy.append((x, y))
            elif level[y][x] == '@':
                level[y] = level[y][:x] + "." + level[y][x + 1:]
                cords_hero.append((x, y))

    # Генерация случайных местоположений монет
    for _ in range(10):
        rand_x = random.randint(0, len(level[0]) - 1)
        rand_y = random.randint(1, len(level) - 2)
        while level[rand_y][rand_x] in "*#%" or level[rand_y + 1][rand_x] in '*.':
            rand_x = random.randint(0, len(level[0]) - 1)
            rand_y = random.randint(1, len(level) - 2)
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
                        if level_clone[y][x - 1] in tile_mas1 and (level_clone[y + 1][x - 1] in tile_mas2 \
                                or level_clone[y + 1][x] in tile_mas2):
                            active_mas.append((y, x - 1))
                            reserv_MFMD.append("left")
                            mas_for_main_data[y][x - 1] = reserv_MFMD[:]
                    reserv_MFMD = mas_for_main_data[y][x][:]
                    if x < m - 1:
                        if level_clone[y][x + 1] in tile_mas1 and (level_clone[y + 1][x + 1] in tile_mas2 \
                                or level_clone[y + 1][x] in tile_mas2):
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


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Wall(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.add(wall_group)


class Ladder(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.add(ladder_group)


class Block(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.add(wall_group)


def spritecollide_vertical(hero, sprite_group):
    global count_coin, level_points
    collide_list = pygame.sprite.spritecollide(hero, sprite_group, False)
    for sprite in collide_list:
        if sprite_group == coins_group and (hero.rect.y + 37) > sprite.rect.y:
            level_points += 1
            count_coin += 1
            sprite.kill()
            return True
        if (hero.rect.y + 37) > sprite.rect.y:
            return True


class Hero(pygame.sprite.Sprite):
    def __init__(self, *group, x, y):
        super().__init__(*group)
        self.course = "right"
        self.image = load_image("idle.png", colorkey=-1)
        self.animCount = 0
        self.state_r = load_image("idle.png", colorkey=-1)
        self.state_l = load_image("idle_left.png", colorkey=-1)
        self.rect = self.image.get_rect()
        self.rect.height = 41
        self.rect.x = x * 30
        self.rect.y = y * 24 - 2
        self.speed = 5
        self.run = [load_image("Push1.png", colorkey=-1), load_image("Push2.png", colorkey=-1),
                    load_image("Push3.png", colorkey=-1), load_image("Push4.png", colorkey=-1),
                    load_image("Push5.png", colorkey=-1), load_image("Push6.png", colorkey=-1),
                    load_image("Push7.png", colorkey=-1), load_image("Push8.png", colorkey=-1),
                    load_image("Push9.png", colorkey=-1), load_image("Push10.png", colorkey=-1),
                    load_image("Push11.png", colorkey=-1), load_image("Push12.png", colorkey=-1),
                    load_image("Push13.png", colorkey=-1), load_image("Push14.png", colorkey=-1),
                    load_image("Push15.png", colorkey=-1), load_image("Push16.png", colorkey=-1), ]
        self.left = False
        self.right = False

    def draw_run(self):
        global numbers_map, all_enemy
        key_pressed_is = pygame.key.get_pressed()
        self.left = False
        self.right = False
        flag_stack = True
        if level[(self.rect.y + 41) // 25][(self.rect.x + 15) // 30] == "." or \
                (not pygame.sprite.spritecollideany(self, tiles_group)):
            self.rect = self.rect.move(0, self.speed)
            flag_stack = False
        else:
            if pygame.sprite.spritecollideany(self, ladder_group):
                if key_pressed_is[pygame.K_UP] and level[(self.rect.y + 35) // 25][(self.rect.x + 15) // 30] == "*":
                    if (self.rect.y + 35) // 25 == 0 and level_points >= 10:
                        numbers_map += 1
                        if numbers_map == 3:
                            numbers_map = 0
                        for en in all_enemy:
                            en.kill()
                        all_enemy.clear()
                        start_game()
                    self.rect = self.rect.move(0, -self.speed)
                if key_pressed_is[pygame.K_DOWN] and level[(self.rect.y + 41) // 25][(self.rect.x + 15) // 30] == "*":
                    self.rect = self.rect.move(0, self.speed)
            if key_pressed_is[pygame.K_LEFT] and (self.rect.x + 15 - self.speed) // 30 > -1:
                self.rect = self.rect.move(-self.speed, 0)
                if spritecollide_vertical(self, wall_group):
                    self.rect = self.rect.move(self.speed, 0)
                self.left = True
                self.course = "left"
            if key_pressed_is[pygame.K_RIGHT] and (self.rect.x + 15 + self.speed) // 30 < len(level[0]):
                self.rect = self.rect.move(self.speed, 0)
                if spritecollide_vertical(self, wall_group):
                    self.rect = self.rect.move(-self.speed, 0)
                self.right = True
                self.course = "right"

            spritecollide_vertical(self, coins_group)

        if spritecollide_vertical(self, wall_group) and flag_stack:
            self.rect = self.rect.move(0, -self.speed)

    def crash_block(self):
        if pygame.sprite.spritecollideany(self, tiles_group):
            bottom_block = pygame.sprite.spritecollide(self, tiles_group, False)[0]
            if bottom_block not in wall_group:
                return
            remove_block = []
            if self.course == "right":
                remove_block = list(filter(lambda sprite: sprite.rect.x == (
                            bottom_block.rect.x + 30) and sprite.rect.y == bottom_block.rect.y, wall_group))
            elif self.course == "left":
                remove_block = list(filter(lambda sprite: sprite.rect.x == (
                            bottom_block.rect.x - 30) and sprite.rect.y == bottom_block.rect.y, wall_group))
            if not remove_block:
                return

            if str(remove_block[0].__class__) == "<class '__main__.Wall'>":
                remove_stack.append(remove_block)
                remove_block[0].kill()

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
            self.image = self.state_r if self.course == "right" else self.state_l
            self.image = pygame.transform.scale(self.image, size_player)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, *group, hero, x, y):
        super().__init__(*group)
        self.image = load_image("goblin_run1.png", colorkey=-1)
        self.animCount = 0
        self.state = load_image("goblin_run1.png", colorkey=-1)
        self.run = [load_image("goblin_run1.png", colorkey=-1), load_image("goblin run2.png", colorkey=-1),
                    load_image("goblin run3.png", colorkey=-1), load_image("goblin run4.png", colorkey=-1),
                    load_image("goblin run5.png", colorkey=-1), load_image("goblin run6.png", colorkey=-1)]
        self.image = pygame.transform.scale(self.image, size_player)
        self.rect = self.image.get_rect()
        self.rect.height = 41
        self.rect.x = x * 30
        self.rect.y = y * 24
        self.speed = 3
        self.hero = hero
        self.left = False
        self.right = False
        self.end = False

    def update(self):
        self.left = False
        self.right = False
        if not pygame.sprite.spritecollideany(self, tiles_group):
            self.rect = self.rect.move(0, self.speed)
        else:
            location_enemy = ((self.rect.y + 41) // 25, (self.rect.x + 15) // 30)
            location_hero = ((self.hero.rect.y + 41) // 25, (self.hero.rect.x + 15) // 30)
            try:
                move = \
                navigation_data[location_enemy[0] - 1][location_enemy[1]][location_hero[0] - 1][location_hero[1]][0]
            except Exception:
                move = ""
            if move == "right":
                self.rect = self.rect.move(self.speed, 0)
                if spritecollide_vertical(self, wall_group):
                    self.rect = self.rect.move(0, -self.speed)
                self.right = True
            if move == "left":
                self.rect = self.rect.move(-self.speed, 0)
                if spritecollide_vertical(self, wall_group):
                    self.rect = self.rect.move(0, -self.speed)
                self.left = True
            if move == "up":
                self.rect = self.rect.move(0, -self.speed)
            if move == "down":
                self.rect = self.rect.move(0, self.speed)
            if move == "" and spritecollide_vertical(self, wall_group):
                self.rect = self.rect.move(0, -self.speed)
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
        if pygame.sprite.spritecollideany(self, [self.hero]):
            self.end = True


def sounds_update():
    global main_sound, game_sound, sound_flag, sound_play_flag
    if sound_play_flag:
        if sound_flag:
            sound_flag = False
            main_sound.stop()
            game_sound.play(-1)
        else:
            sound_flag = True
            main_sound.play(-1)
            game_sound.stop()
    else:
        main_sound.stop()
        game_sound.stop()


def check_end(data):
    for enemy in data:
        if enemy.end:
            return True
    return False


def draw_text_for_help(text):
    count_s = 1
    for one_string in text.split("\n"):
        font = pygame.font.Font(None, 42)
        text_surface = font.render(one_string, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(width / 2, (count_s * 35) + 100))
        screen.blit(text_surface, text_rect)
        count_s += 1


def draw_text_for_results():
    count_s = 1
    for number in range(1, 6):
        font = pygame.font.Font(None, 42)
        text_surface = font.render(str(number) + ")", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(width / 2 - 200, (count_s * 35) + 135))
        screen.blit(text_surface, text_rect)
        count_s += 1


def add_new_results_to_db(new_points):
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    data = cursor.execute("SELECT * FROM results").fetchall()
    if len(data) < 5:
        cursor.execute("INSERT INTO results(points) VALUES (?)", (new_points,))
    else:
        min_points = 0
        min_id = 1
        for id, points in data:
            if min_id == id:
                min_points = points
            else:
                if min_points > points:
                    min_points = points
                    min_id = id
        if new_points > min_points:
            cursor.execute("UPDATE results SET points = (?) WHERE id == (?)", (new_points, min_id))
    conn.commit()
    conn.close()


def get_results():
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    data = sorted(list(map(lambda x: x[0], cursor.execute("SELECT points FROM results").fetchall())), reverse=-1)
    return data


def results_menu():
    running = True
    all_buttons = [back_button]
    text = "5 Лучших результатов:"
    for points in get_results():
        if points > 1 or points == 0:
            if points < 5 and points != 0:
                text += "\n" + "собранно " + str(points) + " подарка"
            else:
                text += "\n" + "собранно " + str(points) + " подарков"
        else:
            text += "\n" + "собран " + str(points) + " подарок"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.USEREVENT and event.button == back_button:
                main_menu()

            work_buttons(all_buttons, event)

        screen.fill((0, 0, 0))

        draw_text_for_results()
        draw_text_for_help(text)

        show_buttons(all_buttons, screen)

        pygame.display.flip()

    pygame.quit()


def main_menu():
    global count_coin, sound_play_flag, sound_flag
    running = True
    count_coin = 0
    all_buttons = [start_button, record_button, help_button, exit_button, music_button]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.USEREVENT and event.button == exit_button):
                terminate()

            if event.type == pygame.USEREVENT and event.button == start_button:
                start_game()

            if event.type == pygame.USEREVENT and event.button == help_button:
                help_menu()

            if event.type == pygame.USEREVENT and event.button == record_button:
                results_menu()

            if event.type == pygame.USEREVENT and event.button == music_button:
                sound_play_flag = not sound_play_flag
                sounds_update()

            work_buttons(all_buttons, event)

        screen.fill((0, 0, 0))

        show_buttons(all_buttons, screen)
        pygame.display.flip()

    pygame.quit()


def start_game():
    global count_coin, remove_stack, level_points, cords_hero, cords_enemy, all_enemy
    prepare_start_programm()
    if count_coin == 0:
        sounds_update()
    running = True

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

    coins_group = pygame.sprite.Group()

    for x, y in cords_hero:
        hero = Hero(x=x, y=y)
    all_sprites.add(hero)
    all_enemy = []
    for x, y in cords_enemy:
        enemy = Enemy(hero=hero, x=x, y=y)
        all_sprites.add(enemy)
        all_enemy.append(enemy)

    clock = pygame.time.Clock()
    FPS = 50
    MYEVENTTYPE = pygame.USEREVENT + 1
    pygame.time.set_timer(MYEVENTTYPE, 10000)

    while running:
        clock.tick(32)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if check_end(all_enemy):
                delete_coin_data_in_db()
                add_new_results_to_db(count_coin)
                for en in all_enemy:
                    en.kill()
                all_enemy.clear()
                hero.kill()
                game_over()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    hero.crash_block()

            if event.type == MYEVENTTYPE:
                if remove_stack:
                    return_sprite = remove_stack[0]
                    remove_stack = remove_stack[1:]
                    tiles_group.add(return_sprite)
                    wall_group.add(return_sprite)
                    all_sprites.add(return_sprite)
                    pygame.time.set_timer(MYEVENTTYPE, 0)
                    pygame.time.set_timer(MYEVENTTYPE, 10000)

        screen.fill((0, 0, 0))

        all_sprites.draw(screen)
        hero.draw_run()
        all_sprites.update()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def game_over():
    global count_coin
    sounds_update()
    running = True
    all_buttons = [back_button]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.USEREVENT and event.button == back_button:
                count_coin = 0
                main_menu()

            work_buttons(all_buttons, event)

        screen.fill((0, 0, 0))

        font = pygame.font.Font(None, 42)
        text_surface = font.render("К сожалению вас поймали гоблины, ваш счёт:", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(width / 2, 200))
        screen.blit(text_surface, text_rect)
        point_font = pygame.font.Font(None, 72)
        point_text_surface = point_font.render(str(count_coin), True, (255, 255, 255))
        point_text_rect = point_text_surface.get_rect(center=(width / 2, 270))
        screen.blit(point_text_surface, point_text_rect)

        show_buttons(all_buttons, screen)

        pygame.display.flip()

    pygame.quit()


def help_menu():
    running = True
    all_buttons = [back_button]
    with open("explanatory_note.txt", encoding="UTF-8") as file:
        text = file.read()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.USEREVENT and event.button == back_button:
                main_menu()

            work_buttons(all_buttons, event)

        screen.fill((0, 0, 0))

        draw_text_for_help(text)

        show_buttons(all_buttons, screen)

        pygame.display.flip()

    pygame.quit()


def prepare_start_programm():
    global all_sprites, tiles_group, wall_group, ladder_group, tile_images, tile_width, tile_height, title, level
    global navigation_data, level_x, level_y, remove_stack, game_maps, numbers_map, level_points
    global cords_hero, cords_enemy
    level_points = 0

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    wall_group = pygame.sprite.Group()
    ladder_group = pygame.sprite.Group()
    remove_stack = []
    cords_hero = []
    cords_enemy = []

    tile_images = {
        'wall': load_image_data_tile('brick_2.png'),
        'ladder': load_image_data_tile('ladder.png'),
        'block': load_image_data_tile('block.png')
    }

    tile_width, tile_height = 30, 25

    title = True
    level = load_level(game_maps[numbers_map])
    level_x, level_y = generate_level(level)
    navigation_data = navigation(level)
    tiles_group.draw(screen)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('runner')
    size = width, height = 840, 600
    screen = pygame.display.set_mode(size)
    start_button = ImageButtton(width / 2 - (300 / 2), 100, 300, 74, "Начать игру", "buttons1.png", "buttons2.png",
                                "button_sound.mp3")
    record_button = ImageButtton(width / 2 - (300 / 2), 200, 300, 74, "Рекорды", "buttons1.png", "buttons2.png",
                                 "button_sound.mp3")
    help_button = ImageButtton(width / 2 - (300 / 2), 300, 300, 74, "Помощь", "buttons1.png", "buttons2.png",
                               "button_sound.mp3")
    exit_button = ImageButtton(width / 2 - (300 / 2), 400, 300, 74, "Выход", "buttons1.png", "buttons2.png",
                                  "button_sound.mp3")
    back_button = ImageButtton(width / 2 - (300 / 2), 380, 300, 74, "В главное меню", "buttons1.png", "buttons2.png",
                               "button_sound.mp3")
    music_button = ImageButtton(700, 60, 100, 100, "", "music_button.png", "music_button2.png", "button_sound.mp3")
    main_sound = load_sound("zanzarah_sound.mp3")
    game_sound = load_sound("game_8bit_sound.mp3")
    game_maps = ["map.txt", "level_2.txt", "level_3.txt"]
    numbers_map = 0
    sound_flag = False
    sound_play_flag = True
    sounds_update()
    main_menu()