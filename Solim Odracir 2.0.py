#-*- coding: utf-8 -*-
# Created by YegorMaratInc
# Solim Odracir

import pygame
import pyganim
import sys
import os
import random
import time

pygame.init()

#Создание окна
size = width, height = 800, 600
screen = pygame.display.set_mode(size)
screen.fill((0, 191, 255))
pygame.display.set_caption("Solim Odracir")
anim_delay = 0.1
plat = []

pygame.display.flip()

#Музыка
pygame.mixer.music.load('music.wav')
pygame.mixer.music.play()

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
    intro_text = []
 
    wallpaper = pygame.transform.scale(load_image('startscreen.png'), (width, height))
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
                g = Tile(x, y, 'ground')
                plat.append(g)
            if level[y][x] == 'w':
                w = Tile(x, y, 'ground_without_grass')
                plat.append(w)
            if level[y][x] == 'b':
                b = Tile(x, y, 'brick')
                plat.append(b)
            if level[y][x] == 'i':
                i = Tile(x, y, 'invisible')
                plat.append(i)
            if level[y][x] == 'c':
                c = Coin(x, y)            
            if level[y][x] == 's':
                s = Spike(x, y)  
            if level[y][x] == 'e':
                e = Skelet(x, y, plat)
            if level[y][x] == 'f':
                f = Winblock(x, y)                
            if level[y][x] == '@':
                player = Player(x, y, plat)           
    return player, x, y

# Классы и спрайты

# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullet_sprite = pygame.sprite.Group()
mobs_sprite = pygame.sprite.Group()
deadly_sprite = pygame.sprite.Group()
money_sprite = pygame.sprite.Group()
win_sprite = pygame.sprite.Group()

#Изображения
tile_images = {
    'brick': load_image('brick.png'),
    'ground_without_grass': load_image('ground2.png'),
    'invisible': load_image('invisible.png'),
    'ground': load_image('ground.png')
}

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
#Блоки        
class Tile(pygame.sprite.Sprite):
    
    def __init__(self, pos_x, pos_y, image):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[image]        
        self.rect = pygame.Rect(50 * pos_x, 50 * pos_y, 50, 50)
#Победный блок
class Winblock(pygame.sprite.Sprite):
    
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, win_sprite)
        self.image = load_image('flag.png')   
        self.rect = pygame.Rect(50 * pos_x, 50 * pos_y, 50, 50)
        self.add(all_sprites) 
        self.add(win_sprite)        
        
#Константы
SPEED = 7
JUMP = 8
GRAVITY = 4

