from __future__ import division

import entity
import enemy

class Level(object):
    def __init__(self, speed, asteroids, aliens):
        self.speed = speed
        self.asteroids = asteroids
        self.aliens = aliens
        self.aliens_entered = 0

    def create_asteroids(self):
        maxspeed = self.speed
        asteroids = set()

        for size, count in enumerate(self.asteroids):
            size += 1
            for _ in xrange(count):
                asteroids.add( entity.Asteroid(size, maxspeed) )
        return asteroids

    def enter_alien(self, target):
        if len(self.aliens) > self.aliens_entered:
            alien_type = self.aliens[self.aliens_entered]
            self.aliens_entered += 1
            alien_class = [None,enemy.Alien1,][alien_type]
            return alien_class(target)

level = [None,Level(1, [0,2,0], []),Level(2, [3,2,0], [1]),Level(3, [5,3,1], [1]),Level(4, [0,0,0,1], []),Level(5, [0,0,2,], [1]),]