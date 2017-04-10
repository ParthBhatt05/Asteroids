from __future__ import division
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy

WIDTH = 1200
HEIGHT = 675
fov = 45
distance = HEIGHT/2 / math.tan(fov/2*math.pi/180)

import entity
import ship
import particle
import levels
import hud

class Game(object):

    def __init__(self):
        self.asteroids = set()
        self.hud = hud.HUD()
        self.ship = ship.Ship(hud=self.hud)
        self.level = 1
        self.hud.set_level(self.level)
        self._level_frame = 0
        self.enemies = set()
        self.asteroids.update(levels.level[self.level].create_asteroids())
        self._update_func = self._update_during_level
        self.ship.fly_in()

    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.hud.draw()
        glEnable(GL_LIGHTING)
        if self.level < 6 and self.ship.lives > -1:
            for a in self.asteroids:
                a.draw()
            self.ship.draw()
            particle.draw()
            for enemy in self.enemies:
                enemy.draw()
            glFlush()
        glutSwapBuffers()

    def update(self, value):
        if self.level<6 and self.ship.lives> -1:
            glutTimerFunc(20, self.update, 0)
            for a in self.asteroids:
                a.update()
            for enemy in self.enemies:
                enemy.update()
            self.ship.update()
            self.collision()
            particle.update()
            self.game_update()
            self._level_frame += 1
            if self._level_frame % 500 == 0:
                newalien = levels.level[self.level].enter_alien(self.ship)
                if newalien:
                    self.enemies.add(newalien)
            glutPostRedisplay()

    def keypress(self, key, x, y):
        try:{
                    GLUT_KEY_UP: lambda: self.ship.thrust(1),
                    GLUT_KEY_LEFT: lambda: self.ship.turn(1),
                    GLUT_KEY_RIGHT: lambda: self.ship.turn(-1),
                    ' ': lambda: self.ship.trigger(1),
            }[key]()
        except KeyError:
            pass

    def keyup(self, key, x, y):
        try:{
                    GLUT_KEY_UP: lambda: self.ship.thrust(0),
                    GLUT_KEY_LEFT: lambda: self.ship.turn(0),
                    GLUT_KEY_RIGHT: lambda: self.ship.turn(0),
                    ' ': lambda: self.ship.trigger(0),
            }[key]()
        except KeyError:
            pass

    def collision(self):
        toremove = set()
        toadd = set()
        enemies_toremove = set()
        ship = self.ship
        for bullet in ship.bullets.bullets:
            for asteroid in self.asteroids:
                if entity.check_collide(bullet, asteroid):
                    bullet.ttl = 0
                    newasteroids = asteroid.split()
                    toadd.update(newasteroids)
                    toremove.add(asteroid)
            for enemy in self.enemies:
                if entity.check_collide(bullet, enemy):
                    bullet.ttl = 0
                    if enemy.damage(ship.bullets.damage):
                        enemies_toremove.add(enemy)
        if ship.is_active():
            for asteroid in self.asteroids:
                distance = numpy.linalg.norm(ship.pos - asteroid.pos)
                if distance < ship.radius + asteroid.radius:
                    newasteroids = asteroid.split()
                    toadd.update(newasteroids)
                    toremove.add(asteroid)
                    ship.damage(1)
                    if not ship.is_active():
                        break
            for enemy in self.enemies:
                for bullet in enemy.bullets.bullets:
                    if entity.check_collide(bullet, self.ship):
                        bullet.ttl = 0
                        ship.damage(enemy.bullets.damage)
        self.asteroids -= toremove
        self.asteroids |= toadd
        self.enemies -= enemies_toremove

    def game_update(self):
        self._update_func()

    def _update_during_level(self):
        dead = self.ship.is_dead()
        lvl_complete = len(self.asteroids) == 0 and len(self.enemies) == 0
        if self.ship.lives < 0:
            pass
        elif dead and lvl_complete:
            self._t = 0
            self._update_func = self._update_ship_next_level
        elif dead:
            self._t = 0
            self._update_func = self._update_respawn
        elif lvl_complete:
            self.ship.fly_out()
            self._update_func = self._update_ship_next_level
        elif self.level > 5:
            pass

    def _update_ship_next_level(self):
        if self.ship.lives>-1 and self.level<6:
            if self.ship.is_flying():
                self._t = 0
            else:
                self._t += 1
            if self._t >= 100:
                self.level += 1
                self._level_frame = 0
                self.hud.set_level(self.level)
                if self.level<6:
                    self.asteroids.update( levels.level[self.level].create_asteroids() )
                if self.ship.is_dead():
                    self.ship.new_ship()
                self.ship.fly_in()
                self._update_func = self._update_during_level

    def _update_respawn(self):
        if self.ship.lives > -1 and self.level < 6:
            self._t += 1
            if self._t > 100:
                self.ship.new_ship()
                self.ship.fly_in()
                self._update_func = self._update_during_level

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow("Asteroids")
    g = Game()
    glutDisplayFunc(g.draw)
    glutTimerFunc(0, g.update, 0)
    glutKeyboardFunc(g.keypress)
    glutKeyboardUpFunc(g.keyup)
    glutSpecialFunc(g.keypress)
    glutSpecialUpFunc(g.keyup)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov, WIDTH/HEIGHT, 10, distance+100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(WIDTH/2.0, HEIGHT/2.0, distance+10,WIDTH/2.0,HEIGHT/2.0,0,0, 1, 0)
    ambience = [0, 0, 0, 0]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambience)
    glLightfv(GL_LIGHT0, GL_POSITION, (1,1,2,0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2,0.2,0.2,1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (.6,.6,.6,1))
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glDisable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glShadeModel(GL_SMOOTH)
    glClearDepth(1.0)
    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_RESCALE_NORMAL)
    glutMainLoop()

if __name__ == "__main__":
    main()