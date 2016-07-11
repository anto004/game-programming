from direct.gui.OnscreenText import OnscreenText, TextNode
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
from panda3d.bullet import ZUp
import sys
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from direct.actor.Actor import Actor


def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1),
                        pos=(1.3, -0.95), align=TextNode.ARight, scale=.07)


def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale=.05)

class EccoGame(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        base.setBackgroundColor(0, 0, 0)
        self.sizescale = 0.6
        self.setupWorld()
        self.setupFloor()
        self.setupCharacter()

        self.title = addTitle("Panda3D - Ecco ")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[Left key]: Turn Ecco Left")
        self.inst3 = addInstructions(0.85, "[Right key]: Turn Ecco Right")
        self.inst4 = addInstructions(0.80, "[Space]: Jump Ecco")

        inputState.watchWithModifiers('esc', 'escape')
        inputState.watchWithModifiers('arrow_up', 'w')
        inputState.watchWithModifiers('arrow_left', 'arrow_left')
        inputState.watchWithModifiers('arrow_right', 'arrow_right')
        inputState.watchWithModifiers('pause', 'p')
        inputState.watchWithModifiers('jump', 'space')

        inputState.watchWithModifiers('cam-left', 'z')
        inputState.watchWithModifiers('cam-right', 'x')
        inputState.watchWithModifiers('cam-forward', 'c')
        inputState.watchWithModifiers('cam-backward', 'v')

        taskMgr.add(self.update, "update")

        # Game state variables
        self.isMoving = False

        # Create a floater object, which floats 2 units above ralph.  We
        # use this as a target for the camera to look at.

        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.characterNP)
        self.floater.setZ(2.0)

        # Set up the camera
        self.disableMouse()
        self.camera.setPos(self.characterNP.getX(), self.characterNP.getY() + 10, 5)
        self.setupSound()

    def update(self, task):
        self.setupSky()
        self.setUpCamera()
        self.processInput()
        dt = globalClock.getDt()
        self.world.doPhysics(dt, 10, 1 / 180.0)
        return task.cont

    def setupWorld(self):
        # create bullet world
        self.debugNP = self.render.attachNewNode(BulletDebugNode('Debug'))
        self.debugNP.show()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -900.81))
        self.world.setDebugNode(self.debugNP.node())

    def setupSky(self):
        # Load the model for the sky
        self.sky = loader.loadModel("models/sky/solar_sky_sphere")
        # Load the texture for the sky.
        self.sky_tex = loader.loadTexture("models/sky/stars_1k_tex.jpg")
        # Set the sky texture to the sky model
        self.sky.setTexture(self.sky_tex, 1)
        # Parent the sky model to the render node so that the sky is rendered
        self.sky.reparentTo(self.render)
        # Scale the size of the sky.
        self.sky.setScale(40000)
        self.sky.setPos(self.characterNP.getX(), self.characterNP.getY() + 10000, 0)

    def setupSound(self):
        # Set up sound
        mySound = base.loader.loadSfx("sounds/Farm Morning.ogg")
        self.footsteps = base.loader.loadSfx("sounds/Footsteps_on_Cement-Tim_Fryer-870410055.ogg")
        mySound.play()
        mySound.setVolume(1.5)
    def setupFloor(self):
        # Floor
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        floorNP = self.render.attachNewNode(BulletRigidBodyNode('Floor'))
        floorNP.node().addShape(shape)
        floorNP.setPos(0, 0, -300)
        floorNP.setCollideMask(BitMask32.allOn())
        self.world.attachRigidBody(floorNP.node())

        #origin = Point3(2, 0, 0)
        size = Vec3(10, 10000, 1)
        shape = BulletBoxShape(size * 0.55)
        stairNP = self.render.attachNewNode(BulletRigidBodyNode('Stair%i' % 1))
        stairNP.node().addShape(shape)
        stairNP.setPos(0, 0, 0)
        stairNP.setCollideMask(BitMask32.allOn())

        modelNP = loader.loadModel('models/box.egg')
        modelNP.reparentTo(stairNP)
        #modelNP.setPos(0, 0, 0)
        modelNP.setPos(-size.x / 2.0, -size.y / 2.0, -size.z / 2.0)
        modelNP.setScale(size)
        self.world.attachRigidBody(stairNP.node())


    def setupCharacter(self):
        # Character
        h = 10.75
        w = 1
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)

        self.character = BulletCharacterControllerNode(shape, 0.4, 'Player')
        #    self.character.setMass(1.0)
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
        camvec.setZ(0)
        camdist = camvec.length()
        print self.characterNP.getPos()
        print "and"
        print camdist
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
        if inputState.isSet('arrow_up'): speed.setY(20.0)
        if inputState.isSet('arrow_left'):
            speed.setX(-35.0)
            #omega = 120.0
        if inputState.isSet('arrow_right'):
            speed.setX(35.0)
            #omega = -120.0

        if inputState.isSet('cam-left'): self.camera.setX(self.camera, -20 * dt)
        if inputState.isSet('cam-right'): self.camera.setX(self.camera, +20 * dt)
        if inputState.isSet('cam-forward'): self.camera.setY(self.camera, -200 * dt)
        if inputState.isSet('cam-backward'): self.camera.setY(self.camera, +200 * dt)

        if self.isMoving is False:
            self.ecco.loop("run")
            self.isMoving = True
        speed.setY(50.0)
        # self.footsteps.play()
        # self.footsteps.setVolume(10)
        #self.character.setAngularMovement(omega)
        self.character.setLinearMovement(speed, True)
        print "omega:"+str(omega)

simulation = EccoGame()
simulation.run()
