# Copyright 2022 Ryan Stutsman.
# Available under the terms of the MIT license.

import sys
import pygame
import random
import time
import os.path

size = width, height = 1024, 600
speed = [0, 0]
black = 0, 0, 0

gravity = 5
max_fall = 15
jump_power = 8
jumping = 0
run_speed = 10

facing = 0
moving_left = False
moving_right = False

shooting = False

SKY = 0
GRASS = 1
WATER = 2

COLS = 21 
ROWS = 12

TILE_HEIGHT = 50
TILE_WIDTH = 50

MUSIC = True

class Tile:
    def __init__(self, filenames, typ):
        self.surfaces = [pygame.image.load('images/%s' % filename)
                            for filename in filenames]
        self.typ = typ
        self.rect = self.surfaces[0].get_rect()
        self.rect.width = TILE_WIDTH
        self.rect.height = TILE_HEIGHT
        for i in range(len(self.surfaces)):
            self.surfaces[i] = pygame.transform.scale(self.surfaces[i],
                                                  (self.rect.width, self.rect.height))
        self.is_solid = False
        if self.typ == GRASS:
            self.is_solid = True
        self.state = 0

    def draw(self, surface, x, y):
        self.rect.left = x * TILE_WIDTH
        self.rect.top = y * TILE_HEIGHT
        self.rect.width = TILE_WIDTH
        self.rect.height = TILE_HEIGHT
        surface.blit(self.surfaces[self.state], self.rect)

    def tick(self):
        self.state += 1
        if self.state >= len(self.surfaces):
            self.state = 0

class Monster:
    def __init__(self, filenames):
        paths = [os.path.join('images', filename) for filename in filenames]
        self.surfaces = [pygame.image.load(path) for path in paths]
        self.rect = self.surfaces[0].get_rect()
        #self.rect.width = TILE_WIDTH
        #self.rect.height = TILE_HEIGHT
        #for i in range(len(self.surfaces)):
        #    self.surfaces[i] = pygame.transform.scale(self.surfaces[i],
        #                                          (self.rect.width, self.rect.height))
        #self.is_solid = False
        #if self.typ == GRASS:
        #    self.is_solid = True
        self.state = 0

    def draw(self, surface, x, y):
        self.rect.left = x * TILE_WIDTH
        self.rect.top = y * TILE_HEIGHT
        self.rect.width = TILE_WIDTH
        self.rect.height = TILE_HEIGHT
        surface.blit(self.surfaces[self.state], self.rect)

tiles = [ Tile(['sky.png'], SKY),
          Tile(['grass.png'], GRASS),
          Tile(['water0.png', 'water1.png'], WATER)
        ]

class Map:
    def __init__(self):
        self.tiles = [ [ tiles[SKY] for y in range(ROWS) ] for x in range(COLS) ]
        for x in range(COLS):
            self.tiles[x][ROWS-1] = tiles[GRASS]
        self.tiles[10][5] = tiles[GRASS]
        self.tiles[11][5] = tiles[GRASS]
        self.tiles[12][6] = tiles[GRASS]
        self.tiles[13][6] = tiles[GRASS]
        self.tiles[2][3] = tiles[GRASS]
        self.tiles[3][3] = tiles[GRASS]
        self.tiles[11][11] = tiles[WATER]
        self.tiles[12][11] = tiles[WATER]
        self.tiles[13][11] = tiles[WATER]
        self.tiles[14][11] = tiles[WATER]

    def draw(self, surface):
        for y in range(ROWS):
            for x in range(COLS):
                self.tiles[x][y].draw(surface, x, y)

    def is_solid(self, x, y):
        x = int(x)
        y = int(y)
        if x >= COLS or x < 0:
            return True
        if y >= ROWS or y < 0:
            return True
        return self.tiles[x][y].is_solid

    def tick(self):
        for y in range(ROWS):
            for x in range(COLS):
                self.tiles[x][y].tick()

def main():
    player = Monster(['dragon.png'])

    global facing
    global jumping
    global moving_left
    global moving_right
    global shooting

    pygame.init()

    if MUSIC:
        music = pygame.mixer.music.load(os.path.join('music', 'main-theme.ogg'))
        pygame.mixer.music.play(loops=-1)

    mp = Map()

    screen = pygame.display.set_mode(size)

    player = pygame.image.load(os.path.join('images', 'dragon.png'))
    playerrect = player.get_rect()
    playerrect.width = 150
    playerrect.height = 125
    playerrect.bottom = height - (TILE_HEIGHT * 2)
    player = pygame.transform.scale(player, (playerrect.width, playerrect.height))

    fire = pygame.image.load(os.path.join('images', 'fire.png'))
    firerect = fire.get_rect()
    firerect.width = 100
    firerect.height = 35
    fire = pygame.transform.scale(fire, (firerect.width, firerect.height))
    fire.set_alpha(0x80)

    while True:
        time.sleep(0.03)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    jumping = True
                elif event.key == pygame.K_LEFT:
                    moving_left = True
                    moving_right = False
                elif event.key == pygame.K_RIGHT:
                    moving_left = False
                    moving_right = True
                elif event.key == pygame.K_SPACE:
                    shooting = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    jumping = False
                elif event.key == pygame.K_LEFT:
                    moving_left = False
                elif event.key == pygame.K_RIGHT:
                    moving_right = False
                elif event.key == pygame.K_SPACE:
                    shooting = False

        if moving_left:
            speed[0] -= run_speed
        elif moving_right:
            speed[0] += run_speed

        if jumping:
            speed[1] -= jump_power

        if facing == 0 and speed[0] < 0:
            player = pygame.transform.flip(player, True, False)
            fire = pygame.transform.flip(fire, True, False)
            facing = 1
        elif facing == 1 and speed[0] > 0:
            player = pygame.transform.flip(player, True, False)
            fire = pygame.transform.flip(fire, True, False)
            facing = 0

        speed[0] *= 0.8
        if playerrect.top < 0 or playerrect.bottom > height:
            speed[1] = 0
            if playerrect.top < 0:
                playerrect.top = 0
            else:
                playerrect.bottom = height

        # This is where we handle falling.
        if playerrect.bottom < height:
            if speed[1] < max_fall:
                speed[1] += gravity

        tile_y = playerrect.bottom / TILE_HEIGHT
        tile_x = playerrect.centerx / TILE_WIDTH
        if mp.is_solid(tile_x, tile_y):
            if speed[1] > 0:
                speed[1] = 0

        playerrect = playerrect.move(speed)

        mp.tick()

        screen.fill(black)
        mp.draw(screen)
        screen.blit(player, playerrect)
        if shooting:
            rnd = random.randint(0, 8)
            firerect.bottom = playerrect.top + (playerrect.height / 2.6) + rnd
            if facing == 0:
                firerect.left = playerrect.right
            else:
                firerect.right = playerrect.left
            screen.blit(fire, firerect)
        pygame.display.flip()

if __name__ == '__main__':
    main()

