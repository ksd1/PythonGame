import sys
import pygame
from pygame import *
from math import sin, cos, pi

SCREEN_RECT = Rect(0, 0, 1024, 768)
SHIP_ROTATION = 0.6
METEORS_COUNT = 2


def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


def calc_move_forward(currPos, angle):
    radius=1
    radianAngle = angle * pi / 180
    currPos[0] += radius * cos(radianAngle)
    currPos[1] -= radius * sin(radianAngle)


def calc_move_backward(currPos, angle):
    radius = 1
    radianAngle = angle * pi / 180
    currPos[0] -= radius * cos(radianAngle)
    currPos[1] += radius * sin(radianAngle)


def back_position_to_screen(position, screen_size):
    if position[0] > screen_size[2]:
        position[0] = screen_size[0]
    elif position[0] < screen_size[0]:
        position[0] = screen_size[2]

    if position[1] > screen_size[3]:
        position[1] = screen_size[1]
    elif position[1] < screen_size[1]:
        position[1] = screen_size[3]


def main():
    pygame.init()
    #bestdepth = pygame.display.mode_ok(SCREEN_RECT.size, 0, 32)
    screen = pygame.display.set_mode([1024,768])
    background = pygame.Surface(screen.get_size())
    background.fill((255, 255, 255))

    #set shit
    ship = pygame.image.load("../assets/ship.png")
    shipRect = ship.get_rect()
    shipPos = [0, 0]
    shipAngle = 0
    shipRect = shipRect.move(shipPos);


    #set meteors
    meteor_slowdown_counter = 10
    meteors_list = []
    meteor_list_copy = []
    for i in xrange(1, METEORS_COUNT):
        meteor_image = pygame.image.load("../assets/meteor.png")
        meteor_rect = meteor_image.get_rect()
        meteor_pos = (600, 600)
        meteor_rect = meteor_rect.move(meteor_pos)
        meteors_list.insert(-1, (meteor_image, meteor_rect, meteor_pos))

    while True:
        keys = key.get_pressed()
        if keys[K_ESCAPE]:
            sys.exit()
        if keys[K_LEFT]:
            shipAngle += SHIP_ROTATION
        if keys[K_RIGHT]:
            shipAngle -= SHIP_ROTATION
        if keys[K_UP]:
            calc_move_forward(shipPos, shipAngle)
            back_position_to_screen(shipPos, SCREEN_RECT )
        if keys[K_DOWN]:
            calc_move_backward(shipPos, shipAngle)
            back_position_to_screen(shipPos, SCREEN_RECT)

        print shipPos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        #move ship
        shipAngle %= 360
        ship_copy = rot_center(ship, shipAngle)
        ship_copy_rect = ship_copy.get_rect(center=shipRect.center)
        ship_copy_rect = ship_copy_rect.move(shipPos)

        #move meteors
        if meteor_slowdown_counter < 0:
            for meteor in meteors_list:
                meteor_image = meteor[0]
                meteor_rect = meteor[1].move(-1, -1)
                meteor_pos = meteor[2]
                meteor_list_copy.insert(-1, (meteor_image, meteor_rect, meteor_pos))
            meteors_list = meteor_list_copy
            meteor_list_copy = []
            meteor_slowdown_counter = 10
        else:
            meteor_slowdown_counter -= 1

        #blit all objects
        screen.blit(background, (0, 0))
        screen.blit(ship_copy, ship_copy_rect)
        for meteor in meteors_list:
            screen.blit(meteor[0], meteor[1])

        pygame.display.update()


main()