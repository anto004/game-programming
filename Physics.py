from panda3d.core import Vec3
from panda3d.core import Point3

class PhysicsModeler():
    def __init__(self, mass=1, location = Point3.zero(), velocity=Vec3.zero(), acceleration=Vec3.zero()):
        # instance variables
        self.mass = mass
        self.location = location
        self.velocity = velocity
        self.acceleration = acceleration

    def applyForce(self, force):
        self.acceleration = self.acceleration + (force/self.mass)

    def update(self):
        self.velocity = self.velocity + self.acceleration
        self.location = self.location + self.velocity
        self.acceleration = Vec3.zero()
