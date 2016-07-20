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


def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1),
                        pos=(1.3, -0.95), align=TextNode.ARight, scale=.07)


def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale=.05)

def addCoinScore(score):
    return OnscreenText(text="Coins:" + str(score), style=1, fg=(1, 1, 1, 1),
                        pos=(0, 0.95), align=TextNode.ALeft, scale=.05)

class EccoGame(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        #base.setBackgroundColor(0, 0, 0)

        self.sizescale = 0.6
        self.setupWorld()
        self.setupFloor()
        self.setupCharacter()

        #self.title = addTitle(" ")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[Left key]: Turn Ecco Left")
        self.inst3 = addInstructions(0.85, "[Right key]: Turn Ecco Right")
        self.inst4 = addInstructions(0.80, "[Up key]: Jump Ecco")

        inputState.watchWithModifiers('esc', 'escape')
        inputState.watchWithModifiers('w', 'w')
        inputState.watchWithModifiers('arrow_left', 'arrow_left')
        inputState.watchWithModifiers('arrow_right', 'arrow_right')
        inputState.watchWithModifiers('pause', 'p')
        inputState.watchWithModifiers('space', 'space')
        inputState.watchWithModifiers('arrow_up', 'arrow_up')

        inputState.watchWithModifiers('cam-left', 'z')
        inputState.watchWithModifiers('cam-right', 'x')
        inputState.watchWithModifiers('cam-forward', 'c')
        inputState.watchWithModifiers('cam-backward', 'v')

        taskMgr.add(self.update, "update")

        # Game state variables
        self.isMoving = False

        # Create a floater object, which floats 2 units above ecco.  We
        # use this as a target for the camera to look at.

        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.characterNP)
        self.floater.setZ(2.0)

        # Set up the camera
        self.disableMouse()
        self.camera.setPos(self.characterNP.getX(), self.characterNP.getY() + 10, 5)
        self.setupSound()

        # coins variables
        self.coinsCollected = 0
        self.dictOfCoins = {}
        self.coins = []

        # Set up Coins as Collectables
        self.setupCoins()

        #Set up Floaters with Coins
        self.setupFloaters()

        #Set up Obstacles
        self.setupObstacles()


    def update(self, task):
        self.setupSky()
        self.setUpCamera()
        self.processInput()
        self.processContacts()
        #addCoinScore(self.coinsCollected)
        self.coinScoreDisplay()
        self.checkIfEccoDied()
        dt = globalClock.getDt()
        #self.world.doPhysics(dt, 10, 1 / 180.0)
        self.world.doPhysics(dt, 10, 1 / 230.0)
        return task.cont

    def setupWorld(self):
        # create bullet world
        self.debugNP = self.render.attachNewNode(BulletDebugNode('Debug'))
        self.debugNP.show()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())

    def setupSky(self):

        self.milkyWayNp = render.attachNewNode('milkyway')
        self.milkyWay_2Np = render.attachNewNode('milkyway_2')
        self.marsNp = render.attachNewNode('mars')
        self.sunNp = render.attachNewNode('sun')

        # Load the model for the sky
        #self.sky = loader.loadModel("models/sky/solar_sky_sphere")
        self.sky = loader.loadModel("models/sky/solar_sky_sphere")
        # Load the texture for the sky.
        self.sky_tex = loader.loadTexture("models/sky/stars_1k_tex.jpg")
        # Set the sky texture to the sky model
        self.sky.setTexture(self.sky_tex, 1)
        # Parent the sky model to the render node so that the sky is rendered
        self.sky.reparentTo(self.render)
        # Scale the size of the sky.
        self.sky.setScale(15000)
        x = 0.005
        y = 1700.0
        z = 0.0
        self.sky.setPos(x, y, 0)

        # #milkyway 1
        self.milkyWay = loader.loadModel("models/sky/planet_sphere")
        self.milkWay_tex = loader.loadTexture("models/sky/milkyway_tex.jpg")
        self.milkyWay.setTexture(self.milkWay_tex, 1)
        self.milkyWay.reparentTo(self.milkyWayNp)
        self.milkyWay.setScale(200)
        self.milkyWay.setPos(x + 2000, y + 10000, z - 500)

        # #milkyway 2
        self.milkyWay_2 = loader.loadModel("models/sky/planet_sphere")
        self.milkWay_2_tex = loader.loadTexture("models/sky/milkyway_2_tex.jpg")
        self.milkyWay_2.setTexture(self.milkWay_2_tex, 1)
        self.milkyWay_2.reparentTo(self.milkyWay_2Np)
        self.milkyWay_2.setScale(400)
        self.milkyWay_2.setPos(x - 3000, y + 10000, z + 500)

        # #sun
        self.sun = loader.loadModel("models/sky/planet_sphere")
        self.sun_tex = loader.loadTexture("models/sky/sun_2_tex.jpg")
        self.sun.setTexture(self.sun_tex, 1)
        self.sun.reparentTo(self.sunNp)
        self.sun.setScale(600)
        self.sun.setPos(x + 1000, y + 10000, z + 1000)
        #
        # # Load Mars
        self.mars = loader.loadModel("models/sky/planet_sphere")
        self.mars_tex = loader.loadTexture("models/sky/mars_1k_tex.jpg")
        self.mars.setTexture(self.mars_tex, 1)
        self.mars.reparentTo(self.marsNp)
        self.mars.setScale(200)
        self.mars.setPos(x + 3000, y + 10000, z + 500)


    def setupSound(self):
        # Set up sound
        mySound = base.loader.loadSfx("sounds/Farm Morning.ogg")
        #self.footsteps = base.loader.loadSfx("sounds/Footsteps_on_Cement-Tim_Fryer.wav")
        mySound.play()
        mySound.setVolume(3.0)
        mySound.setLoop(True)

    def setupFloor(self):
        # Floor
        # shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        # floorNP = self.render.attachNewNode(BulletRigidBodyNode('Floor'))
        # floorNP.node().addShape(shape)
        # floorNP.setPos(0, 0, -300)
        # floorNP.setCollideMask(BitMask32.allOn())
        # self.world.attachRigidBody(floorNP.node())

        #origin = Point3(2, 0, 0)
        size = Vec3(10, 5000, 1)
        shape = BulletBoxShape(size * 0.55)
        stairNP = self.render.attachNewNode(BulletRigidBodyNode('Floor'))
        stairNP.node().addShape(shape)
        stairNP.setPos(0, 0, 0)
        stairNP.setCollideMask(BitMask32.allOn())

        modelNP = loader.loadModel('models/box.egg')
        modelNP.reparentTo(stairNP)
        #modelNP.setPos(0, 0, 0)
        modelNP.setPos(-size.x / 2.0, -size.y / 2.0, -size.z / 2.0)
        modelNP.setScale(size)
        self.world.attachRigidBody(stairNP.node())

    def setupFloaters(self):
        size = Vec3(5.5, 5.5, 0.3)
        for i in range(5):
            #randX = random.uniform(-3.5, 3.5)
            randX = random.randrange(-8, 8, 6)
            randY = random.randint(0, 1000)
            shape = BulletBoxShape(size * 0.55)
            node = BulletRigidBodyNode('Floater')
            node.setMass(0)
            node.addShape(shape)
            np = self.render.attachNewNode(node)
            #np.setPos(9, 30, 3)
            np.setPos(randX, randY, 4)
            np.setR(0)
            self.world.attachRigidBody(node)

            dummyNp = self.render.attachNewNode('milkyway')
            dummyNp.setPos(randX, randY, 4)

            modelNP = loader.loadModel('models/box.egg')
            modelNP_tex = loader.loadTexture("models/sky/moon_tex.jpg")
            modelNP.setTexture(modelNP_tex, 1)
            modelNP.reparentTo(dummyNp)
            modelNP.setPos(-1, 0, -1)
            modelNP.setPos(-size.x / 2.0, -size.y / 2.0, -size.z / 2.0)
            modelNP.setScale(size)
            dummyNp.hprInterval(2.5, Vec3(360, 0, 0)).loop()

            # Put A Coin On the Floater

            shape = BulletSphereShape(0.75)
            coinNode = BulletGhostNode('FloaterCoin-' + str(i))
            coinNode.addShape(shape)
            np = self.render.attachNewNode(coinNode)
            np.setCollideMask(BitMask32.allOff())
            # np.setPos(randX, randY, 2)
            np.setPos(randX, randY, 5.0)

            # Adding sphere model
            sphereNp = loader.loadModel('models/smiley.egg')
            sphereNp_tex = loader.loadTexture("models/sky/coin_2_tex.jpg")
            sphereNp.setTexture(sphereNp_tex, 1)
            sphereNp.reparentTo(np)
            sphereNp.setScale(0.85)

            self.world.attachGhost(coinNode)
            self.coins.append(coinNode)
            print "node name:" + str(coinNode.getName())

    def setupCharacter(self):
        # Character
        h = 10.75
        w = 1
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)

        self.character = BulletCharacterControllerNode(shape, 0, 'Player')
        #self.character.setMass(1.0)
        self.characterNP = self.render.attachNewNode(self.character)
        self.characterNP.setPos(0, 0, 5)
        #self.characterNP.setH(45)
        self.characterNP.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character)

        self.ecco = Actor('models/lack.egg', {
            'run': 'models/lack-run.egg',
            'jump': 'models/lack-jump.egg',
            'damage': 'models/lack-damage.egg'})

        self.ecco.reparentTo(self.characterNP)
        self.ecco.setScale(0.3048)
        self.ecco.setH(180)
        self.ecco.setPos(0, 0, -1)


    def setUpCamera(self):
        # If the camera is too far from ecco, move it closer.
        # If the camera is too close to ecco, move it farther.
        camvec = self.characterNP.getPos() - self.camera.getPos()
        camvec.setZ(0.0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.camera.setPos(self.camera.getPos() + camvec * (camdist - 60))
            camdist = 10.0
        if camdist < 5.0:
            self.camera.setPos(self.camera.getPos() - camvec * (5 - camdist))
            camdist = 5.0
        self.camera.lookAt(self.floater)


    def processInput(self):
        dt = globalClock.getDt()
        startpos = self.ecco.getPos()
        speed = Vec3(0, 0, 0)
        omega = 0.0
        if inputState.isSet('esc'): sys.exit()
        if inputState.isSet('w'): speed.setY(20.0)
        if inputState.isSet('arrow_left'):
            speed.setX(-35.0)
            #omega = 120.0
        if inputState.isSet('arrow_right'):
            speed.setX(35.0)
            #omega = -120.0
        if inputState.isSet('space'): self.jump()
        if inputState.isSet('arrow_up'): self.jump()
        if inputState.isSet('cam-left'): self.camera.setX(self.camera, -20 * dt)
        if inputState.isSet('cam-right'): self.camera.setX(self.camera, +20 * dt)
        if inputState.isSet('cam-forward'): self.camera.setY(self.camera, -200 * dt)
        if inputState.isSet('cam-backward'): self.camera.setY(self.camera, +200 * dt)

        #Make Ecco run
        if self.isMoving is False:
            self.ecco.loop("run")
            self.isMoving = True
        #speed.setY(20.0)

        # self.footsteps.play()
        # self.footsteps.setVolume(150)
        #self.character.setAngularMovement(omega)
        self.character.setLinearMovement(speed, True)
    i = 0
    def jump(self):
        self.character.setMaxJumpHeight(5.0)
        self.character.setJumpSpeed(10.0)
        # self.i = self.i + 1
        # print "jump executing" + str(self.i)
        # self.character.doJump()
        if self.character.isOnGround():
            self.i = self.i + 1
            print "jump executing" + str(self.i)
            self.character.doJump()


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
        for i in range(10):
            randX = random.uniform(-3.5, 3.5)
            randY = random.randint(0, 1000)
            shape = BulletSphereShape(0.75)
            coinNode = BulletGhostNode('Coin-' + str(i))
            coinNode.addShape(shape)
            np = self.render.attachNewNode(coinNode)
            np.setCollideMask(BitMask32.allOff())
            np.setPos(randX, randY, 2)

            #Adding sphere model
            sphereNp = loader.loadModel('models/smiley.egg')
            sphereNp_tex = loader.loadTexture("models/sky/coin_2_tex.jpg")
            sphereNp.setTexture(sphereNp_tex, 1)
            sphereNp.reparentTo(np)
            sphereNp.setScale(0.85)

            self.world.attachGhost(coinNode)
            self.coins.append(coinNode)
            print "node name:"+ str(coinNode.getName())

    def processContacts(self):
        # self.testWithEveryBody()

        for coin in self.coins:
            self.testWithSingleBody(coin)
        #     for key in self.dictOfCoins:
        #         x = set(key)
        #         #print "length of x" + str(len(x) - 1)
        #         #self.coinsCollected = len(x) - 1
        # for key in self.dictOfCoins:
        #     x = set(key)
        #     print "Value of key in dictOfCoins:"+ str(x)
        # print "Value of dictOfCoins:"
        #print self.dictOfCoins
        self.coinsCollected = len(self.dictOfCoins)
        #print "Value of coinsCollected:"+str(self.coinsCollected)
        #self.CoinsScore = addCoinScore(str(self.coinsCollected))
        #print self.coinsCollected

    def testWithSingleBody(self, secondNode):
        # test sphere for contacts with secondNode
        contactResult = self.world.contactTestPair(self.character, secondNode)  # returns a BulletContactResult object

        if contactResult.getNumContacts() > 0:
            for contact in contactResult.getContacts():
                cp = contact.getManifoldPoint()
                node0 = contact.getNode0()
                node1 = contact.getNode1()
                print node0.getName(), node1.getName()
                self.dictOfCoins[node1.getName()] = 1
                print "Removing:" + str(node1.getName())
                np = self.render.find(node1.getName())
                np.node().removeAllChildren()
                self.world.removeGhost(np.node())

    def setupObstacles(self):
        # Obstacle
        origin = Point3(2, 0, 0)
        size = Vec3(3, 4.75, 3.5)
        shape = BulletBoxShape(size * 0.55)
        for i in range(3):
            randX = random.uniform(-3.5, 3.5)
            randY = random.randint(0, 1000)
            pos = origin + size * i
            #pos.setY(0)
            ObstacleNP = self.render.attachNewNode(BulletRigidBodyNode('Obstacle%i' % i))
            ObstacleNP.node().addShape(shape)
            #ObstacleNP.setPos(randX, randY, 2)
            ObstacleNP.setPos(randX, randY, 2)
            ObstacleNP.setCollideMask(BitMask32.allOn())

            modelNP = loader.loadModel('models/box.egg')
            modelNP_tex = loader.loadTexture("models/sky/milkyway_tex.jpg")
            modelNP.setTexture(modelNP_tex, 1)
            modelNP.reparentTo(ObstacleNP)
            # modelNP.setPos(0, 0, 0)
            modelNP.setPos(-size.x / 2.0, -size.y / 2.0, -size.z / 2.0)
            modelNP.setScale(size)
            self.world.attachRigidBody(ObstacleNP.node())

        size_2 = Vec3(3, 4.75, 1.5)
        for i in range(3):
            randX = random.uniform(-3.5, 3.5)
            randY = random.randint(0, 1000)
            pos = origin + size_2 * i
            pos.setY(0)
            ObstacleNP = self.render.attachNewNode(BulletRigidBodyNode('Obstacle%i' % i))
            ObstacleNP.node().addShape(shape)
            # ObstacleNP.setPos(randX, randY, 2)
            ObstacleNP.setPos(randX, randY, 2)
            ObstacleNP.setCollideMask(BitMask32.allOn())

            modelNP = loader.loadModel('models/box.egg')
            modelNP_tex = loader.loadTexture("models/sky/moon_1k_tex.jpg")
            modelNP.setTexture(modelNP_tex, 1)
            modelNP.reparentTo(ObstacleNP)
            # modelNP.setPos(0, 0, 0)
            modelNP.setPos(-size_2.x / 2.0, -size_2.y / 2.0, -size_2.z / 2.0)
            modelNP.setScale(size_2)
            self.world.attachRigidBody(ObstacleNP.node())

    def checkIfEccoDied(self):
        pos = self.characterNP.getPos()
        if pos.getZ() < -50.0:
            sys.exit(1)

    def coinScoreDisplay(self):
        textNp = self.aspect2d.find('coin-score')
        textNp.node().clearText()
        textNp.node().setText(str("Coins: " + str(self.coinsCollected)))



simulation = EccoGame()
simulation.run()
