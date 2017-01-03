import sys
import pygame
from pygame import *
from random import randint
from math import sin, cos, pi, ceil
from trajectory_functions import *
import numpy as np
import copy

SCREEN_RECT = Rect(0, 0, 1024, 768)
SHIP_ROTATION = 0.6
MAX_METEORS_COUNT = 1


def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


def calc_move_forward(currPos, angle, radius):
    radianAngle = angle * pi / 180
    currPos[0] += radius * cos(radianAngle)
    currPos[1] -= radius * sin(radianAngle)


def calc_move_backward(currPos, angle, radius):
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


def is_out_of_screen(position, screen_size):
    if position[0] > screen_size[2] or position[0] < screen_size[0] or position[1] > screen_size[3] or position[1] < screen_size[1]:
        return True
    else:
        return False


def get_new_meteor():
    meteor_image = pygame.image.load("../assets/meteor.png")
    meteor_rect = meteor_image.get_rect()

    meteor_beg_x = SCREEN_RECT[0];
    meteor_side = randint(0, 1)
    meteor_side_factor = 1
    if meteor_side == 1:
        meteor_beg_x = SCREEN_RECT[2]
        meteor_side_factor = -1

    meteor_beg = [meteor_beg_x, randint(SCREEN_RECT[1], SCREEN_RECT[3])]
    random_screen_point = [randint(SCREEN_RECT[0], SCREEN_RECT[2]), randint(SCREEN_RECT[1], SCREEN_RECT[3])]

    # solve Y = a * X +b
    matrixA = np.array([[meteor_beg[0], 1], [random_screen_point[0], 1]])
    matrixB = np.array([[meteor_beg[1], random_screen_point[1]]]).T
    equation = np.linalg.solve(matrixA, matrixB)
    coefficients = [equation[0][0], equation[1][0]]
    meteor_rect = meteor_rect.move(meteor_beg)

    meteor_tuple = (meteor_image, meteor_rect, meteor_beg, coefficients, meteor_side_factor)

    return meteor_tuple


def get_new_bullet(begin_pos, angle):
    bullet_image = pygame.image.load("../assets/bullet.png")
    bullet_rect = bullet_image.get_rect()
    bullet_rect = bullet_rect.move(begin_pos)
    bullet = (bullet_image, bullet_rect, begin_pos, angle)
    return bullet


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

    #set bullets
    bullets_list = []
    bullets_list_copy = []

    #set meteors
    meteor_slowdown_counter = 10
    meteors_counter = MAX_METEORS_COUNT
    meteors_list = []
    meteor_list_copy = []
    for i in xrange(0, MAX_METEORS_COUNT):
        meteors_list.insert(-1, get_new_meteor())

    while True:
        keys = key.get_pressed()
        if keys[K_ESCAPE]:
            sys.exit()
        if keys[K_LEFT]:
            shipAngle += SHIP_ROTATION
        if keys[K_RIGHT]:
            shipAngle -= SHIP_ROTATION
        if keys[K_UP]:
            calc_move_forward(shipPos, shipAngle, 1)
            back_position_to_screen(shipPos, SCREEN_RECT)
        if keys[K_DOWN]:
            calc_move_backward(shipPos, shipAngle, 1)
            back_position_to_screen(shipPos, SCREEN_RECT)
        if keys[K_SPACE]:
            pos_copy = copy.copy(shipPos)
            bullets_list.insert(-1, get_new_bullet(pos_copy, shipAngle))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        #move ship
        shipAngle %= 360
        ship_copy = rot_center(ship, shipAngle)
        ship_copy_rect = ship_copy.get_rect(center=shipRect.center)
        ship_copy_rect = ship_copy_rect.move(shipPos)

        #move bullets
        for bullet in bullets_list:
            bullet_image = bullet[0]
            bullet_rect = bullet[1]
            bullet_pos = bullet[2]
            bullet_angle = bullet[3]

            old_x = bullet_pos[0]
            old_y = bullet_pos[1]

            calc_move_forward(bullet_pos, bullet_angle, 3)

            off_x = bullet_pos[0] - old_x
            off_y = bullet_pos[1] - old_y

            print "OFF_X: ", off_x, " OFF_Y: ", off_y

            if not is_out_of_screen(bullet_pos, SCREEN_RECT):
                bullet_rect = bullet[1].move(off_x, ceil(off_y))
                bullets_list_copy.insert(-1, (bullet_image, bullet_rect, bullet_pos, bullet_angle))

        bullets_list = bullets_list_copy
        bullets_list_copy = []

        #move meteors
        if meteor_slowdown_counter < 0:
            for meteor in meteors_list:
                meteor_image = meteor[0]
                meteor_pos = meteor[2]
                meteor_coefficients = meteor[3]
                meteor_side_factor = meteor[4]

                new_meteor_pos = [meteor_pos[0], meteor_pos[1]]
                meteor_trajectory(new_meteor_pos, meteor_coefficients, meteor_side_factor)

                #print new_meteor_pos
                off_x = new_meteor_pos[0] - meteor_pos[0]
                off_y = new_meteor_pos[1] - meteor_pos[1]

                if not is_out_of_screen(new_meteor_pos, SCREEN_RECT):
                    meteor_rect = meteor[1].move(off_x, ceil(off_y))
                    meteor_list_copy.insert(-1, (meteor_image, meteor_rect, new_meteor_pos, meteor_coefficients, meteor_side_factor))
                else:
                    meteors_counter -= 1

            meteors_list = meteor_list_copy
            meteor_list_copy = []
            meteor_slowdown_counter = 10
        else:
            meteor_slowdown_counter -= 1

        #check collision meteors with ship
        ship_collision = False;
        for meteor in meteors_list:
            if ship_copy_rect.colliderect(meteor[1]):
                ship_collision = True
                break

        if ship_collision:
            break;

        not_collided_meteors = []
        #check collision bullets with meteors
        if bullets_list:
            for bullet in bullets_list:
                for meteor in meteors_list:
                    if not bullet[1].colliderect(meteor[1]):
                        not_collided_meteors.insert(-1, meteor)

            meteors_list = not_collided_meteors
            not_collided_meteors = []

        #blit all objects
        screen.blit(background, (0, 0))
        screen.blit(ship_copy, ship_copy_rect)

        for bullet in bullets_list:
            screen.blit(bullet[0], bullet[1])

        for meteor in meteors_list:
            screen.blit(meteor[0], meteor[1])

        pygame.display.update()




main()