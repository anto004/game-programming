
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, BitMask32
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletGhostNode
from panda3d.bullet import BulletWorld
import random
from pandac.PandaModules import TextNode, loadPrcFileData
loadPrcFileData('', 'bullet-enable-contact-events true')

class Floaters():
    world = BulletWorld()

    def __init__(self, world, pos = Vec3(0, 0, 0), name = "Floater"):
        self.world = world
        self.pos = pos
        self.name = name


    def setupFloaters(self, world):
        size = Vec3(3.5, 5.5, 0.3)
        for i in range(5):
            randX = random.randrange(-6, 6, 5)
            randY = random.randint(0, 1000)
            shape = BulletBoxShape(size * 0.55)
            node = BulletRigidBodyNode('Floater')
            node.setMass(0)
            node.addShape(shape)
            self.np = self.render.attachNewNode(node)
            # np.setPos(9, 30, 3)
            np.setPos(randX, randY, 6)
            np.setR(0)
            world.attachRigidBody(node)

            dummyNp = self.render.attachNewNode('milkyway')
            dummyNp.setPos(randX, randY, 6)

            modelNP = loader.loadModel('models/box.egg')
            modelNP_tex = loader.loadTexture("models/sky/moon_tex.jpg")
            modelNP.setTexture(modelNP_tex, 1)
            modelNP.reparentTo(dummyNp)
            modelNP.setPos(-1, 0, -1)
            modelNP.setPos(-size.x / 2.0, -size.y / 2.0, -size.z / 2.0)
            modelNP.setScale(size)
            # dummyNp.hprInterval(2.5, Vec3(360, 0, 0)).loop()

            # Put A Coin On the Floater
            shape = BulletSphereShape(0.75)
            coinNode = BulletGhostNode('FloaterCoin-' + str(i))
            coinNode.addShape(shape)
            np = self.render.attachNewNode(coinNode)
            np.setCollideMask(BitMask32.allOff())
            # np.setPos(randX, randY, 2)
            np.setPos(randX, randY, 7.0)

            # Adding sphere model
            sphereNp = loader.loadModel('models/smiley.egg')
            sphereNp_tex = loader.loadTexture("models/sky/coin_2_tex.jpg")
            sphereNp.setTexture(sphereNp_tex, 1)
            sphereNp.reparentTo(np)
            sphereNp.setScale(0.85)
            sphereNp.hprInterval(1.5, Vec3(360, 0, 0)).loop()

            world.attachGhost(coinNode)
            world.coins.append(coinNode)
            print "node name:" + str(coinNode.getName())

    # Controller class
    # floaters = []
    # floater = Floater(bullterWorld, pos = Vex3(20, 20, 10), name = "Floater-1")
    # floaters.append(floater)

    # for floater in floaters:
            # floater.np.getPos()
            # render.removeNode(floater.np.node())