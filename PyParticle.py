import math
import random


def calculate_vectors(pos_queue):
    if (len(pos_queue) == 1):
        return (0, 0)
    for num in range(len(pos_queue) - 1, 0, -1):
        dx = pos_queue[num][0] - pos_queue[num - 1][0]
        dy = pos_queue[num][1] - pos_queue[num - 1][1]
        # pdb.set_trace()

        angle = math.atan2(dy, dx) + 0.5 * math.pi
        speed = math.hypot(dx, dy) * 0.01
        print(speed, angle)
        return speed, angle


def calculate_speed_angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx) + 0.5 * math.pi
    speed = math.hypot(dx, dy) * 0.01
    return speed, angle


def addVectors(angle1, length1, angle2, length2):
    """ Returns the sum of two vectors """

    x = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y = math.cos(angle1) * length1 + math.cos(angle2) * length2

    angle = 0.5 * math.pi - math.atan2(y, x)
    length = math.hypot(x, y)

    return (angle, length)


def combine(p1, p2):
    if math.hypot(p1.x - p2.x, p1.y - p2.y) < p1.size + p2.size:
        total_mass = p1.mass + p2.mass
        p1.x = (p1.x * p1.mass + p2.x * p2.mass) / total_mass
        p1.y = (p1.y * p1.mass + p2.y * p2.mass) / total_mass
        (p1.angle, p1.speed) = addVectors(p1.angle, p1.speed * p1.mass / total_mass,
                                          p2.angle, p2.speed * p2.mass / total_mass)
        p1.speed *= (p1.elasticity * p2.elasticity)
        p1.mass += p2.mass
        p1.collide_with = p2


def collide(p1, p2):
    """ Tests whether two particles overlap
        If they do, make them bounce, i.e. update their angle, speed and position """

    dx = p1.x - p2.x
    dy = p1.y - p2.y

    dist = math.hypot(dx, dy)
    if dist < p1.size + p2.size:
        angle = math.atan2(dy, dx) + 0.5 * math.pi
        total_mass = p1.mass + p2.mass

        (p1.angle, p1.speed) = addVectors((p1.angle, p1.speed * (p1.mass - p2.mass) / total_mass),
                                          (angle, 2 * p2.speed * p2.mass / total_mass))
        (p2.angle, p2.speed) = addVectors((p2.angle, p2.speed * (p2.mass - p1.mass) / total_mass),
                                          (angle + math.pi, 2 * p1.speed * p1.mass / total_mass))
        elasticity = p1.elasticity * p2.elasticity
        p1.speed *= elasticity
        p2.speed *= elasticity

        overlap = 0.5 * (p1.size + p2.size - dist + 1)
        p1.x += math.sin(angle) * overlap
        p1.y -= math.cos(angle) * overlap
        p2.x -= math.sin(angle) * overlap
        p2.y += math.cos(angle) * overlap


class Particle:
    """ A circular object with a velocity, size and mass """

    def __init__(self, x, y, size, mass=1):
        self.x = x
        self.y = y
        self.size = size
        self.colour = (0, 0, 255)
        self.thickness = 0
        self.speed = 0
        self.angle = 0
        self.mass = mass
        self.drag = 1
        self.elasticity = 1

    def move(self):
        """ Update position based on speed, angle """

        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed

    def experienceDrag(self):
        self.speed *= self.drag

    def mouseMove(self, x, y):
        """ Change angle and speed to move towards a given point """
        dx = x - self.x
        dy = y - self.y
        self.angle = 0.5 * math.pi + math.atan2(dy, dx)
        self.speed = math.hypot(dx, dy) * 0.1

    def move_particle_W_mouse(self, x, y):
        """ Change angle and speed to move towards a given point """
        self.x = x
        self.y = y

    def accelerate(self, vector):
        """ Change angle and speed by a given vector """
        (self.angle, self.speed) = addVectors(self.angle, self.speed, *vector)

    def attract(self, other):
        """" Change velocity based on gravatational attraction between two particle"""

        dx = (self.x - other.x)
        dy = (self.y - other.y)
        dist = math.hypot(dx, dy)

        if dist < self.size + other.size:
            return True

        theta = math.atan2(dy, dx)
        force = 0.2 * self.mass * other.mass / dist ** 2
        self.accelerate((theta - 0.5 * math.pi, force / self.mass))
        other.accelerate((theta + 0.5 * math.pi, force / other.mass))

class Spring:
    def __init__(self, p1, p2, length=50, strength=0.5):
        self.p1 = p1
        self.p2 = p2
        self.length = length
        self.strength = strength

    def update(self):
        dx = self.p1.x - self.p2.x
        dy = self.p1.y - self.p2.y
        dist = math.hypot(dx, dy)
        theta = math.atan2(dy, dx)
        force = (self.length - dist) * self.strength

        self.p1.accelerate((theta + 0.5 * math.pi, force / self.p1.mass))
        self.p2.accelerate((theta - 0.5 * math.pi, force / self.p2.mass))



