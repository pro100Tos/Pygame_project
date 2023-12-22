import pygame, os, sys


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


class Hero(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = load_image("idle.gif", colorkey=-1)
        self.rect = self.image.get_rect()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, *group, hero):
        super().__init__(*group)
        self.image = load_image("goblin_run1.png", colorkey=-1)
        self.image = pygame.transform.scale(self.image, (40, 50))
        self.rect = self.image.get_rect()
        self.rect.x = 600
        self.rect.y = 600
        self.hero = hero

    def update(self):
        if self.hero.rect.x > self.rect.x:
            self.rect.x += 5
        if self.hero.rect.x < self.rect.x:
            self.rect.x -= 5
        if self.hero.rect.y > self.rect.y:
            self.rect.y += 5
        if self.hero.rect.y < self.rect.y:
            self.rect.y -= 5


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('runner')
    size = width, height = 1200, 800
    screen = pygame.display.set_mode(size)

    running = True
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 5000)

    all_sprites = pygame.sprite.Group()
    hero = Hero()
    all_sprites.add(hero)
    enemy = Enemy(hero=hero)
    all_sprites.add(enemy)

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.USEREVENT:
                all_sprites.add(Enemy(hero=hero))

        key_pressed_is = pygame.key.get_pressed()

        if key_pressed_is[pygame.K_LEFT]:
            hero.rect.x -= 10
        if key_pressed_is[pygame.K_RIGHT]:
            hero.rect.x += 10
        if key_pressed_is[pygame.K_UP]:
            hero.rect.y -= 10
        if key_pressed_is[pygame.K_DOWN]:
            hero.rect.y += 10

        screen.fill((0, 0, 0))

        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()
    pygame.quit()