from direct.gui.OnscreenText import OnscreenText, TextNode
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from math import pi, sin, cos
from panda3d.core import Vec3
from panda3d.core import Point3
from panda3d.core import TransparencyAttrib

from Physics import PhysicsModeler

class BouncingBall(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.title = OnscreenText(
            text="Ecco",
            parent=base.a2dBottomRight, align=TextNode.A_right,
            style=1, fg=(1, 1, 1, 1), pos=(-0.1, 0.1), scale=.07)
        base.setBackgroundColor(0, 0, 0)
        self.setup()
        self.setupRoom()
        # disable default camera control
        base.disableMouse()
        # position camera
        self.camera.setPos(50, -20, 10)

        # Add the update-and-render procedure to the task manager.
        #self.taskMgr.add(self.updateAndRender, "updateAndRender")
        self.taskMgr.add(self.cameraPosition, "Camera Positioning")
        #self.smileyFace.setPos(self.mover.location)
        self.smileyFace2 = self.loader.loadModel("models/lack")
        self.smileyFace2.reparentTo(self.render)
        self.smileyFace2.setPos(60, -70, 0)
        self.smileyFace2.setScale(2)

    def setupRoom(self):
        self.floor = self.loader.loadModel("models/misc/rgbCube")
        self.floor.reparentTo(self.render)
        self.floor.setScale(100, 5, 1)
        self.floor.setPos(0, -10, -50)

        self.leftWall = self.loader.loadModel("models/misc/rgbCube")
        self.leftWall.setScale(1, 100, 150)
        self.leftWall.setPos(-20, 0, -30)
        self.leftWall.reparentTo(self.render)

    def setup(self):
        self.smileyFace = self.loader.loadModel("models/smiley")
        self.smileyFace.reparentTo(self.render)
        location = Point3(50, -50, 0)
        self.smileyFace.setPos(location)
        self.smileyFace.setScale(2)
        smileyFaceMass = 25.0
        self.mover = PhysicsModeler(mass=smileyFaceMass, location = location)

    def updateAndRender(self, task):
        gravity = Vec3(0, 0, self.mover.mass * -0.0001)

        self.mover.applyForce(gravity)
        self.mover.update()
        self.smileyFace.setPos(self.mover.location)

        return Task.cont
    #testing camera position
    def cameraPosition(self, task):
        self.camera.setPos(0, task.time * -20, 10)
        print "task.time " + str(task.time *30)
        return Task.cont


simulation = BouncingBall()
simulation.run()