#Персонаж
class Player(pygame.sprite.Sprite):
    
    def __init__(self, pos_x, pos_y, plat):
        super().__init__(player_group, all_sprites)
        self.startx = pos_x
        self.starty = pos_y     
        #Анимация
        #Право
        walkRight = [(load_image('walk/walk_right_1.png'), anim_delay),
                     (load_image('walk/walk_right_2.png'), anim_delay),
                     (load_image('walk/walk_right_3.png'), anim_delay),
                     (load_image('walk/walk_right_4.png'), anim_delay),
                     (load_image('walk/walk_right_5.png'), anim_delay),
                     (load_image('walk/walk_right_6.png'), anim_delay)]
        self.animation_right = pyganim.PygAnimation(walkRight)
        self.animation_right.play()
        #Лево
        walkLeft = [(load_image('walk/walk_left_1.png'), anim_delay),
                     (load_image('walk/walk_left_2.png'), anim_delay),
                     (load_image('walk/walk_left_3.png'), anim_delay),
                     (load_image('walk/walk_left_4.png'), anim_delay),
                     (load_image('walk/walk_left_5.png'), anim_delay),
                     (load_image('walk/walk_left_6.png'), anim_delay)]
        self.animation_left = pyganim.PygAnimation(walkLeft)
        self.animation_left.play()  
        #Прыжок право
        jumpRight = [(load_image('jump/jump_right_1.png'), anim_delay),
                     (load_image('jump/jump_right_2.png'), anim_delay),
                     (load_image('jump/jump_right_3.png'), anim_delay),
                     (load_image('jump/jump_right_4.png'), anim_delay),
                     (load_image('jump/jump_right_5.png'), anim_delay)]
        self.animation_right_jump = pyganim.PygAnimation(jumpRight)
        self.animation_right_jump.play()        
        #Прыжок лево
        jumpLeft = [(load_image('jump/jump_left_1.png'), anim_delay),
                     (load_image('jump/jump_left_2.png'), anim_delay),
                     (load_image('jump/jump_left_3.png'), anim_delay),
                     (load_image('jump/jump_left_4.png'), anim_delay),
                     (load_image('jump/jump_left_5.png'), anim_delay)]
        self.animation_left_jump = pyganim.PygAnimation(jumpLeft)
        self.animation_left_jump.play()        
        #
        self.image = load_image('walk/walk_right_1.png')
        self.rect = pygame.Rect(53 * pos_x, 66 * pos_y, 53, 66) 
        self.on_ground = True
        self.lifes = 3
        self.score = 0
        self.gostay = True
        self.goright = False
        self.goleft = False
        self.gotop = False
        self.gobottom = False
        self.watchright = True
        self.watchleft = False
        self.up = False
        self.lvlgo = 1
        self.winner = False
        
        
    def pravo(self):
        self.rect.x += SPEED
        self.image = pygame.Surface([53,66], pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.animation_right.blit(self.image, (0, 0))
        self.goright = True
        self.goleft = False
        self.gostay = False
        self.gotop = False
        self.gobottom = False        
        self.watchright = True
        self.watchleft = False        
        
    def levo(self):
        self.rect.x -= SPEED   
        self.image = pygame.Surface([53,66], pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.animation_left.blit(self.image, (0, 0))   
        self.goright = False
        self.goleft = True   
        self.gostay = False
        self.gotop = False
        self.gobottom = False        
        self.watchright = True
        self.watchleft = False
        self.watchright = False
        self.watchleft = True        
        
    def stay(self):
        if self.goright:
            self.image = load_image('walk/walk_right_1.png')
        if self.goleft:
            self.image = load_image('walk/walk_left_1.png')   
        self.gostay = True
        self.goright = False
        self.goleft = False
        self.gotop = False
        self.gobottom = False  
        
    def jump(self):
        if self.on_ground:
            for i in range(20): 
                self.rect.y -= JUMP
                if self.gotop or self.gobottom:
                    self.collide(False, True, plat)    
                if self.goright:
                    self.image = pygame.Surface([53,66], pygame.SRCALPHA, 32)
                    self.image = self.image.convert_alpha()
                    self.animation_right_jump.blit(self.image, (0, 0))                 
                if self.goleft:
                    self.image = pygame.Surface([53,66], pygame.SRCALPHA, 32)
                    self.image = self.image.convert_alpha()
                    self.animation_left_jump.blit(self.image, (0, 0))                
                pygame.display.update()
                pygame.display.flip()
            self.on_ground = False
            if self.goright:
                self.image = pygame.Surface([53,66], pygame.SRCALPHA, 32)
                self.image = self.image.convert_alpha()
                self.animation_right_jump.blit(self.image, (0, 0))                 
            if self.goleft:
                self.image = pygame.Surface([53,66], pygame.SRCALPHA, 32)
                self.image = self.image.convert_alpha()
                self.animation_left_jump.blit(self.image, (0, 0))   
        self.gotop = True
        self.gobottom = False
        self.gostay = False
        self.goright = False

    def dead(self):
        self.lifes -= 1
        if self.lifes < 0 :
            self.restart()
        self.teleporting(self.startx, self.starty)
    
    def money(self):
        self.score += 50
        if self.score == 250:
            self.score = 0
            self.lifes += 1
        
    def restart(self):
        pass

    def teleporting(self, goX, goY):
        self.rect.x = goX
        self.rect.y = goY
        
    def update(self):
        if self.goright or self.goleft:    
            self.collide(True, False, plat)
            
        self.gobottom = True
        self.rect.y += GRAVITY
        
        if self.gotop or self.gobottom:
            self.collide(False, True, plat)
            
    def notice(self):
        try:
            #Отрисовка кол-во сердечек и монет
            shrift = pygame.font.Font(None, 100)
            text = shrift.render(str(self.lifes), 1, (255, 0, 0))
            screen.blit(text, (50, 0))
        
            shrift = pygame.font.Font(None, 100)
            text = shrift.render(str('Score:'), 1, (255, 255, 0))
            screen.blit(text, (100, 0)) 
        
            shrift = pygame.font.Font(None, 100)
            text = shrift.render(str(self.score), 1, (255, 255, 0))
            screen.blit(text, (320, 0)) 
            #     
        except Exception:
            sys.exit(0)
    
    def shoot(self):
        b = Bullet(self.rect.x, self.rect.y, self.watchright, self.watchleft)
    
    def win(self):
        pygame.mixer.music.pause()
        self.winner = True
    
    def collide(self, gox, goy, plat):
        if pygame.sprite.spritecollideany(self, deadly_sprite):
            self.dead()
        
        if pygame.sprite.spritecollide(self, money_sprite, True):
            self.money()
        
        if pygame.sprite.spritecollide(self, win_sprite, True):
            self.lvlgo += 1
            print(self.lvlgo)    
            
        for p in plat:
            if pygame.sprite.collide_rect(self, p):
                
                if self.goright and gox:
                    self.rect.right = p.rect.left
                
                if self.goleft and gox:
                    self.rect.left = p.rect.right
                    
                if self.gobottom and goy:
                    self.rect.bottom = p.rect.top
                    self.on_ground = True
                    self.gobottom = False
    
                if self.gotop and goy:
                    self.rect.top = p.rect.bottom
                    self.top = False
                    
       
#Пуля
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, watchright, watchleft):
        super().__init__(all_sprites)
        self.add(bullet_sprite)
        self.add(all_sprites)
        self.goright = watchright
        self.goleft = watchleft         
        self.image = load_image('bullet_black.png')
        if self.goleft:
            self.rect = self.image.get_rect().move(pos_x - 5, pos_y + 25)
        if self.goright:
            self.rect = self.image.get_rect().move(pos_x + 45, pos_y + 25)            

    def update(self):
        if self.goleft:
            self.rect.x -= 15
        if self.goright:
            self.rect.x += 15
        if  pygame.sprite.spritecollideany(self, tiles_group):
            self.kill()
#Жизни
class Life(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)   
        self.image = load_image("heart.png")
        self.rect = self.image.get_rect()
        
    def paste(self):
        screen.blit(self.image, (0, 0))     
#Монеты
class Coin(pygame.sprite.Sprite):  
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, money_sprite)   
        self.image = load_image("coin.png")
        self.image_2 = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image_2.get_rect().move(50 * pos_x, 50 * pos_y)
        self.add(all_sprites)        
        self.add(money_sprite)  
