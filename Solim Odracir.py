#-*- coding: utf-8 -*-
# Created by YegorMaratInc
# Solim Odracir

import pygame
import sys
import os
import random
import time

pygame.init()

size = width, height = 800, 600
screen = pygame.display.set_mode(size)
screen.fill((0, 191, 255))
pygame.display.set_caption("Solim Odracir")

pygame.display.flip()
# Фунцкии

# Загрузка изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image

# Конец игры
def terminate():
    pygame.quit()
    sys.exit(0)
    
# Начальный экран
def start_screen():
    intro_text = ["Solim Odracir:", "", "Magic Runes"]
 
    wallpaper = pygame.transform.scale(load_image('zastavka.png'), (width, height))
    screen.blit(wallpaper, (0, 0))
    font = pygame.font.Font(None, 60)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        
# Загрузка левела
def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
 
    # и подсчитываем максимальную длину    
    max_width = max(map(len, level_map))
 
    # дополняем каждую строку пустыми клетками ('.')    
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))   

# Создание левела
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'g':
                Tile(x, y)   
            if level[y][x] == 'b':
                Tile(x, y)            
                """
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                """
            if level[y][x] == '@':
                new_player = Player(x, y)           
    return new_player, x, y

# Классы и спрайты

# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullet_sprite = pygame.sprite.Group()

#Классы    
class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
 
    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
 
    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, radius, x, y):
        super().__init__(all_sprites)
        self.radius = radius
        self.add(bullet_sprite)
        self.image = pygame.Surface((2 * radius, 2 * radius))
        self.image.fill((255, 0, 0)) 
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)

    def update(self):
        self.rect.y += 3
        
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = pygame.Surface((50,50))
        self.image.fill((255, 0, 0))        
        self.rect = pygame.Rect(50 * pos_x, 50 * pos_y, 50, 50)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = pygame.Surface((46,65))
        self.image.fill((0, 0, 0))
        self.rect = pygame.Rect(46 * pos_x, 65 * pos_y, 46, 65) 
        self.on_ground = True
        
    def pravo(self):
        self.rect.x += 7
        
    def levo(self):
        self.rect.x -= 7   
        
    def jump(self):
        if  pygame.sprite.spritecollideany(self, tiles_group):
            self.rect.y -= 120
            
    def update(self):
        if not pygame.sprite.spritecollideany(self, tiles_group):
            self.rect.y += 5
    
    def shoot(self):
        b = Bullet(self.rect.x, self.rect.y, 100)
        
            
lvl = load_level('obuchenie.txt')
mapp = generate_level(lvl)
player = mapp[0]
camera = Camera()   

FPS = 60
stsc = True
on_ground = True
clock = pygame.time.Clock()
running = True
while running:
    if stsc == True:
        start_screen()
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False     
            
    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
        stsc = False    
        
    if event.type == pygame.KEYDOWN:     

        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
            player.levo()
            pygame.display.update() 
                    
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            player.pravo()
            pygame.display.update()
            
        if event.key == pygame.K_UP or event.key == pygame.K_SPACE or event.key == pygame.K_w:
            player.jump()
            pygame.display.update()
        
        if event.key == pygame.K_f:
            player.shoot()
            pygame.display.update()   
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.levo()
        if keys[pygame.K_UP]:
            player.jump()
        if keys[pygame.K_RIGHT]:
            player.pravo()


    screen.fill((0, 191, 255))
     
    tiles_group.draw(screen)
    player_group.draw(screen)
    all_sprites.update()    
    camera.update(player)
    
    for sprite in all_sprites:
        camera.apply(sprite)    
    
    clock.tick(FPS)
    pygame.display.update()    
     
pygame.quit()