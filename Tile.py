import os
import sys

import pygame

if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    size = WIDTH, HEIGHT = 840, 600
    screen = pygame.display.set_mode(size)
    FPS = 50
    player = None
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()


    def load_image(name, colorkey=None):
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


    tile_images = {
        'wall': load_image('brick_2.png'),
        'ladder': load_image('ladder.png'),
        'block': load_image('block.png')
    }

    tile_width, tile_height = 30, 25


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

    title = True
    level_x, level_y = generate_level(load_level('map.txt'))
    tiles_group.draw(screen)
    all_sprites.draw(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        pygame.display.flip()
        clock.tick(FPS)