class Environment:
    """ Defines the boundary of a simulation and its properties """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.springs = []

        self.colour = (255, 255, 255)
        self.mass_of_air = 0.2
        self.elasticity = 1
        self.acceleration = (0, 0)

        self.particle_functions1 = []
        self.particle_functions2 = []
        self.function_dict = {
            'move': (1, lambda p: p.move()),
            'drag': (1, lambda p: p.experienceDrag()),
            'bounce': (1, lambda p: self.bounce(p)),
            'no_boundry': (1, lambda p: self.no_boundries(p)),
            'accelerate': (1, lambda p: p.accelerate(self.acceleration)),
            # 'mouse_move': (1, lambda p: p.mouseMove(x,y)),
            'collide': (2, lambda p1, p2: collide(p1, p2)),
            'combine': (2, lambda p1, p2: combine(p1, p2)),
            'attract': (2, lambda p1, p2: p1.attract(p2))}

    def addSpring(self, p1, p2, length=50, strength=0.5):
        """ Add a spring between particles p1 and p2 """
        self.springs.append(Spring(self.particles[p1], self.particles[p2], length, strength))

    def addFunctions(self, function_list):
        for func in function_list:
            (n, f) = self.function_dict.get(func, (-1, None))
            if n == 1:
                self.particle_functions1.append(f)
            elif n == 2:
                self.particle_functions2.append(f)
            else:
                print
                "No such function: %s" % f

    def addParticles(self, n=1, **kargs):
        """ Add n particles with properties given by keyword arguments """

        for i in range(n):
            size = kargs.get('size', random.randint(10, 20))
            mass = kargs.get('mass', random.randint(100, 10000))
            x = kargs.get('x', random.uniform(size, self.width - size))
            y = kargs.get('y', random.uniform(size, self.height - size))

            particle = Particle(x, y, size, mass)
            particle.speed = kargs.get('speed', random.random())
            particle.angle = kargs.get('angle', random.uniform(0, math.pi * 2))
            particle.colour = kargs.get('colour', (0, 0, 255))
            particle.elasticity = kargs.get('elasticity', 1)
            particle.drag = (particle.mass / (particle.mass + self.mass_of_air)) ** particle.size

            self.particles.append(particle)

    def update(self, x=None, y=None):
        """  Moves particles and tests for collisions with the walls and each other """
        for spring in self.springs:
            spring.update()

        for i, particle in enumerate(self.particles):
            if 'chosen' in particle.__dict__:
                if particle.chosen:  # The particle is chosen while the mouse is still clicking the particle
                    particle.move_particle_W_mouse(x, y)
                    speed,angle = calculate_speed_angle(particle.dq[-2][0], particle.dq[-2][1],particle.dq[-1][0], particle.dq[-1][1])
                    particle.speed_dq.append((speed,angle))
                else:  # the particle is chosen but no longer clicked on
                    # for calculating speed 
                    particle.speed, particle.angle = calculate_speed_angle(particle.dq[-15][0], particle.dq[-15][1],particle.dq[-10][0], particle.dq[-1][1])
                    del particle.__dict__['chosen']

            for f in self.particle_functions1:
                f(particle)
            for particle2 in self.particles[i + 1:]:
                for f in self.particle_functions2:
                    f(particle, particle2)

    def bounce(self, particle):
        """ Tests whether a particle has hit the boundary of the environment """

        if particle.x > self.width - particle.size:
            particle.x = 2 * (self.width - particle.size) - particle.x
            particle.angle = - particle.angle
            particle.speed *= self.elasticity*particle.elasticity

        elif particle.x < particle.size:
            particle.x = 2 * particle.size - particle.x
            particle.angle = - particle.angle
            particle.speed *= self.elasticity*particle.elasticity

        if particle.y > self.height - particle.size:
            particle.y = 2 * (self.height - particle.size) - particle.y
            particle.angle = math.pi - particle.angle
            particle.speed *= self.elasticity*particle.elasticity
            print(self.elasticity,particle.speed)

        elif particle.y < particle.size:
            particle.y = 2 * particle.size - particle.y
            particle.angle = math.pi - particle.angle
            particle.speed *= self.elasticity*particle.elasticity




    def no_boundries(self, particle):
        """ when particle hits wall it comes out the other side"""

        if particle.x > self.width - particle.size and (0 < particle.angle < math.pi):
            particle.x = particle.x + particle.size - self.width

        elif particle.x < particle.size and (math.pi < particle.angle < math.pi * 2):
            particle.x = (particle.x - particle.size) + self.width

        if particle.y > self.height - particle.size and (math.pi * 0.5 < particle.angle < math.pi * 1.5):
            particle.y = particle.y + particle.size - self.height

        elif particle.y < particle.size and (
                math.pi * 1.5 < particle.angle <= math.pi * 2 or 0 <= particle.angle <= math.pi * 0.5):
            particle.y = self.height - particle.size

    def findParticle(self, x, y):
        """ Returns any particle that occupies position x, y """

        for particle in self.particles:
            if math.hypot(particle.x - x, particle.y - y) <= particle.size:
                return particle
        return None


