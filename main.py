#!/Users/DY/anaconda3/bin/python
import pygame
from time import sleep, time
from math import sqrt, hypot
import plane
import missile
from pygame.locals import *
from random import randint, random, seed, choice
import sys
from termcolor import colored, cprint
import profile


class Game:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.display = None
        self.background_color = (66, 194, 245)
        self.running = True
        self.plane = None
        self.missiles = []
        self.alive = True
        self.fps = 60
        self.plane_img = pygame.image.load('jet.png')
        self.plane_img = pygame.transform.scale(self.plane_img, (40, 40))
        self.missile_img = pygame.image.load('missile.png')
        self.missile_img = pygame.transform.scale(self.missile_img, (15, 30))
        self.missile_img1 = pygame.image.load('missile1.png')
        self.missile_img1 = pygame.transform.scale(self.missile_img1, (20, 30))
        self.collision_img = pygame.image.load('collision.jpeg')
        self.collision_img = pygame.transform.scale(self.collision_img, (40, 40))
        self.collisions = []
        self.score = 0


    def init_display(self):
        """ -> void
        creates the game window
        """
        pygame.init()
        self.display = pygame.display.set_mode((self.width, self.height))
        self.display.fill((self.background_color))
        pygame.display.set_caption("AIM9X Sidewinder")


    def centering(self):
        """ prevents the plane from drifting outside of the window
        keeps the PLANE relatively in the center of the screen
        """
        x_pos_lim = 600
        x_neg_lim = 200
        y_pos_lim = 400
        y_neg_lim = 200
        x, y = self.plane.x, self.plane.y
        # shifting x
        if x > x_pos_lim:
            x_shift = x_pos_lim - x
        elif x < x_neg_lim:
            x_shift = x_neg_lim - x
        else:
            x_shift = 0
        # shifting y
        if y > y_pos_lim:
            y_shift = y_pos_lim - y
        elif y < y_neg_lim:
            y_shift = y_neg_lim - y
        else:
            y_shift = 0
        # shifts missiles and plane
        self.plane.shift(x_shift, y_shift)
        for m in self.missiles:
            m.shift(x_shift, y_shift)


    def spawn_missiles(self, omega_missile, v_missile):
        ''' spawn a missile near the plane when called
        4 cases: above below left right
        '''
        c = choice([0, 1, 2, 3])
        if c == 0:
            # spawn above
            self.missiles.append(missile.Missile(randint(-100, 900), 0, 0,\
                 v_missile, omega_missile, 0, 0, self.fps, 1))
        elif c == 1:
            # spawn below
            self.missiles.append(missile.Missile(randint(-100, 900), 600, 0,\
                 -1*v_missile, omega_missile, 0, 0, self.fps, 1))
        elif c == 2:
            # left
            self.missiles.append(missile.Missile(0, randint(-100, 700),\
                 v_missile, 0, omega_missile, 0, 0, self.fps, 1))
        else:
            # right
            self.missiles.append(missile.Missile(800, randint(-100, 700),\
                 -1*v_missile, 0, omega_missile, 0, 0, self.fps, 1))


    def kb_control(self, keys):
        """ (tuple(bool)) -> void
        takes kb inputs and controls the plane/quit the game
        """
        if keys[K_LEFT] and not keys[K_RIGHT]:
            # counter clockwise
            self.plane.move(-1)
        elif keys[K_RIGHT] and not keys[K_LEFT]:
            # clockwise
            self.plane.move(1)
        elif not keys[K_RIGHT] and not keys [K_LEFT]:
            self.plane.move()
        else:
            self.plane.move()
        if keys[K_ESCAPE]:
            self.quit()
            self.running = False


    def rot_center(self, image, angle):
        """rotate an image while keeping its center and size
        ** for square only
        borrowed from https://www.pygame.org/wiki/RotateCenter?parent=CookBook
        """
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image


    def draw_plane(self):
        ''' draws the plane, gets pos by calling pos()
        '''
        # pygame.draw.circle(self.display, (0, 0, 255), self.plane.pos(), 8)
        x, y = self.plane.pos()
        x -= 15         # adjusting the center of of the jet
        y -= 15
        rotated = self.rot_center(self.plane_img, self.plane.get_angle())
        # rotated = pygame.transform.rotate(self.plane_img, self.plane.get_angle())
        self.display.blit(rotated, (x, y))


    def draw_missiles(self):
        ''' draws all missiles if there are any
        '''
        if len(self.missiles) != 0:
            for m in self.missiles:
                # pygame.draw.circle(self.display, (255, 0, 0), m.pos(), 10)
                x, y = m.pos()
                x -= 7.5
                y -= 15
                rotated = pygame.transform.rotate(self.missile_img, m.get_angle())
                self.display.blit(rotated, (x, y))


    def is_alive(self, radius):
        ''' detects if plane and missiles are alive
        if hit, sets self.alive to 0
        '''
        for m in self.missiles:
            s = sqrt((m.x-self.plane.x)**2 + (m.y-self.plane.y)**2)
            if s < radius:
                # plane destroyed, ask for restart
                self.alive = False
                m.hit = True
                return False
            if hypot(m.v[0], m.v[1]) < 160:
                # destroys missile if it's slower than the plane
                m.alive = False
                self.missiles.remove(m)
                self.score += 1


    def missiles_collision(self, radius):
        ''' detects missile collision
        '''
        for i, m1 in enumerate(self.missiles):
            for j, m2 in enumerate(self.missiles):
                if i != j and hypot(m1.x-m2.x, m1.y-m2.y) < radius:
                    # collision!
                    cprint("KABOOOM!!!", 'red', attrs=['bold'])
                    self.missiles.remove(m1)
                    self.missiles.remove(m2)
                    self.collisions.append([time(), int(round((m1.x+m2.x)/2)), int(round((m1.y+m2.y)/2))])
                    self.score += 2


    def draw_explosion(self):
        ''' draws display the explosion when 2 missiles collide
        '''
        for c in self.collisions:
            if (time() - c[0]) < 0.5:
                # self.display.blit(self.collision_img, (c[1], c[2])
                pygame.draw.circle(self.display, (255,0,0), (c[1], c[2]), 8)
            else:
                self.collisions.remove(c)


    def mainloop(self, omega_missile, v_missile):
        """ Called by run() at every tick
        Controls the game routine
        """
        keys = pygame.key.get_pressed()
        events = pygame.event.get()         # this makes the display work!
        # spawn missiles randomly
        spawn_rate = 0.5        # 0.1 missile/s
        if random() < (spawn_rate / self.fps):
            self.spawn_missiles(omega_missile, v_missile)
        self.missiles_collision(8)
        self.kb_control(keys)               # this also moves the plane
        if len(self.missiles) != 0:
            for m in self.missiles:
                m.move(self.plane)
        self.centering()
        self.draw_plane()
        self.draw_missiles()
        self.draw_explosion()
        self.is_alive(15)
        pygame.display.flip()
        self.display.fill(self.background_color)
        pygame.display.set_caption("AIM9X  Missile Dodged: {}".format(self.score))
        sleep(1/self.fps)


    def run(self, omega_plane=540, v_plane=240, omega_missile=150, v_missile=500):
        """ () -> void
        runs the game routine
        ORDER OR OPERATION:
        1. move()
        2. shift()
        3. pos()
        """
        # seed(7)
        self.alive = True
        self.score = 0
        self.init_display()
        self.plane = plane.Plane(400, 200, 0, v_plane, omega_plane, self.fps)
        self.missiles = []
        self.missiles.append(missile.Missile(randint(-100, 900), 0, 0, v_missile, omega_missile, 0, 0, self.fps, 1))
        try:
            while self.alive:
                # main game loop
                self.mainloop(omega_missile, v_missile)
            cprint("You got destroyed by the AIM9X Sidewinder", 'red', 'on_green', attrs=['bold'])
            cprint("Press <ENTER> to restart", 'red')
            while not self.alive and self.running:
                # restart loop
                self.restart()
        except KeyboardInterrupt:
            self.quit()


    def restart(self):
        ''' restart loop
        '''
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        pygame.display.set_caption("Destroyed by the AIM9X!  Score: {}  <ENTER> to restart, <ESC> to quit".format(self.score))
        if keys[K_ESCAPE]:
            self.quit()
            self.running = False
        elif keys[K_RETURN]:
            self.run()


    def quit(self):
        cprint("Good Bye!", "green", attrs=["bold"])
        s = 'High score: {}'.format(self.score)
        cprint(s, 'green')
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
