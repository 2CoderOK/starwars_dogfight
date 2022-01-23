from random import randint

import pygame
from pygame.locals import K_DOWN, K_LEFT, K_RIGHT, K_SPACE, K_UP, RLEACCEL

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("images/fighter_xwing.png").convert_alpha()
        self.surf = pygame.transform.rotate(self.surf, -90)
        self.rect = self.surf.get_rect(center=(100, 250))
        self.speed = 10

    def update(self, keys):
        if keys[K_UP]:
            if self.rect.top > 0:
                self.rect.move_ip(0, -self.speed)
        elif keys[K_DOWN]:
            if self.rect.top < SCREEN_HEIGHT - 35:
                self.rect.move_ip(0, self.speed)
        elif keys[K_LEFT]:
            if self.rect.left > 0:
                self.rect.move_ip(-self.speed, 0)
        elif keys[K_RIGHT]:
            if self.rect.top < SCREEN_WIDTH:
                self.rect.move_ip(self.speed, 0)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("images/fighter_tie.png").convert_alpha()
        self.surf = pygame.transform.rotate(self.surf, -90)
        self.rect = self.surf.get_rect(center=(SCREEN_WIDTH + 50, randint(20, SCREEN_HEIGHT - 50)))
        self.speed = randint(5, 10)

    def update(self):
        if self.rect.right > 0:
            self.rect.move_ip(-self.speed, 0)
        else:
            self.kill()


class Fire(pygame.sprite.Sprite):
    def __init__(self, playerRect):
        super(Fire, self).__init__()
        self.surf = pygame.image.load("images/fire_1.png").convert_alpha()
        self.surf = pygame.transform.rotate(self.surf, -90)
        self.rect = self.surf.get_rect(center=(playerRect.left + 10, playerRect.top + 25))
        self.speed = 30

    def update(self):
        if self.rect.right < SCREEN_WIDTH + 50:
            self.rect.move_ip(self.speed, 0)
        else:
            self.kill()


class BGPlanet(pygame.sprite.Sprite):
    def __init__(self, img_path, dest, speed, resize):
        super(BGPlanet).__init__()
        self.surf = pygame.image.load(img_path).convert_alpha()
        self.surf = pygame.transform.scale(self.surf, (self.surf.get_width() + resize, self.surf.get_height() + resize))
        self.rect = self.surf.get_rect()
        self.rect.move_ip(dest.left, dest.top)
        self.speed = speed
        self.speed_counter = 0

    def update(self):
        self.speed_counter += self.speed
        if self.speed_counter >= 1:
            self.rect.move_ip(-1, 0)
            self.speed_counter = 0
        return True


class BGStar(pygame.sprite.Sprite):
    def __init__(self, dest, is_falling=False):
        super(BGStar).__init__()
        self.surf = pygame.image.load("images/star.png").convert_alpha()
        self.surf.set_alpha(0)
        self.rect = self.surf.get_rect()
        self.rect.move_ip(dest.left, dest.top)
        self.is_falling = is_falling
        self.alpha_dir = 0
        self.dir = pygame.Rect(dest.left + 100, dest.top + 100, 0, 0)

    def update(self):
        alpha = 7
        if self.alpha_dir:
            alpha = -7
            if self.surf.get_alpha() < 10:
                return False
        else:
            if self.surf.get_alpha() > 250:
                self.alpha_dir = 1

        self.surf.set_alpha(self.surf.get_alpha() + alpha)

        if self.is_falling:
            if self.rect.left < self.dir.left:
                self.rect.move_ip(-2, 1)
        return True


pygame.init()
FPS = 60
fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.SCALED + pygame.RESIZABLE)

ADDSTAR = pygame.USEREVENT + 1
ADDFALLINGSTAR = pygame.USEREVENT + 2
ADDENEMY = pygame.USEREVENT + 3
GAMEOVER = pygame.USEREVENT + 4

pygame.time.set_timer(ADDSTAR, 25)
pygame.time.set_timer(ADDFALLINGSTAR, 700)
pygame.time.set_timer(ADDENEMY, 1000)

pl = Player()

bg_space = pygame.image.load("images/space.png").convert()

death_star = BGPlanet("images/death_star.png", pygame.rect.Rect(150, 150, 0, 0), 0.05, 90)
planet_1 = BGPlanet("images/planet_1.png", pygame.rect.Rect(550, 90, 0, 0), 0.020, 20)
planet_2 = BGPlanet("images/planet_2.png", pygame.rect.Rect(750, 390, 0, 0), 0.007, -5)

bg_objects = []
bg_objects.append(death_star)
bg_objects.append(planet_1)
bg_objects.append(planet_2)

enemies = pygame.sprite.Group()
fires = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
all_sprites.add(pl)

my_score = 0
myfont = pygame.font.SysFont("Comic Sans MS", 10)
font_texture = myfont.render(f"SCORE: {my_score}", False, (255, 40, 45))

fire_sound = pygame.mixer.Sound("sound/fire.mp3")
fire_sound.set_volume(0.4)
hit_sound = pygame.mixer.Sound("sound/hit.mp3")
fire_sound.set_volume(0.3)
music = pygame.mixer.Sound("sound/music.mp3")
music.set_volume(0.4)
music.play(-1)

running = True
update_game = True
while running:

    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                f = Fire(pl.rect)
                fires.add(f)
                all_sprites.add(f)
                fire_sound.play()

        elif e.type == ADDSTAR or e.type == ADDFALLINGSTAR:
            is_falling = False
            if e.type == ADDFALLINGSTAR:
                is_falling = True
            s = BGStar(pygame.Rect(randint(10, SCREEN_WIDTH - 10), randint(10, SCREEN_HEIGHT - 10), 0, 0), is_falling)
            bg_objects.append(s)
        elif e.type == ADDENEMY:
            en = Enemy()
            enemies.add(en)
            all_sprites.add(en)
        elif e.type == pygame.QUIT or e.type == GAMEOVER:
            running = False

    if update_game:
        screen.blit(bg_space, (0, 0))

        for o in bg_objects:
            if o.update():
                screen.blit(o.surf, o.rect)
            else:
                bg_objects.remove(o)

        for f in fires:
            f.update()
            en = pygame.sprite.spritecollideany(f, enemies)
            if en:
                en.kill()
                f.kill()
                my_score += 100
                font_texture = myfont.render(f"SCORE: {my_score}", False, (255, 40, 45))
                hit_sound.play()

        pl.update(pygame.key.get_pressed())
        enemies.update()

        if pygame.sprite.spritecollideany(pl, enemies):
            update_game = False
            pygame.time.set_timer(GAMEOVER, 1000)
            music.stop()
            hit_sound.play()

        for s in all_sprites:
            screen.blit(s.surf, s.rect)

        screen.blit(font_texture, (10, 10))
        pygame.display.flip()
    fpsClock.tick(FPS)
pygame.quit()
