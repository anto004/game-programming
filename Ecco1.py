from direct.gui.OnscreenText import OnscreenText, TextNode
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from math import pi, sin, cos
from panda3d.core import Vec3
from panda3d.core import Point3
from panda3d.core import TransparencyAttrib
from Physics import PhysicsModeler
from direct.showbase.InputStateGlobal import inputState
from panda3d.core import Vec3
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletDebugNode
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
        # disable default camera control
        # base.disableMouse()
        # # position camera
        # self.camera.setPos(0, -200, 10)

        # create bullet world
        self.debugNP = self.render.attachNewNode(BulletDebugNode('Debug'))
        self.debugNP.show()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())

        self.setupFloor()
        self.setupCharacter()

        self.title = addTitle("Panda3D - Ecco ")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[Left Arrow]: Turn Ecco Left")
        self.inst3 = addInstructions(0.85, "[Right Arrow]: Turn Ecco Right")
        self.inst4 = addInstructions(0.80, "[Up Arrow]: Jump Ecco")

        inputState.watchWithModifiers('esc', 'escape')
        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('right', 'd')
        inputState.watchWithModifiers('turnLeft', 'q')
        inputState.watchWithModifiers('turnRight', 'e')
        inputState.watchWithModifiers('cam-left', 'z')
        inputState.watchWithModifiers('cam-right', 'x')
        inputState.watchWithModifiers('cam-forward', 'c')
        inputState.watchWithModifiers('cam-backward', 'v')

        taskMgr.add(self.update, "update")

        # Game state variables
        self.isMoving = False

        # Set up the camera
        self.disableMouse()
        self.camera.setPos(self.ecco.getX(), self.ecco.getY() + 10, 2)

    def setupFloor(self):
        # Floor
        floorShape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(floorShape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setPos(0, 0, 0)
        self.world.attachRigidBody(floorNode)
        floorModel = self.loader.loadModel("models/misc/rgbCube")
        floorModel.setScale(30, 1000, 1)
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(self.render)

    def setupCharacter(self):
        # Sphere
        shape = BulletSphereShape(13)
        node = BulletRigidBodyNode('Box')
        node.setMass(10.0)
        node.addShape(shape)
        self.sphere = self.render.attachNewNode(node)
        self.sphere.setPos(0, 0, 50)
        self.world.attachRigidBody(node)

        #self.ecco = self.loader.loadModel("models/lack")
        self.ecco = Actor('models/lack.egg',{
            'run' : 'models/lack-run.egg',
            'jump' : 'models/lack-jump.egg',
            'damage' : 'models/lack-damage.egg'})
        self.ecco.reparentTo(self.sphere)
        self.ecco.setScale(1)

        # Create a floater object, which floats 2 units above ralph.  We
        # use this as a target for the camera to look at.
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.ecco)
        self.floater.setZ(2.0)

    def update(self, task):
        self.processInput()
        dt = globalClock.getDt()
        self.world.doPhysics(dt, 10, 1 / 180.0)
        self.ecco.loop('run')
        return task.cont

    def processInput(self):
        force = Vec3(0, 0, 0)
        torque = Vec3(0, 0, 0)

        dt = globalClock.getDt()

        if inputState.isSet('esc'): sys.exit()
        if inputState.isSet('forward'): force.setY(1.0)
        if inputState.isSet('reverse'): force.setY(-1.0)
        if inputState.isSet('left'):    force.setX(-1.0)
        if inputState.isSet('right'):   force.setX(1.0)
        if inputState.isSet('turnLeft'):  torque.setZ(1.0)
        if inputState.isSet('turnRight'): torque.setZ(-1.0)
        if inputState.isSet('cam-left'): self.camera.setX(self.camera, -20 * dt)
        if inputState.isSet('cam-right'): self.camera.setX(self.camera, +20 * dt)
        if inputState.isSet('cam-forward'): self.camera.setY(self.camera, -200 * dt)
        if inputState.isSet('cam-backward'): self.camera.setY(self.camera, +200 * dt)

        force *= 60.0
        torque *= 20.0

        self.sphere.node().setActive(True)
        self.sphere.node().applyCentralForce(force)
        self.sphere.node().applyTorque(torque)



simulation = EccoGame()
simulation.run()
