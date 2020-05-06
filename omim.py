#! /usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2016 Marcos Dione <mdione@grulic.org.ar>

# This file *is* OurManInMarseille.
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

from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap, QKeySequence, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsPixmapItem, QAction
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import QTimer, QObject, QSize, Qt, QRectF

from gi.repository import GExiv2, GLib


class OMIMMain (QObject):
    def __init__ (self, view, scene, item, root, *args):
        QObject.__init__ (self, view)
        self.view= view
        self.scene= scene
        self.item= item

        self.zoomLevel= 1.0
        self.rotation= 0

        self.files= []
        self.scan (root)


    def scan (self, root):
        # print ('scanning %s' % root)
        for r, dirs, files in os.walk (os.path.abspath (root)):
            for name in files:
                if name[-4:].lower () in ('.jpg', '.png'):
                    # print ('found %s' % name)
                    self.files.append (os.path.join (r, name))


    def rotate (self, metadata, origImgSize):
        # Qt only handles orientation properly from v5.5
        try:
            # try directly to get the tag, because sometimes get_tags() returns
            # tags that don't actually are in the file
            rot= metadata['Exif.Image.Orientation']
        except KeyError:
            # guess :-/
            print ("rotation 'guessed'")
            rot= '1'

        # see http://www.daveperrett.com/images/articles/2012-07-28-exif-orientation-handling-is-a-ghetto/EXIF_Orientations.jpg
        # we have to 'undo' the rotations, so the numbers are negative
        if rot=='1':
            rotate= 0
            imgSize= origImgSize
        if rot=='8':
            rotate= -90
            imgSize= QSize (origImgSize.height (), origImgSize.width ())
        if rot=='3':
            rotate= -180
            imgSize= origImgSize
        if rot=='6':
            rotate= -270
            imgSize= QSize (origImgSize.height (), origImgSize.width ())

        # undo the last rotation and apply the new one
        self.view.rotate (-self.rotation+rotate)
        self.rotation= rotate
        # print (rot, rotate, self.rotation)

        return imgSize


    def zoomFit (self, imgSize):
        winSize= self.view.size ()
        # we might have rotated the view, but the scene still has the image
        # in its original size, so we use that as bounding rect
        boundingRect= QRectF (self.item.pixmap ().rect ())
        self.scene.setSceneRect (boundingRect)

        hZoom= winSize.width  ()/imgSize.width  ()
        vZoom= winSize.height ()/imgSize.height ()
        zoomLevel= min (hZoom, vZoom)
        # print (zoomLevel)

        scale= zoomLevel/self.zoomLevel
        # print ("scaling", scale)
        self.view.scale (scale, scale)
        self.view.centerOn (self.item)
        self.zoomLevel= zoomLevel


    def nextImage (self, *args):
        found_next= False
        while not found_next:
            fname= random.choice (self.files)
            print (fname)

            try:
                metadata= GExiv2.Metadata (fname)
            except GLib.Error as e:
                print (repr (e))
            else:
                found_next= True

        img= QPixmap (fname)
        imgSize= self.rotate (metadata, img.size ())

        self.item.setPixmap (img)
        # print (self.item.pos ().x(), self.item.pos ().y(), )
        self.zoomFit (imgSize)

        # print (self.view.size (), self.view.sceneRect ())
        # print (self.scene.sceneRect ())
        # print (self.item.boundingRect (), self.item.pos ().x (),
        #        self.item.pos ().y (), imgSize)


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

    view= QGraphicsView (scene, win)
    view.setFrameShadow (QFrame.Plain)
    view.setFrameStyle (QFrame.NoFrame)

    brush = QBrush(QColor(0, 0, 0))
    brush.setStyle(Qt.SolidPattern)
    view.setBackgroundBrush(brush)

    runner= OMIMMain (view, scene, item, sys.argv[1])

    timer= QTimer (app)
    timer.timeout.connect (runner.nextImage)
    timer.start (float (sys.argv[2])*1000)

    firstImage= QTimer.singleShot (200, runner.nextImage)

    view.show()
    win.setCentralWidget (view)
    win.showFullScreen ()

    app.exec_ ()