#Шипы                
class Spike(pygame.sprite.Sprite):

    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)        
        self.image = load_image("spike.png")
        self.rect = self.image.get_rect().move(50 * pos_x, 50 * pos_y)
        self.add(all_sprites) 
        self.add(deadly_sprite)
        
#Константы скелет
SKELET_SPEED = 3

#Скелет
class Skelet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, plat):
        super().__init__(all_sprites, mobs_sprite) 
        self.add(all_sprites) 
        self.add(mobs_sprite)
        
        self.image = load_image("skelet\walk\skeleton_right_1.png")
        self.rect = self.image.get_rect().move(50 * pos_x, 50 * pos_y)
        #Анимация
        #Право
        SkeletwalkRight = [(load_image('skelet/walk/skeleton_right_1.png'), anim_delay),
                     (load_image('skelet/walk/skeleton_right_2.png'), anim_delay),
                     (load_image('skelet/walk/skeleton_right_3.png'), anim_delay)]
        self.animation_right = pyganim.PygAnimation(SkeletwalkRight)
        self.animation_right.play()
        #Лево
        SkeletwalkLeft = [(load_image('skelet/walk/skeleton_left_1.png'), anim_delay),
                     (load_image('skelet/walk/skeleton_left_2.png'), anim_delay),
                     (load_image('skelet/walk/skeleton_left_3.png'), anim_delay)]
        self.animation_left = pyganim.PygAnimation(SkeletwalkLeft)
        self.animation_left.play()
        #Смерть лево
        SkeletdeadLeft = load_image('skelet/death/dead_left_2.png') 
        #Смерть право
        SkeletdeathRight = load_image('skelet/death/dead_right_2.png')  
        #
        self.speed = SKELET_SPEED
        self.plat = plat
        
    def update(self):
        self.rect.x += self.speed
        self.collide(self.plat)
        if self.speed > 0:
            self.image = pygame.Surface([53,66], pygame.SRCALPHA, 32)
            self.image = self.image.convert_alpha()
            self.animation_right.blit(self.image, (0, 0)) 
            
        if self.speed < 0:       
            self.image = pygame.Surface([53,66], pygame.SRCALPHA, 32)
            self.image = self.image.convert_alpha()
            self.animation_left.blit(self.image, (0, 0))        
            
    def collide(self, plat):
        if pygame.sprite.spritecollide(self, bullet_sprite, True):
            self.kill()
            
        if pygame.sprite.spritecollideany(self, player_group):
            player.dead()        
            
        for p in plat:
            if pygame.sprite.collide_rect(self, p):
                self.speed *=  -1  
