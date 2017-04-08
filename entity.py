from __future__ import division
from OpenGL.GL import *
import random
import numpy
import math

import model
import particle

def check_collide(ent1, ent2):
    dist = numpy.linalg.norm(ent1.pos - ent2.pos)
    return dist < ent1.radius + ent2.radius

class Entity(object):

    def __init__(self, model, radius):
        self.model = model
        self.radius = radius

from asteroids import WIDTH, HEIGHT

class FloatingEntity(Entity):

    WRAPDIST = 30
    def __init__(self, model, initpos, vel, radius, scale=1):
        assert len(initpos) == 3
        self.pos = numpy.array(initpos, dtype=float)
        self.rotangle = 0
        self.scale = float(scale)
        theta = random.uniform(0, 360)
        phi = random.uniform(0, 180)
        rotaxis = [math.cos(theta)*math.sin(phi),math.sin(theta)*math.sin(phi),math.cos(theta)]
        self.rotaxis = numpy.array(rotaxis, dtype=float)
        self.dtheta = random.uniform(-5, 5)
        self.vel = numpy.array(vel, dtype=float)
        super(FloatingEntity, self).__init__(model, radius)

    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslated(*self.pos)
        if self.scale != 1:
            glScaled(self.scale, self.scale, self.scale)
        glRotatef(self.rotangle, *self.rotaxis)
        self.model.draw()
        glPopMatrix()

    def update(self):
        self.pos += self.vel
        self.rotangle += self.dtheta
        if self.pos[0] > WIDTH + self.WRAPDIST:
            self.pos[0] = -self.WRAPDIST
        elif self.pos[0] < -self.WRAPDIST:
            self.pos[0] = WIDTH + self.WRAPDIST
        if self.pos[1] > HEIGHT + self.WRAPDIST:
            self.pos[1] = -self.WRAPDIST
        elif self.pos[1] < -self.WRAPDIST:
            self.pos[1] = HEIGHT + self.WRAPDIST

class Asteroid(FloatingEntity):
    asteroidmodelclass = model.AsteroidModel

    def __init__(self, size, maxvel, initialpos=None):
        if initialpos is None:
            initialpos = [random.uniform(0,WIDTH),random.uniform(0,HEIGHT), 0]
        vel = [random.uniform(-maxvel, maxvel) for _ in xrange(2)]
        vel.append(0)
        self.size = size
        self.maxvel = maxvel
        scale = (3*size**2 + size * 5)
        self.WRAPDIST = scale*2
        super(Asteroid, self).__init__(self.asteroidmodelclass(), initialpos, vel,1.5*scale, scale)

    def split(self):
        particle.explosion(self.pos, (1,1,1))
        if self.size == 1:
            return ()
        newasteroids = []
        split_range = self.radius / 2
        for _ in xrange(2):
            newpos = self.pos
            newpos[:2] += numpy.random.uniform(-split_range, split_range, size=2)
            newasteroids.append(Asteroid(self.size-1,self.maxvel*1.1,newpos))
        return newasteroids