
from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from math import pi, sin, cos
from panda3d.core import Vec3
from panda3d.core import Point3
from panda3d.core import TransparencyAttrib
from Physics import PhysicsModeler
from direct.showbase.InputStateGlobal import inputState
from panda3d.core import Vec3, BitMask32
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletHelper
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletGhostNode
from panda3d.bullet import ZUp
import sys
import random
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from direct.actor.Actor import Actor
from pandac.PandaModules import TextNode, loadPrcFileData
loadPrcFileData('', 'bullet-enable-contact-events true')
from panda3d.core import *
from direct.gui.DirectGui import *
import sys
from direct.showbase.ShowBase import ShowBase
base = ShowBase()

class Level(object):
    def __init__(self):
        self.title = OnscreenText(
            text="ECCO",
            parent=base.a2dpTopCenter, align=TextNode.A_boxed_center,
            style=1, fg=(0.5, 0.5, 1, 1), pos=(0, -0.5), scale=.135, font=loader.loadFont("font/Caveman.ttf"))

        base.setBackgroundColor(0, 0, 0)

        bk_text = "This is my Demo"
        self.textObject = OnscreenText(text=bk_text, pos=(0.95, -0.95),
                                  scale=0.07, fg=(1, 0.5, 0.5, 1), align=TextNode.ACenter, mayChange=1)

        def level1():
            bk_text = "Level 1"
            self.textObject.setText(bk_text)


        def level2():
            bk_text = "Level 2"
            self.textObject.setText(bk_text)

        level1Button = DirectButton(text=("Level 1"), scale=.1, pos=(0, 0, 0.2), command=level1)

        level2Button = DirectButton(text=("Level 2"), scale=.1, pos=(0, 0, 0), command=level2)

    # def inputTask(self, task):
    #     if inputState.isSet('esc'):
    #         sys.exit(1)
    #
    #     if inputState.isSet('one'):
    #         sys.exit(1)
    #
    #     return task.cont




        # Add button




    #     self.setupLevelDisplay()
    #
    # def setupLevelDisplay(self):
    #     LEVEL_SELECT = "Please Select Level"
    #     levelN = TextNode('level-display')
    #     levelN.setText(LEVEL_SELECT)
    #     levelN.setTextColor(1, 1, 1, 1)
    #     levelN.setSlant(0.1)
    #     levelN.setShadow(0.05)
    #     levelN.setShadowColor(255, 0, 0, 1)
    #     levelN.setFrameAsMargin(0, 0, 0, 0)
    #     levelN.setFrameColor(0, 0, 255, 1)
    #     levelN.setFrameLineWidth(5.0)
    #     # textNp.node().setGlyphShift(1.0)
    #     textNodePath = self.aspect2d.attachNewNode(levelN)
    #     textNodePath.setPos(-0.3, 0, 0)
    #     textNodePath.setScale(0.2)

w = Level()
base.run()
