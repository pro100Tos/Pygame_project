import pygame, os, sys

size_player = p_width, p_height = 30, 40

def make_data(level):
    data_level = []
    for i in level:
        s = ""
        for j in i:
            s += 30 * j
        for j in range(26):
            data_level.append(s)
    return data_level

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
    return x, y


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

        if key_pressed_is[pygame.K_LEFT]:
            self.rect.x -= 3
            self.left = True
        if key_pressed_is[pygame.K_RIGHT]:
            self.rect.x += 3
            self.right = True
        if key_pressed_is[pygame.K_UP] and data_level[self.rect.y + 42][self.rect.x + 15] == "*":
            self.rect.y -= 3
        if key_pressed_is[pygame.K_DOWN] and data_level[self.rect.y + 52][self.rect.x + 15] == "*":
            self.rect.y += 3

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
        self.rect.x = 600
        self.rect.y = 400
        self.hero = hero
        self.left = False
        self.right = False

    def update(self):
        self.left = False
        self.right = False
        if self.hero.rect.x > self.rect.x:
            self.rect.x += 1
            self.right = True
        if self.hero.rect.x < self.rect.x:
            self.rect.x -= 1
            self.left = True
        if self.hero.rect.y > self.rect.y and data_level[self.rect.y + 52][self.rect.x + 15] == "*":
            self.rect.y += 1
        if self.hero.rect.y < self.rect.y and data_level[self.rect.y + 52][self.rect.x + 15] == "*":
            self.rect.y -= 1
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
    data_level = make_data(level)
    level_x, level_y = generate_level(level)
    tiles_group.draw(screen)

    while running:
        clock.tick(32)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.USEREVENT:
                all_sprites.add(Enemy(hero=hero))

        screen.fill((0, 0, 0))

        all_sprites.draw(screen)

        hero.draw_run()
        all_sprites.update()

        pygame.display.flip()

    pygame.quit()