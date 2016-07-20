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


class coins(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        taskMgr.add(self.update, "update")
        #coins variables
        self.coinsCollected = 0
        self.dictOfCoins = {}

        # world
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))

        # Set up Coins as Collectables
        #self.setupCoins()

        # Set up plank
        self.setupCoinOnPlank()
        self.topPlank()

        base.disableMouse()
        base.cam.setPos(0, -10, 2)
        base.cam.lookAt(0, 0, 2)

        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(True)
        debugNode.showNormals(True)
        debugNP = self.render.attachNewNode(debugNode)
        debugNP.show()
        self.world.setDebugNode(debugNP.node())


    def update(self, task):

        dt = globalClock.getDt()
        #self.world.doPhysics(dt, 10, 1 / 180.0)
        self.world.doPhysics(dt, 10, 1 / 230.0)
        return task.cont

    def setupCoins(self):
        #display coins = 0
        textN = TextNode('coin-score')
        textN.setText(str("Coins: " + str(self.coinsCollected)))
        textN.setSlant(0.1)
        # textNp.node().setGlyphShift(1.0)
        textNodePath = self.aspect2d.attachNewNode(textN)
        textNodePath.setPos(0, 0.95, 0.9)
        textNodePath.setScale(0.08)

        #coins
        self.coins = []
        for i in range(1):
            randX = random.uniform(-3.5, 3.5)
            randY = random.randint(0, 1000)
            shape = BulletSphereShape(0.75)
            coinNode = BulletGhostNode('Coin-' + str(i))
            coinNode.addShape(shape)
            np = self.render.attachNewNode(coinNode)
            np.setCollideMask(BitMask32.allOff())
            np.setPos(0,10, 2)

            # #Adding sphere model
            # sphereNp = loader.loadModel('models/smiley.egg')
            # sphereNp_tex = loader.loadTexture("models/sky/coin_2_tex.jpg")
            # sphereNp.setTexture(sphereNp_tex, 1)
            # sphereNp.reparentTo(np)
            # sphereNp.setScale(0.85)
            # rotate_coin = sphereNp.hprInterval(2.5, Vec3(360, 0, 0))
            # rotate_coin.loop()
            self.world.attachGhost(coinNode)
            #self.coins.append(coinNode)
            print "node name:" + str(coinNode.getName())

    def setupCoinOnPlank(self):
        # Plane
        size = Vec3(2.5, 0.6, 0.3)
        shape = BulletBoxShape(Vec3(1, 0.1, 0.1))
        node = BulletRigidBodyNode('Box')
        node.setMass(0)
        node.addShape(shape)
        np = self.render.attachNewNode(node)
        np.setPos(0, 0, 0)
        np.setR(0)
        self.world.attachRigidBody(node)

        modelNP = loader.loadModel('models/box.egg')
        modelNP_tex = loader.loadTexture("models/sky/moon_tex.jpg")
        modelNP.setTexture(modelNP_tex, 1)
        modelNP.reparentTo(np)
        modelNP.setPos(-1, 0, -1)
        modelNP.setPos(-size.x / 2.0, -size.y / 2.0, -size.z / 2.0)
        modelNP.setScale(size)


        # # Boxes
        # model = loader.loadModel('models/box.egg')
        # model.setPos(-0.5, -0.5, -0.5)
        # model.flattenLight()
        # shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))
        # for i in range(1):
        #     node = BulletRigidBodyNode('Box')
        #     node.setMass(1.0)
        #     node.addShape(shape)
        #     np = self.render.attachNewNode(node)
        #     np.setPos(0, 0, 2 + i * 2)
        #     self.world.attachRigidBody(node)
        #     model.copyTo(np)
    def topPlank(self):
        # Plane
        shape = BulletBoxShape(Vec3(1, 0.1, 0.1))
        node = BulletRigidBodyNode('Box')
        node.setMass(1)
        node.addShape(shape)
        np = self.render.attachNewNode(node)
        np.setPos(0, 0, 3)
        np.setR(0)
        self.world.attachRigidBody(node)



coin = coins()
coin.run()
