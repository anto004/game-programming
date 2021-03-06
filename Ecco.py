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
from direct.gui.DirectGui import *
from pandac.PandaModules import TextNode, loadPrcFileData
loadPrcFileData('', 'bullet-enable-contact-events true')

def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1),
                        pos=(1.3, -0.95), align=TextNode.ARight, scale=.07)


def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale=.05)

def levelDisplay(level):
        return OnscreenText(text=level, style=1, fg=(255, 102, 102, 1),
                        pos=(0.9, 0.9), align=TextNode.ABoxedCenter, scale=.08)

#CONTRIBUTORS
#models contributed by Howard Li and Lewis Chen
#sound effects - www.SoundBible.com, www.indieGameMusic.com
#texture images - www.dreamstime.com
#fonts - www.webpagepublicity.com

class EccoGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setBackgroundColor(0, 0, 0)
        game_title = "ECCO"
        titleN = TextNode('game-title')
        font = loader.loadFont("font/Caveman.ttf")
        titleN.setFont(font)
        titleN.setText(game_title)
        titleN.setTextColor(1, 1, 1, 1)
        titleN.setSlant(0.1)
        titleN.setShadow(0.05)
        titleN.setShadowColor(0, 0, 200, 1)
        titleN.setFrameColor(0, 0, 255, 1)
        titleN.setFrameLineWidth(5.0)
        textNodePath = self.aspect2d.attachNewNode(titleN)
        textNodePath.setPos(-0.4, 1.5, 0.5)
        textNodePath.setScale(0.2)

        self.level1Button = DirectButton(text=("Level 1"), scale=.1, pos=(0, 0, 0.2), command=self.level1)
        self.level2Button = DirectButton(text=("Level 2"), scale=.1, pos=(0, 0, 0), command=self.level2)


    def level1(self):
        titleNp = self.aspect2d.find('game-title')
        titleNp.removeNode()
        self.level1Button.destroy()
        self.level2Button.destroy()

        self.sizescale = 0.6
        self.setupWorld()
        self.setupSky()
        self.setupFloor()
        self.setupCharacter()

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

        # display framerate
        self.setFrameRateMeter(True)

        # Set up the camera
        self.disableMouse()
        self.camera.setPos(self.characterNP.getX(), self.characterNP.getY() - 30, 4)
        self.setupSound()

        # coins variables
        self.coinsCollected = 0
        self.dictOfCoins = {}
        self.coins = []

        # Set up Coins as Collectables
        self.setupCoins()

        # Set up Obstacles
        self.setupObstacles()

        # Setup Level Display
        self.setupLevelDisplay()

        self.counter = 0

    def setupLevelDisplay(self):
        LEVEL_1 = "Level 1"
        levelDisplay(LEVEL_1)
        levelN = TextNode('level-display')
        levelN.setText(LEVEL_1)
        font = loader.loadFont("font/Caveman.ttf")
        levelN.setFont(font)
        levelN.setTextColor(1, 1, 1, 1)
        levelN.setSlant(0.1)
        levelN.setShadow(0.05)
        levelN.setShadowColor(255, 0, 0, 1)
        textNodePath = self.aspect2d.attachNewNode(levelN)
        textNodePath.setPos(-0.45, 0, 0)
        textNodePath.setScale(0.2)


    def update(self, task):
        dt = globalClock.getDt()
        self.pos = self.characterNP.getPos()
        self.counter = self.counter + 1
        if self.counter == 150:
            levelNp = self.aspect2d.find('level-display')
            levelNp.removeNode()
        self.setUpCamera()
        self.processInput(dt)
        self.processContacts()
        self.coinScoreDisplay()
        self.checkIfEccoDied()
        self.world.doPhysics(dt, 10, 1 / 230.0)
        return task.cont

    def setupWorld(self):
        # create bullet world
        self.debugNP = self.render.attachNewNode(BulletDebugNode('Debug'))
        #self.debugNP.show()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())

    def setupSky(self):

        self.milkyWayNp = render.attachNewNode('milkyway')
        self.milkyWay_2Np = render.attachNewNode('milkyway_2')
        self.marsNp = render.attachNewNode('mars')
        self.sunNp = render.attachNewNode('sun')

        # Load the model for the sky
        # self.sky = loader.loadModel("models/sky/solar_sky_sphere")
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

        # milkyway 2
        self.milkyWay_2 = loader.loadModel("models/sky/planet_sphere")
        self.milkWay_2_tex = loader.loadTexture("models/sky/milkyway_2_tex.jpg")
        self.milkyWay_2.setTexture(self.milkWay_2_tex, 1)
        self.milkyWay_2.reparentTo(self.milkyWay_2Np)
        self.milkyWay_2.setScale(400)
        self.milkyWay_2.setPos(x - 3000, y + 10000, z + 500)

        # sun
        self.sun = loader.loadModel("models/sky/planet_sphere")
        self.sun_tex = loader.loadTexture("models/sky/sun_2_tex.jpg")
        self.sun.setTexture(self.sun_tex, 1)
        self.sun.reparentTo(self.sunNp)
        self.sun.setScale(600)
        self.sun.setPos(x + 1000, y + 10000, z + 1000)
        #
        # Load Mars
        self.mars = loader.loadModel("models/sky/planet_sphere")
        self.mars_tex = loader.loadTexture("models/sky/mars_1k_tex.jpg")
        self.mars.setTexture(self.mars_tex, 1)
        self.mars.reparentTo(self.marsNp)
        self.mars.setScale(200)
        self.mars.setPos(x + 3000, y + 10000, z + 500)

    def setupSound(self):
        # Set up sound
        mySound = base.loader.loadSfx("sounds/Farm Morning.ogg")
        mySound.play()
        mySound.setVolume(3.0)
        mySound.setLoop(True)
        footsteps = base.loader.loadSfx("sounds/Footsteps_on_Cement-Tim_Fryer.wav")
        footsteps.play()
        footsteps.setVolume(0.8)
        footsteps.setLoop(True)
        self.jumpSound = base.loader.loadSfx("sounds/Jump-SoundBible.com-1007297584.wav")
        self.jumpSound.setVolume(0.2)
        self.collectSound = base.loader.loadSfx("sounds/pin_dropping-Brian_Rocca-2084700791.wav")
        self.gameOverSound = base.loader.loadSfx("sounds/Bike Horn-SoundBible.com-602544869.wav")
        self.levelCompleteSound = base.loader.loadSfx("sounds/Ta Da-SoundBible.com-1884170640.wav")



    def setupFloor(self):
        size = Vec3(7.5, 3000, 1.81818)
        shape = BulletBoxShape(size * 0.55)
        # shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        node = BulletRigidBodyNode('Box-Floor')
        node.addShape(shape)
        node.setMass(0)
        stairNP = self.render.attachNewNode(node)
        stairNP.setPos(0, 0, 0)
        stairNP.setCollideMask(BitMask32.allOn())
        self.world.attachRigidBody(stairNP.node())

        modelNP = loader.loadModel('models/box.egg')
        modelNP.reparentTo(stairNP)
        modelNP.setPos(-size.x / 2.0, -size.y / 2.0, -size.z / 2.0)
        modelNP.setScale(size)


    def setupCharacter(self):
        # Character
        h = 1.75
        w = 0.4
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)
        self.character = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.character.setGravity(35)
        self.characterNP = self.render.attachNewNode(self.character)
        self.characterNP.setPos(0, 10, 5)
        self.characterNP.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character)

        self.ecco = Actor('ralph-models/ralph.egg.pz', {
            'run': 'ralph-models/ralph-run.egg',
            'jump': 'ralph/ralph-run.egg',
            'damage': 'models/lack-damage.egg'})
        self.ecco.reparentTo(self.characterNP)
        self.ecco.setScale(0.7048)
        self.ecco.setH(180)

    def setUpCamera(self):
        # If the camera is too far from ecco, move it closer.
        # If the camera is too close to ecco, move it farther.
        camvec = self.characterNP.getPos() - self.camera.getPos()
        camvec.setZ(0.0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.camera.setPos(self.camera.getPos() + camvec * (camdist - 40))
            camdist = 10.0
        if camdist < 5.0:
            self.camera.setPos(self.camera.getPos() - camvec * (35 - camdist))
            camdist = 5.0

    def processInput(self, dt):
        speed = Vec3(0, 0, 0)
        if inputState.isSet('esc'): sys.exit()
        if inputState.isSet('w'): speed.setY(35.0)
        if inputState.isSet('arrow_left'): speed.setX(-35.0)
        if inputState.isSet('arrow_right'): speed.setX(35.0)
        if inputState.isSet('space'):
            self.jump()
            self.jumpSound.play()
        if inputState.isSet('arrow_up'):
            self.jump()
            self.jumpSound.play()
        if inputState.isSet('cam-left'): self.camera.setX(self.camera, -20 * dt)
        if inputState.isSet('cam-right'): self.camera.setX(self.camera, +20 * dt)
        if inputState.isSet('cam-forward'): self.camera.setY(self.camera, -200 * dt)
        if inputState.isSet('cam-backward'): self.camera.setY(self.camera, +200 * dt)

        # Make Ecco run
        if self.isMoving is False:
            self.ecco.loop("run")
            self.isMoving = True

        if self.pos.getY() > 1450.0:
            speed.setY(0.0)
        else:
            speed.setY(40.0)

        self.character.setLinearMovement(speed, True)

    def jump(self):
        self.character.setMaxJumpHeight(3.0)
        self.character.setJumpSpeed(25.0)
        self.character.doJump()

    def setupCoins(self):
        # display coins = 0
        textN = TextNode('coin-score')
        textN.setText(str("Coins: " + str(self.coinsCollected)))
        textN.setSlant(0.1)
        textNodePath = self.aspect2d.attachNewNode(textN)
        textNodePath.setPos(0, 0.95, 0.9)
        textNodePath.setScale(0.08)
        randNum = random.sample(range(0, 1500, 200), 6)

        # coins
        for i in range(6):
            randX = random.uniform(-3.0, 3.2)
            randY = float(randNum[i])
            shape = BulletSphereShape(0.3)
            coinNode = BulletGhostNode('Coin-' + str(i))
            coinNode.addShape(shape)
            np = self.render.attachNewNode(coinNode)
            np.setCollideMask(BitMask32.allOff())
            np.setPos(randX, randY, 2)

            # Adding sphere model
            sphereNp = loader.loadModel('models/smiley.egg')
            sphereNp_tex = loader.loadTexture("models/sky/coin_2_tex.jpg")
            sphereNp.setTexture(sphereNp_tex, 1)
            sphereNp.reparentTo(np)
            sphereNp.setScale(0.45)
            sphereNp.hprInterval(2.5, Vec3(360, 0, 0)).loop()

            self.world.attachGhost(coinNode)
            self.coins.append(coinNode)
            print "node name:" + str(coinNode.getName())

    def processContacts(self):
        for coin in self.coins:
            self.testWithSingleBody(coin)

        self.coinsCollected = len(self.dictOfCoins)

    def testWithSingleBody(self, secondNode):
        contactResult = self.world.contactTestPair(self.character, secondNode)

        if contactResult.getNumContacts() > 0:
            self.collectSound.play()
            for contact in contactResult.getContacts():
                cp = contact.getManifoldPoint()
                node0 = contact.getNode0()
                node1 = contact.getNode1()
                self.dictOfCoins[node1.getName()] = 1
                np = self.render.find(node1.getName())
                np.node().removeAllChildren()
                self.world.removeGhost(np.node())

    def setupObstacles(self):
        # Obstacle
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2.75, 1.5)
        shape = BulletBoxShape(size * 0.55)
        randNum1 = random.sample(range(0, 1500, 300), 3)
        randNum2 = random.sample(range(0, 1500, 500), 3)
        for i in range(2):
            randX = random.uniform(-3.5, 3.5)
            randY = float(randNum1[i])
            pos = origin + size * i
            ObstacleNP = self.render.attachNewNode(BulletRigidBodyNode('Obstacle%i' % i))
            ObstacleNP.node().addShape(shape)
            ObstacleNP.node().setMass(1.0)
            ObstacleNP.setPos(randX, randY, 3)
            ObstacleNP.setCollideMask(BitMask32.allOn())

            modelNP = loader.loadModel('models/box.egg')
            modelNP_tex = loader.loadTexture("models/sky/milkyway_tex.jpg")
            modelNP.setTexture(modelNP_tex, 1)
            modelNP.reparentTo(ObstacleNP)
            # modelNP.setPos(0, 0, 0)
            modelNP.setPos(-size.x / 2.0, -size.y / 2.0, -size.z / 2.0)
            modelNP.setScale(size)
            self.world.attachRigidBody(ObstacleNP.node())

        size_2 = Vec3(3, 2.75, 1.5)
        shape2 = BulletBoxShape(size_2 * 0.55)
        for i in range(2):
            randX = random.uniform(-3.5, 3.5)
            randY = float(randNum2[i])
            pos = origin + size_2 * i
            pos.setY(0)
            ObstacleNP = self.render.attachNewNode(BulletRigidBodyNode('ObstacleSmall%i' % i))
            ObstacleNP.node().addShape(shape2)
            ObstacleNP.node().setMass(1.0)
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
        print "position" + str(self.pos.getY())
        if self.pos.getZ() > -50.0 and self.pos.getZ() < 0.0:
            title = "Game Over"
            levelCompleteN = TextNode('ecco-died')
            font = loader.loadFont("font/Caveman.ttf")
            levelCompleteN.setFont(font)
            levelCompleteN.setText(title)
            levelCompleteN.setTextColor(1, 1, 1, 1)
            levelCompleteN.setSlant(0.1)
            levelCompleteN.setShadow(0.03)
            levelCompleteN.setShadowColor(0, 0, 200, 1)
            # levelN.setFrameAsMargin(0, 0, 0, 0)
            levelCompleteN.setFrameColor(200, 0, 0, 1)
            levelCompleteN.setFrameLineWidth(5.0)
            # textNp.node().setGlyphShift(1.0)
            textNodePath = self.aspect2d.attachNewNode(levelCompleteN)
            textNodePath.setPos(-0.9, 1.5, 0.5)
            textNodePath.setScale(0.2)
            if self.pos.getZ() < -49.0:
                self.gameOverSound.play()

        elif self.pos.getZ() < -50.0:
            if self.gameOverSound.status() != self.gameOverSound.PLAYING:
                sys.exit(1)

        elif self.pos.getY() > 1300.0:
            title = "Level 1 \n Complete"
            levelCompleteN = TextNode('level-complete')
            font = loader.loadFont("font/Caveman.ttf")
            levelCompleteN.setFont(font)
            levelCompleteN.setText(title)
            levelCompleteN.setTextColor(1, 1, 1, 1)
            levelCompleteN.setSlant(0.1)
            levelCompleteN.setShadow(0.03)
            levelCompleteN.setShadowColor(0, 0, 200, 1)
            # levelN.setFrameAsMargin(0, 0, 0, 0)
            levelCompleteN.setFrameColor(200, 0, 0, 1)
            levelCompleteN.setFrameLineWidth(5.0)
            # textNp.node().setGlyphShift(1.0)
            textNodePath = self.aspect2d.attachNewNode(levelCompleteN)
            textNodePath.setPos(-0.6, 1.5, 0.5)
            textNodePath.setScale(0.2)
            if self.levelCompleteSound.status() != self.levelCompleteSound.PLAYING:
                self.levelCompleteSound.play()
        else:
            pass


    def coinScoreDisplay(self):
        textNp = self.aspect2d.find('coin-score')
        textNp.node().clearText()
        textNp.node().setText(str("Coins: " + str(self.coinsCollected)))


    #Level 2
    def level2(self):
        titleNp2 = self.aspect2d.find('game-title')
        titleNp2.removeNode()
        self.level1Button.destroy()
        self.level2Button.destroy()

        self.sizescale2 = 0.6
        self.setupWorld2()
        self.setupSky2()
        self.setupFloor2()
        self.setupCharacter2()

        # self.title = addTitle(" ")
        self.inst12 = addInstructions(0.95, "[ESC]: Quit")
        self.inst22 = addInstructions(0.90, "[Left key]: Turn Ecco Left")
        self.inst32 = addInstructions(0.85, "[Right key]: Turn Ecco Right")
        self.inst42 = addInstructions(0.80, "[Up key]: Jump Ecco")

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

        taskMgr.add(self.update2, "update")

        # Game state variables
        self.isMoving2 = False


        # display framerate
        self.setFrameRateMeter(True)

        # Set up the camera
        self.disableMouse()
        self.camera.setPos(self.characterNP2.getX(), self.characterNP2.getY() - 30, 4)
        self.setupSound2()

        # coins variables
        self.coinsCollected2 = 0
        self.dictOfCoins2 = {}
        self.coins2 = []

        # Set up Coins as Collectables
        self.setupCoins2()

        # Set up Floaters with coins
        self.setupFloaters2()

        # Set up Obstacles
        self.setupObstacles2()

        # Setup Level Display
        self.setupLevelDisplay2()

        self.counter2 = 0

    def setupLevelDisplay2(self):
        LEVEL_2 = "Level 2"
        levelDisplay(LEVEL_2)
        levelN = TextNode('level-display')
        levelN.setText(LEVEL_2)
        # www.webpagepublicity.com
        font = loader.loadFont("font/Caveman.ttf")
        levelN.setFont(font)
        levelN.setTextColor(1, 1, 1, 1)
        levelN.setSlant(0.1)
        levelN.setShadow(0.05)
        levelN.setShadowColor(255, 0, 0, 1)
        # levelN.setFrameAsMargin(0, 0, 0, 0)
        # levelN.setFrameColor(0, 0, 255, 1)
        # levelN.setFrameLineWidth(5.0)
        # # textNp.node().setGlyphShift(1.0)
        textNodePath = self.aspect2d.attachNewNode(levelN)
        textNodePath.setPos(-0.45, 0, 0)
        textNodePath.setScale(0.2)

    def update2(self, task):
        dt = globalClock.getDt()
        self.pos2 = self.characterNP2.getPos()
        self.counter2 = self.counter2 + 1
        if self.counter2 == 150:
            levelNp = self.aspect2d.find('level-display')
            levelNp.removeNode()
        self.setUpCamera2()
        self.processInput2(dt)
        self.processContacts2()
        self.coinScoreDisplay2()
        self.checkIfEccoDied2()
        self.world2.doPhysics(dt, 10, 1 / 230.0)
        return task.cont

    def setupWorld2(self):
        # create bullet world
        self.debugNP = self.render.attachNewNode(BulletDebugNode('Debug'))
        #self.debugNP.show()

        self.world2 = BulletWorld()
        self.world2.setGravity(Vec3(0, 0, -9.81))
        self.world2.setDebugNode(self.debugNP.node())

    def setupSky2(self):

        self.milkyWayNp = render.attachNewNode('milkyway')
        self.milkyWay_2Np = render.attachNewNode('milkyway_2')
        self.marsNp = render.attachNewNode('mars')
        self.sunNp = render.attachNewNode('sun')

        # Load the model for the sky
        # self.sky = loader.loadModel("models/sky/solar_sky_sphere")
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

        # milkyway 2
        self.milkyWay_2 = loader.loadModel("models/sky/planet_sphere")
        self.milkWay_2_tex = loader.loadTexture("models/sky/milkyway_2_tex.jpg")
        self.milkyWay_2.setTexture(self.milkWay_2_tex, 1)
        self.milkyWay_2.reparentTo(self.milkyWay_2Np)
        self.milkyWay_2.setScale(400)
        self.milkyWay_2.setPos(x - 3000, y + 10000, z + 500)

        # sun
        self.sun = loader.loadModel("models/sky/planet_sphere")
        self.sun_tex = loader.loadTexture("models/sky/sun_2_tex.jpg")
        self.sun.setTexture(self.sun_tex, 1)
        self.sun.reparentTo(self.sunNp)
        self.sun.setScale(600)
        self.sun.setPos(x + 1000, y + 10000, z + 1000)
        #
        # Load Mars
        self.mars = loader.loadModel("models/sky/planet_sphere")
        self.mars_tex = loader.loadTexture("models/sky/mars_1k_tex.jpg")
        self.mars.setTexture(self.mars_tex, 1)
        self.mars.reparentTo(self.marsNp)
        self.mars.setScale(200)
        self.mars.setPos(x + 3000, y + 10000, z + 500)

    def setUpCamera2(self):
        # If the camera is too far from ecco, move it closer.
        # If the camera is too close to ecco, move it farther.
        camvec = self.characterNP2.getPos() - self.camera.getPos()
        camvec.setZ(0.0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.camera.setPos(self.camera.getPos() + camvec * (camdist - 40))
            camdist = 10.0
        if camdist < 5.0:
            self.camera.setPos(self.camera.getPos() - camvec * (35 - camdist))
            camdist = 5.0

    def setupSound2(self):
        # Set up sound
        mySound = base.loader.loadSfx("sounds/Farm Morning.ogg")
        mySound.play()
        mySound.setVolume(3.0)
        mySound.setLoop(True)
        footsteps = base.loader.loadSfx("sounds/Footsteps_on_Cement-Tim_Fryer.wav")
        footsteps.play()
        footsteps.setVolume(0.8)
        footsteps.setLoop(True)
        self.jumpSound2 = base.loader.loadSfx("sounds/Jump-SoundBible.com-1007297584.wav")
        self.jumpSound2.setVolume(0.2)
        self.collectSound2 = base.loader.loadSfx("sounds/pin_dropping-Brian_Rocca-2084700791.wav")
        self.gameOverSound2 = base.loader.loadSfx("sounds/Bike Horn-SoundBible.com-602544869.wav")
        self.levelCompleteSound2 = base.loader.loadSfx("sounds/Ta Da-SoundBible.com-1884170640.wav")

    def setupFloor2(self):
        size = Vec3(7.5, 3000, 1.81818)
        shape = BulletBoxShape(size * 0.55)
        # shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        node = BulletRigidBodyNode('Box-Floor')
        node.addShape(shape)
        node.setMass(0)
        stairNP = self.render.attachNewNode(node)
        stairNP.setPos(0, 0, 0)
        stairNP.setCollideMask(BitMask32.allOn())
        self.world2.attachRigidBody(stairNP.node())

        modelNP = loader.loadModel('models/box.egg')
        modelNP.reparentTo(stairNP)
        modelNP.setPos(-size.x / 2.0, -size.y / 2.0, -size.z / 2.0)
        modelNP.setScale(size)


    def setupCharacter2(self):
        # Character
        h = 1.75
        w = 0.4
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)
        self.character2 = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.character2.setGravity(35)
        self.characterNP2 = self.render.attachNewNode(self.character2)
        self.characterNP2.setPos(0, 10, 5)
        self.characterNP2.setCollideMask(BitMask32.allOn())
        self.world2.attachCharacter(self.character2)

        self.ecco2 = Actor('ralph-models/ralph.egg.pz', {
            'run': 'ralph-models/ralph-run.egg',
            'jump': 'ralph/ralph-run.egg',
            'damage': 'models/lack-damage.egg'})
        self.ecco2.reparentTo(self.characterNP2)
        self.ecco2.setScale(0.7048)
        self.ecco2.setH(180)


    def processInput2(self, dt):
        speed = Vec3(0, 0, 0)
        if inputState.isSet('esc'): sys.exit()
        if inputState.isSet('w'): speed.setY(35.0)
        if inputState.isSet('arrow_left'): speed.setX(-35.0)
        if inputState.isSet('arrow_right'): speed.setX(35.0)
        if inputState.isSet('space'):
            self.jump2()
            self.jumpSound2.play()
        if inputState.isSet('arrow_up'):
            self.jump2()
            self.jumpSound2.play()
        if inputState.isSet('cam-left'): self.camera.setX(self.camera, -20 * dt)
        if inputState.isSet('cam-right'): self.camera.setX(self.camera, +20 * dt)
        if inputState.isSet('cam-forward'): self.camera.setY(self.camera, -200 * dt)
        if inputState.isSet('cam-backward'): self.camera.setY(self.camera, +200 * dt)

        # Make Ecco run
        if self.isMoving2 is False:
            self.ecco2.loop("run")
            self.isMoving2 = True

        if self.pos2.getY() > 1450.0:
            speed.setY(0.0)
        else:
            speed.setY(40.0)

        self.character2.setLinearMovement(speed, True)

    def jump2(self):
        self.character2.setMaxJumpHeight(3.0)
        self.character2.setJumpSpeed(25.0)
        self.character2.doJump()

    def setupCoins2(self):
        # display coins = 0
        textN = TextNode('coin-score')
        textN.setText(str("Coins: " + str(self.coinsCollected2)))
        textN.setSlant(0.1)
        textNodePath = self.aspect2d.attachNewNode(textN)
        textNodePath.setPos(0, 0.95, 0.9)
        textNodePath.setScale(0.08)
        randNum = random.sample(range(0, 1500, 200), 6)

        # coins
        for i in range(6):
            randX = random.uniform(-3.0, 3.2)
            randY = float(randNum[i])
            shape = BulletSphereShape(0.3)
            coinNode = BulletGhostNode('Coin-' + str(i))
            coinNode.addShape(shape)
            np = self.render.attachNewNode(coinNode)
            np.setCollideMask(BitMask32.allOff())
            np.setPos(randX, randY, 2)

            # Adding sphere model
            sphereNp = loader.loadModel('models/smiley.egg')
            sphereNp_tex = loader.loadTexture("models/sky/coin_2_tex.jpg")
            sphereNp.setTexture(sphereNp_tex, 1)
            sphereNp.reparentTo(np)
            sphereNp.setScale(0.45)
            sphereNp.hprInterval(2.5, Vec3(360, 0, 0)).loop()

            self.world2.attachGhost(coinNode)
            self.coins2.append(coinNode)
            print "node name:" + str(coinNode.getName())

    def setupObstacles2(self):
        # Obstacle
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2.75, 1.5)
        shape = BulletBoxShape(size * 0.55)
        randNum1 = random.sample(range(0, 1500, 300), 3)
        randNum2 = random.sample(range(0, 1500, 500), 3)
        for i in range(2):
            randX = random.uniform(-3.5, 3.5)
            randY = float(randNum1[i])
            pos = origin + size * i
            ObstacleNP = self.render.attachNewNode(BulletRigidBodyNode('Obstacle%i' % i))
            ObstacleNP.node().addShape(shape)
            ObstacleNP.node().setMass(1.0)
            ObstacleNP.setPos(randX, randY, 3)
            ObstacleNP.setCollideMask(BitMask32.allOn())

            modelNP = loader.loadModel('models/box.egg')
            modelNP_tex = loader.loadTexture("models/sky/milkyway_tex.jpg")
            modelNP.setTexture(modelNP_tex, 1)
            modelNP.reparentTo(ObstacleNP)
            # modelNP.setPos(0, 0, 0)
            modelNP.setPos(-size.x / 2.0, -size.y / 2.0, -size.z / 2.0)
            modelNP.setScale(size)
            self.world2.attachRigidBody(ObstacleNP.node())

        size_2 = Vec3(3, 2.75, 1.5)
        shape2 = BulletBoxShape(size_2 * 0.55)
        for i in range(2):
            randX = random.uniform(-3.5, 3.5)
            randY = float(randNum2[i])
            pos = origin + size_2 * i
            pos.setY(0)
            ObstacleNP = self.render.attachNewNode(BulletRigidBodyNode('ObstacleSmall%i' % i))
            ObstacleNP.node().addShape(shape2)
            ObstacleNP.node().setMass(1.0)
            ObstacleNP.setPos(randX, randY, 2)
            ObstacleNP.setCollideMask(BitMask32.allOn())

            modelNP = loader.loadModel('models/box.egg')
            modelNP_tex = loader.loadTexture("models/sky/moon_1k_tex.jpg")
            modelNP.setTexture(modelNP_tex, 1)
            modelNP.reparentTo(ObstacleNP)
            # modelNP.setPos(0, 0, 0)
            modelNP.setPos(-size_2.x / 2.0, -size_2.y / 2.0, -size_2.z / 2.0)
            modelNP.setScale(size_2)
            self.world2.attachRigidBody(ObstacleNP.node())

    def setupFloaters2(self):
        size = Vec3(3.5, 5.5, 0.3)
        randNum = random.sample(range(10, 1500, 500), 3)
        for i in range(3):
            randX = random.randrange(-2, 3, 10)
            randY = float(randNum[i])
            # randY = random.randint(1000, 1500)
            shape = BulletBoxShape(size * 0.55)
            node = BulletRigidBodyNode('Floater')
            node.setMass(0)
            node.addShape(shape)
            np = self.render.attachNewNode(node)
            # np.setPos(9, 30, 3)
            np.setPos(randX, randY, 6)
            np.setR(0)
            self.world2.attachRigidBody(node)

            dummyNp = self.render.attachNewNode('milkyway')
            dummyNp.setPos(randX, randY, 6)

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
            np.setPos(randX, randY, 7.0)

            # Adding sphere model
            sphereNp = loader.loadModel('models/smiley.egg')
            sphereNp_tex = loader.loadTexture("models/sky/coin_2_tex.jpg")
            sphereNp.setTexture(sphereNp_tex, 1)
            sphereNp.reparentTo(np)
            sphereNp.setScale(0.85)
            sphereNp.hprInterval(1.5, Vec3(360, 0, 0)).loop()

            self.world2.attachGhost(coinNode)
            self.coins2.append(coinNode)
            print "node name:" + str(coinNode.getName())

    def processContacts2(self):
        for coin in self.coins2:
            self.testWithSingleBody2(coin)

        self.coinsCollected2 = len(self.dictOfCoins2)

    def testWithSingleBody2(self, secondNode):
        contactResult = self.world2.contactTestPair(self.character2, secondNode)

        if contactResult.getNumContacts() > 0:
            self.collectSound2.play()
            for contact in contactResult.getContacts():
                cp = contact.getManifoldPoint()
                node0 = contact.getNode0()
                node1 = contact.getNode1()
                self.dictOfCoins2[node1.getName()] = 1
                np = self.render.find(node1.getName())
                np.node().removeAllChildren()
                self.world2.removeGhost(np.node())


    def checkIfEccoDied2(self):
        print "position" + str(self.pos2.getY())
        if self.pos2.getZ() > -50.0 and self.pos2.getZ() < 0.0:
            title = "Game Over"
            levelCompleteN = TextNode('ecco-died')
            font = loader.loadFont("font/Caveman.ttf")
            levelCompleteN.setFont(font)
            levelCompleteN.setText(title)
            levelCompleteN.setTextColor(1, 1, 1, 1)
            levelCompleteN.setSlant(0.1)
            levelCompleteN.setShadow(0.03)
            levelCompleteN.setShadowColor(0, 0, 200, 1)
            # levelN.setFrameAsMargin(0, 0, 0, 0)
            levelCompleteN.setFrameColor(200, 0, 0, 1)
            levelCompleteN.setFrameLineWidth(5.0)
            # textNp.node().setGlyphShift(1.0)
            textNodePath = self.aspect2d.attachNewNode(levelCompleteN)
            textNodePath.setPos(-0.9, 1.5, 0.5)
            textNodePath.setScale(0.2)
            if self.pos2.getZ() < -49.0:
                self.gameOverSound2.play()

        elif self.pos2.getZ() < -50.0:
            if self.gameOverSound2.status() != self.gameOverSound2.PLAYING:
                sys.exit(1)
        elif self.pos2.getY() > 1300.0:
            title = "Level 2 \n Complete"
            levelCompleteN = TextNode('level-complete')
            font = loader.loadFont("font/Caveman.ttf")
            levelCompleteN.setFont(font)
            levelCompleteN.setText(title)
            levelCompleteN.setTextColor(1, 1, 1, 1)
            levelCompleteN.setSlant(0.1)
            levelCompleteN.setShadow(0.03)
            levelCompleteN.setShadowColor(0, 0, 200, 1)
            # levelN.setFrameAsMargin(0, 0, 0, 0)
            levelCompleteN.setFrameColor(200, 0, 0, 1)
            levelCompleteN.setFrameLineWidth(5.0)
            # textNp.node().setGlyphShift(1.0)
            textNodePath = self.aspect2d.attachNewNode(levelCompleteN)
            textNodePath.setPos(-0.6, 1.5, 0.5)
            textNodePath.setScale(0.2)
            if self.levelCompleteSound2.status() != self.levelCompleteSound2.PLAYING:
                self.levelCompleteSound2.play()
        else:
            pass

    def coinScoreDisplay2(self):
        textNp = self.aspect2d.find('coin-score')
        textNp.node().clearText()
        textNp.node().setText(str("Coins: " + str(self.coinsCollected2)))



ecco = EccoGame()
ecco.run()


