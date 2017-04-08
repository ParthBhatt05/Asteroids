from OpenGL.GL import *
from OpenGL.GLUT import *

from util import get_displaylist

def render_string(x, y, string):
    glRasterPos2d(x, y)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

def _make_dl_hud_prepare():
    dl_num = get_displaylist()
    glNewList(dl_num, GL_COMPILE)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 1, 0, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDepthMask(GL_FALSE)
    glDisable(GL_LIGHTING)
    glEndList()
    return dl_num

def _make_dl_hud_restore():
    dl_num = get_displaylist()
    glNewList(dl_num, GL_COMPILE)
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)
    glEnable(GL_LIGHTING)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEndList()
    return dl_num

class HUD(object):
    def __init__(self):
        dl_hud_prepare = _make_dl_hud_prepare()
        dl_hud_restore = _make_dl_hud_restore()
        self.level_dl = get_displaylist()
        self.lives_dl = get_displaylist()
        self.health_outline = get_displaylist()
        self.health_level = get_displaylist()
        self.master_dl = get_displaylist()
        glNewList(self.master_dl, GL_COMPILE)
        glCallList(dl_hud_prepare)
        glCallList(self.level_dl)
        glCallList(self.lives_dl)
        glCallList(self.health_outline)
        glCallList(self.health_level)
        glCallList(dl_hud_restore)
        glEndList()

    def draw(self):
        glCallList(self.master_dl)

    def set_level(self, level):
        glNewList(self.level_dl, GL_COMPILE)
        glColor3f(0.0, 1.0, 0.0)
        render_string(0.01, 0.975, "Level:")
        render_string(0.075, 0.975, str(level))
        glEndList()

    def set_lives(self, lives):
        glNewList(self.lives_dl, GL_COMPILE)
        glColor3f(0.0, 1.0, 0.0)
        if (lives>-1):
            render_string(0.18, 0.975, "Lives Left:")
            render_string(0.28, 0.975, str(lives))
            render_string(0.86, 0.975, "Press ALT to Pause")
        else:
            render_string(0.18, 0.975, "Game Over")
            render_string(0.08, 0.975, " ")
        glEndList()

    def set_health(self, amt):
        border = 0.000
        length = amt * 0.05 - border
        glNewList(self.health_level, GL_COMPILE)
        glColor3f(0.0, 1.0, 0.0)
        render_string(0.375, 0.975, "Health:")
        glBegin(GL_QUADS)
        glVertex2d(0.45+border,0.985)
        glVertex2d(0.45+border,0.975)
        glVertex2d(0.45+length+border,0.975)
        glVertex2d(0.45+length+border,0.985)
        glEnd()
        glEndList()

    def set_health_max(self, upper):
        length = upper * 0.05
        glNewList(self.health_outline, GL_COMPILE)
        glColor3f(0.0,1.0,0.0)
        glBegin(GL_LINE_LOOP)
        glVertex2d(0.45,0.985)
        glVertex2d(0.45,0.975)
        glVertex2d(0.45+length,0.975)
        glVertex2d(0.45+length,0.985)
        glEnd()
        glEndList()