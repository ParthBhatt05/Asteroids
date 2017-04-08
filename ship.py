from __future__ import division
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy
import math

import entity
import bullets
import bezier
import model
from asteroids import WIDTH, HEIGHT, distance
import particle

SHIP_ACCEL = 0.1
SHIP_ROTSPEED = 4
SHIP_HEALTH_FADE = 0.08
SHIP_DEAD = 4 
SHIP_ACTIVE = 1
SHIP_FLYING_IN = 2
SHIP_FLYING_OUT = 3
SHIP_SCALE = 15

class Ship(entity.Entity):
    WRAPDIST = 25
    modelfile = "ship.obj"

    def __init__(self, hud):
        self.scale = SHIP_SCALE
        super(Ship, self).__init__(model.ObjModel(self.modelfile), 2*self.scale)
        self.pos = numpy.array((WIDTH/2, HEIGHT/2, 0),dtype=float)
        self.lives = 4
        hud.set_lives(self.lives)
        self.hud = hud
        self._state = 0
        # Store the ship's orientation as three angles:
        # theta is the rotation about the Z axis. When phi is 0, this is the angle the ship is pointing on the X/Y plane. 0 is straight up, and increasing angles turn the ship clockwise.
        self.theta = 30
        # phi is the counterclockwise rotation about the X axis (out of the page) Together with theta they describe the ship's direction
        self.phi = 0
        # rot is the rotation about the ship's axis (Y). When phi is 90, this variable is equivilant to theta
        self.rot = 0
        # translational velocity
        self.speed = numpy.array([0,0,0], dtype=float)
        self.accel = 1
        self.bullets = bullets.Bullets()
        self.healthmax = 7
        self.health = self.healthmax
        self.hud.set_health_max(self.healthmax)
        self.hud.set_health(self.health)
        self._reset()
        self._health_vis = 0
        self.autofire = True

    def direction(self):
        direction = numpy.matrix("[0;1;0]", dtype=float)
        cosphi = math.cos(self.phi*math.pi/180)
        sinphi = math.sin(self.phi*math.pi/180)
        xrot = numpy.matrix([[1, 0, 0],[0, cosphi, -sinphi],[0, sinphi, cosphi],], dtype=float)
        costheta = math.cos(self.theta*math.pi/180)
        sintheta = math.sin(self.theta*math.pi/180)
        zrot = numpy.matrix([[costheta, -sintheta, 0],[sintheta, costheta, 0],[0, 0, 1],], dtype=float)
        return numpy.array(zrot * xrot * direction).squeeze()

    def update(self):
        p = lambda: None
        [p, self._update_normal,self._update_bezier, self._update_bezier,p][self._state]()
        if self._thrusting:
            direction = self.direction()
            self.speed += SHIP_ACCEL * direction
            particle.thrust(self.pos-direction*4, self.speed - direction*2)
        if self._turning:
            self.theta += SHIP_ROTSPEED * self._turning
            self.rot = self.theta
        if self.autofire and self._trigger:
            self.fire()
        self.bullets.update()
        if self._health_vis > 0:
            self._health_vis -= SHIP_HEALTH_FADE

    def _update_normal(self):
        self.pos += self.speed
        if self.pos[0] > WIDTH + self.WRAPDIST:
            self.pos[0] = -self.WRAPDIST
        elif self.pos[0] < -self.WRAPDIST:
            self.pos[0] = WIDTH + self.WRAPDIST
        if self.pos[1] > HEIGHT + self.WRAPDIST:
            self.pos[1] = -self.WRAPDIST
        elif self.pos[1] < -self.WRAPDIST:
            self.pos[1] = HEIGHT + self.WRAPDIST

    def _update_bezier(self):
        direction = self.direction()
        particle.thrust(self.pos-direction*4, self.speed - direction*2)
        self._t += 1
        self.rot += 2
        current = self._bezier.B(self._t)
        self.pos = current[:3]
        self.theta = current[3]
        self.phi = current[4]
        if self._t >= self._bezier.tmax:
            if self._state == 2:
                self._state = 1
            else:
                self._state = 0

    def thrust(self, on):
        if self._state != 1:
            return
        self._thrusting = on

    def turn(self, dir):
        if self._state != 1:
            return
        self._turning = dir

    def draw(self):
        self.bullets.draw()
        if self._state == 4:
            return
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslated(*self.pos)
        glScaled(self.scale, self.scale, self.scale)
        glRotated(self.theta, 0,0,1)
        phi = self.phi
        if phi:
            glRotated(phi, 1,0,0)
        # ship's axis rotation. Do this last, so it's always along the ship's axis, not the world's Y axis
        glRotated(self.rot, 0,1,0)
        self.model.draw()
        if self._health_vis > 0:
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0,1,0,self._health_vis,))
            glDepthMask(GL_FALSE)
            glEnable(GL_BLEND)
            glutSolidSphere(2, 6, 6)
            glDepthMask(GL_TRUE)
            glDisable(GL_BLEND)
        glPopMatrix()

    def _reset(self):
        self.speed[:] = 0
        self._turning = 0
        self._thrusting = 0
        self._trigger = 0

    def fly_in(self):
        self._state = 2
        self._reset()
        # first 3 are position, second two are theta and phi
        p0 = numpy.array([WIDTH*0.5,HEIGHT/2,distance * 1.1,90.0,-90.0], dtype=float)
        p1 = numpy.array([WIDTH*0.5,HEIGHT/2,distance * 0.3,90.0,-80.0], dtype=float)
        p2 = numpy.array([WIDTH/2,HEIGHT/2,0,90,0], dtype=float)
        self.pos[:] = p0[:3]
        self.theta = p0[3]
        self.phi = p0[4]
        self._t = 0
        # Specify the number of frames to take as the 4th parameter
        self._bezier = bezier.Quadratic(p0,p1,p2,100)

    def fly_out(self):
        self._state = 3
        self._reset()
        p0 = numpy.empty((5,))
        p0[:3] = self.pos
        p0[3] = self.theta
        p0[4] = self.phi
        p2 = numpy.array([WIDTH*0.5,HEIGHT/2,distance * 1.1,0.0,90.0], dtype=float)
        p1 = p0.copy()
        p1[:3] += self.direction() * 200
        p1[3:] = (0.2*p0[3:] + 1.8*p2[3:]) / 2
        self._t = 0
        self._bezier = bezier.Quadratic(p0,p1,p2,200)

    def damage(self, damage_amt):
        if not self.is_active():
            return
        if self.health == 0:
            particle.explosion(self.pos, (0,10,0), self.speed)
            self.lives -= 1
            self.hud.set_lives(self.lives)
            self._state = 4
            self._reset()
        else:
            self.health = max(0, self.health-damage_amt)
            self.hud.set_health(self.health)
            self._health_vis = 1

    def new_ship(self):
        if (self.lives>-1):
            self.health = self.healthmax
            self.hud.set_health(self.health)
    
    def is_active(self):
        return self._state == 1

    def is_flying(self):
        return self._state == 2 or self._state == 3

    def is_dead(self):
        return self._state == SHIP_DEAD

    def trigger(self, on):
        if not self.autofire and on and not self._trigger:
            self.fire()
        self._trigger = on

    def fire(self):
        if not self.bullets.can_fire() or not self.is_active():
            return
        shipdirection = self.direction()
        position = self.pos + shipdirection*20
        velocity = self.bullets.speed * shipdirection + self.speed
        self.bullets.fire(self.pos, velocity)