#Мегафон                     
class Megafon(pygame.sprite.Sprite):
 
    def __init__(self):
        super().__init__()        
        self.image1 = load_image("mikrofon.png")
        self.image2 = load_image("mikrofon_off.png")
        self.image = self.image1
        self.rect = self.image.get_rect()
        self.flswitch = True
        
    def paste(self):
        screen.blit(self.image, (750, 0))
        
    def switch(self):
        if self.flswitch:
            pygame.mixer.music.pause()
            self.image = self.image2
            self.flswitch = False
        else:
            pygame.mixer.music.unpause()
            self.image = self.image1
            self.flswitch = True
#Стартовый экран
startscreenbefore = (load_image('startscreen.png'))    
startscreen = pygame.transform.scale(startscreenbefore, (800, 600))
screen.blit(startscreen, (0, 0))
pygame.display.update()  
# Очищение экрана
def clear_screen():
    all_sprites.empty()
    tiles_group.empty()
    player_group.empty()
    bullet_sprite.empty()
    mobs_sprite.empty()
    deadly_sprite.empty()
    money_sprite.empty()
    win_sprite.empty()
    screen.fill((0, 191, 255))
    
#Создание лвл    
lvl = load_level('1_lvl.txt')
mapp = generate_level(lvl)
player = mapp[0]
print(mapp[0])
camera = Camera() 
meg = Megafon()
clock = pygame.time.Clock()
life = Life()
backgroundbefore = (load_image('background_1_lvl.png'))    
background = pygame.transform.scale(backgroundbefore, (800, 600))
screen.blit(background, (0, 0))
pygame.display.update()   

#Основные значения
FPS = 60
lvlfl = 2
on_ground = True
running = True
stscgo = True
while running:
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False     
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            stscgo = False
            if event.button == 1:
                if (event.pos[0] > 750 and event.pos[0] < 800) and (event.pos[1] > 0 and event.pos[1] < 50):
                    meg.switch()
            pygame.display.update()            
        
        if event.type == pygame.KEYDOWN:
            stscgo = False
            if event.key == pygame.K_z:
                player.shoot()
                pygame.display.update()              
                           
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.levo()
    elif keys[pygame.K_RIGHT]:
        player.pravo()
    elif keys[pygame.K_UP]:
        player.jump()           
    else:
        player.stay()
    pygame.display.update()
            
    screen.fill((0, 191, 255))
    
    screen.blit(background, (0, 0))
     
    tiles_group.draw(screen)
    all_sprites.update()
    all_sprites.draw(screen)
    player_group.draw(screen)
    camera.update(player)
    
    for sprite in all_sprites:
        camera.apply(sprite)    
    
        
    #Вывод на экран
    meg.paste()
    life.paste()
    player.notice()
    clock.tick(FPS)
    #Левел 2
    if player.lvlgo == 2 and lvlfl == 2:
        clear_screen()
        lvl = load_level('2_lvllox.txt')
        mapp = generate_level(lvl)
        player = mapp[0]
        backgroundbefore = (load_image('background_2_lvl.png'))    
        background = pygame.transform.scale(backgroundbefore, (800, 600))
        screen.blit(background, (0, 0))        
        camera = Camera() 
        meg = Megafon()
        clock = pygame.time.Clock()
        life = Life()
        pygame.display.update()        
        lvlfl += 1
    #Победа
    if player.lvlgo == 3 and lvlfl == 3:
        clear_screen()
        win_jpg = (load_image('win.jpg'))    
        win_jpg2 = pygame.transform.scale(win_jpg, (800, 600))
        screen.blit(win_jpg2, (0, 0))
        pygame.display.update()    
        
    #Стартовый экран 
    if stscgo == True:
        screen.blit(startscreen, (0, 0))
        
    pygame.display.update()     
pygame.quit()