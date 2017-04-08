from OpenGL.GL import *
import numpy

import entity
import model
import bullets
import particle

class Alien1(entity.Entity):
    model = None
    health = 3

    def __init__(self, target):
        if Alien1.model is None:
            Alien1.model = model.ObjModel("alien_torus.obj", scale=10)
        super(Alien1, self).__init__(Alien1.model, 20)
        self.player = target
        self.health = Alien1.health
        self.pos = numpy.array([0,0,0],dtype=float)
        self.rot = 0
        self.vel = numpy.zeros((3,))
        self.redirect_countdown = 100
        self.bullet_countdown = 80
        self.bullets = bullets.Bullets(color=(1,0,0,1))

    def damage(self, amt):
        self.health -= amt
        if self.health <= 0:
            particle.explosion(self.pos, (10,0,0), self.vel)
            return True
        return False

    def update(self):
        self.bullets.update()
        self.rot += 5
        if self.rot >= 360:
            self.rot -= 360
        self.pos += self.vel
        self.redirect_countdown -= 1
        self.bullet_countdown -= 1
        self.vel *= 0.995
        if self.redirect_countdown <= 0:
            self.redirect_countdown = 200
            newdir = self.player.pos - self.pos
            newdir /= numpy.linalg.norm(newdir)
            newdir *= 3
            self.vel = newdir
        if self.bullet_countdown <= 0:
            self.bullet_countdown = 80
            bulvel = self.player.pos - self.pos
            bulvel /= numpy.linalg.norm(bulvel)
            bulvel *= self.bullets.speed
            self.bullets.fire(self.pos, bulvel)

    def draw(self):
        glPushMatrix()
        glTranslated(*self.pos)
        glRotated(self.rot, 0, 1, 0)
        self.model.draw()
        glPopMatrix()
        self.bullets.draw()