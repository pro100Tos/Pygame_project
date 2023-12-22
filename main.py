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
        self.image = load_image("idle.png", colorkey=-1)
        self.animCount = 0
        self.state = load_image("idle.png", colorkey=-1)
        self.rect = self.image.get_rect()
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
            self.rect.x -= 5
            self.left = True
        if key_pressed_is[pygame.K_RIGHT]:
            self.rect.x += 5
            self.right = True
        if key_pressed_is[pygame.K_UP]:
            self.rect.y -= 5
        if key_pressed_is[pygame.K_DOWN]:
            self.rect.y += 5

    def update(self):
        if self.animCount + 1 >= 32:
            self.animCount = 0
        if self.left:
            self.image = self.run[self.animCount // 2]
            self.image = pygame.transform.scale(self.image, (60, 70))
            self.image = pygame.transform.flip(self.image, True, False)
            self.animCount += 1
        elif self.right:
            self.image = self.run[self.animCount // 2]
            self.image = pygame.transform.scale(self.image, (60, 70))
            self.animCount += 1
        else:
            self.image = self.state
            self.image = pygame.transform.scale(self.image, (60, 70))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, *group, hero):
        super().__init__(*group)
        self.image = load_image("goblin_run1.png", colorkey=-1)
        self.animCount = 0
        self.state = load_image("goblin_run1.png", colorkey=-1)
        self.run = [load_image("goblin_run1.png", colorkey=-1), load_image("goblin run2.png", colorkey=-1),
                    load_image("goblin run3.png", colorkey=-1), load_image("goblin run4.png", colorkey=-1),
                    load_image("goblin run5.png", colorkey=-1), load_image("goblin run6.png", colorkey=-1)]
        self.image = pygame.transform.scale(self.image, (60, 70))
        self.rect = self.image.get_rect()
        self.rect.x = 600
        self.rect.y = 600
        self.hero = hero
        self.left = False
        self.right = False

    def update(self):
        self.left = False
        self.right = False
        if self.hero.rect.x > self.rect.x:
            self.rect.x += 2
            self.right = True
        if self.hero.rect.x < self.rect.x:
            self.rect.x -= 2
            self.left = True
        if self.hero.rect.y > self.rect.y:
            self.rect.y += 2
        if self.hero.rect.y < self.rect.y:
            self.rect.y -= 2
        if self.animCount + 1 >= 30:
            self.animCount = 0
        if self.left:
            self.image = self.run[self.animCount // 5]
            self.image = pygame.transform.scale(self.image, (60, 70))
            self.image = pygame.transform.flip(self.image, True, False)
            self.animCount += 1
        elif self.right:
            self.image = self.run[self.animCount // 5]
            self.image = pygame.transform.scale(self.image, (60, 70))
            self.animCount += 1
        else:
            self.image = self.state
            self.image = pygame.transform.scale(self.image, (60, 70))


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
        clock.tick(32)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.USEREVENT:
                all_sprites.add(Enemy(hero=hero))

        screen.fill((0, 0, 0))

        all_sprites.draw(screen)

        hero.draw_run()
        all_sprites.update()

        pygame.display.flip()

    pygame.quit()