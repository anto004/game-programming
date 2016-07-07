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
        self.sizescale = 0.6
        self.loadPlanets()
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

    def loadPlanets(self):
        # Here, inside our class, is where we are creating the loadPlanets function
        # For now we are just loading the star-field and sun. In the next step we
        # will load all of the planets

        # Loading objects in Panda is done via the command loader.loadModel, which
        # takes one argument, the path to the model file. Models in Panda come in
        # two types, .egg (which is readable in a text editor), and .bam (which is
        # not readable but makes smaller files). When you load a file you leave the
        # extension off so that it can choose the right version

        # Load model returns a NodePath, which you can think of as an object
        # containing your model

        # Here we load the sky model. For all the planets we will use the same
        # sphere model and simply change textures. However, even though the sky is
        # a sphere, it is different from the planet model because its polygons
        # (which are always one-sided in Panda) face inside the sphere instead of
        # outside (this is known as a model with reversed normals). Because of
        # that it has to be a separate model.
        self.sky = loader.loadModel("models/sky/solar_sky_sphere")

        # After the object is loaded, it must be placed in the scene. We do this by
        # changing the parent of self.sky to render, which is a special NodePath.
        # Each frame, Panda starts with render and renders everything attached to
        # it.
        self.sky.reparentTo(render)

        # You can set the position, orientation, and scale on a NodePath the same
        # way that you set those properties on the camera. In fact, the camera is
        # just another special NodePath
        self.sky.setScale(40)

        # Very often, the egg file will know what textures are needed and load them
        # automatically. But sometimes we want to set our textures manually, (for
        # instance we want to put different textures on the same planet model)
        # Loading textures works the same way as loading models, but instead of
        # calling loader.loadModel, we call loader.loadTexture
        self.sky_tex = loader.loadTexture("models/sky/stars_1k_tex.jpg")

        # Finally, the following line sets our new sky texture on our sky model.
        # The second argument must be one or the command will be ignored.
        self.sky.setTexture(self.sky_tex, 1)

        # Now we load the sun.
        self.sun = loader.loadModel("models/sky/planet_sphere")
        # Now we repeat our other steps
        self.sun.reparentTo(render)
        self.sun_tex = loader.loadTexture("models/sky/sun_1k_tex.jpg")
        self.sun.setTexture(self.sun_tex, 1)
        # The sun is really much bigger than
        self.sun.setScale(2 * self.sizescale)
        # this, but to be able to see the
        # planets we're making it smaller

    # end loadPlanets()

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
