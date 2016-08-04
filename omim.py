#! /usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2016 Marcos Dione <mdione@grulic.org.ar>

# This file is part of OurManInMarseille.
#
# ayrton is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ayrton is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ayrton.  If not, see <http://www.gnu.org/licenses/>.

"""
OurManInMarseille - Recursive random slideshow
"""

import os
import os.path
import random
import sys

from PyQt4.QtGui import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PyQt4.QtGui import QPixmap, QGraphicsPixmapItem, QAction, QKeySequence
from PyQt4.QtCore import QTimer, QObject


class OMIMMain (QObject):
    def __init__ (self, view, item, root, *args):
        QObject.__init__ (self, view)
        self.view= view
        self.item= item
        self.zoomLevel= 1.0

        self.files= []
        self.scan (root)


    def scan (self, root):
        # print ('scanning %s' % root)
        for r, dirs, files in os.walk (os.path.abspath (root)):
            for name in files:
                if name[-4:] in ('.jpg', '.png'):
                    # print ('found %s' % name)
                    self.files.append (os.path.join (r, name))


    def zoomFit (self, img):
        winSize= self.view.size ()
        imgSize= img.size ()
        # print (winSize, imgSize)

        hZoom= winSize.width  ()/imgSize.width  ()
        vZoom= winSize.height ()/imgSize.height ()
        zoomLevel= min (hZoom, vZoom)
        # print (zoomLevel)

        scale= zoomLevel/self.zoomLevel
        # print ("scaling", scale)
        self.view.centerOn (self.item)
        self.view.scale (scale, scale)
        self.zoomLevel= zoomLevel


    def newImage (self, *args):
        fname= random.choice (self.files)
        print (fname)

        img= QPixmap (fname)
        self.item.setPixmap (img)
        # print (self.item.pos ().x(), self.item.pos ().y(), )
        self.zoomFit (img)

        self.item= item


if __name__=='__main__':
    if len (sys.argv)<3:  # awwww :)
        print ("""usage: %s ROOT SECONDS

ROOT points to the root directory where the images are going to be picked up.
SECONDS is the time between images.""" % sys.argv[0])
        sys.exit (1)

    app= QApplication (sys.argv)
    win= QMainWindow ()

    scene= QGraphicsScene ()
    item= QGraphicsPixmapItem ()
    scene.addItem (item)
    view= QGraphicsView (scene)
    view.show()

    runner= OMIMMain (view, item, sys.argv[1])
    runner.newImage ()

    timer= QTimer (app)
    timer.timeout.connect (runner.newImage)
    timer.start (float (sys.argv[2])*1000)

    app.exec_ ()
