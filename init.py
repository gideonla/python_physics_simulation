# -*- coding: utf-8 -*-
"""Example Google style docstrings.

Testing out physics simulations using python.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension
"""

import math
import random
from collections import deque as dq

import pygame

# definition block
(width, height) = (500, 500)  # screen size
background_colour = (255, 255, 255)
number_of_particles = 2
gravity = (math.pi, 0.001)
elasticity = 0.9  # how much elastic energy the ball keeps after collision
mouse_position_mem = dq(maxlen=5)  # save the last five positions
mouse_vector_mem = dq(maxlen=5)  # save the last five positions
mass_of_air = 0.2


def calculate_vectors(pos_queue):
    ret_queu = dq(maxlen=5)
    if (len(pos_queue) == 1):
        ret_queu.append((0, 0))
        return ret_queu
    for num in range(len(pos_queue) - 1, 0, -1):
        dx = pos_queue[num][0] - pos_queue[num - 1][0]
        dy = pos_queue[num][1] - pos_queue[num - 1][1]
        angle = math.atan2(dy, dx) + 0.5 * math.pi
        speed = math.hypot(dx, dy) * 0.1
        ret_queu.append((speed, angle))
        # pdb.set_trace()
    return ret_queu


def addVectors(angle1, length1, angle2, length2):
    x = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y = math.cos(angle1) * length1 + math.cos(angle2) * length2
    length = math.hypot(x, y)
    angle = 0.5 * math.pi - math.atan2(y, x)
    return (angle, length)


def findParticle(particles, x, y):
    # print(x, y)
    for p in particles:
        if math.hypot(p.x - x, p.y - y) <= p.size:
            return p


def collide(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y

    dist = math.hypot(dx, dy)
    if dist < p1.size + p2.size:
        angle = math.atan2(dy, dx) + 0.5 * math.pi
        total_mass = p1.mass + p2.mass
        (p1.angle, p1.speed) = addVectors(p1.angle, p1.speed * (p1.mass - p2.mass) / total_mass,
                                          angle, 2 * p2.speed * p2.mass / total_mass)
        (p2.angle, p2.speed) = addVectors(p2.angle, p2.speed * (p2.mass - p1.mass) / total_mass,
                                          angle + math.pi, 2 * p1.speed * p1.mass / total_mass)
        p1.speed *= elasticity
        p2.speed *= elasticity
        overlap = 0.5 * (p1.size + p2.size - dist + 1)
        p1.x += math.sin(angle) * overlap
        p1.y -= math.cos(angle) * overlap
        p2.x -= math.sin(angle) * overlap
        p2.y += math.cos(angle) * overlap

my_particles = []


class Particle:
    def __init__(self, position, size, speed, angle, mass=1, color=(0, 0, 255)):
        self.x, self.y = position
        self.size = size
        self.colour = color
        self.thickness = 1
        self.speed = speed
        self.angle = angle
        self.mass = mass
        self.drag = (self.mass / (self.mass + mass_of_air)) ** self.size

    def display(self):
        # pdb.set_trace()
        pygame.draw.circle(screen, self.colour, (int(self.x), int(self.y)), self.size, self.thickness)

    def move(self):
        (self.angle, self.speed) = addVectors(self.angle, self.speed, *gravity)
        self.speed *= self.drag
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed

    def bounce(self):  # detect collisions with the walls
        if self.x > width - self.size:
            self.x = 2 * (width - self.size) - self.x
            self.angle = - self.angle
            self.speed *= elasticity
        elif self.x < self.size:
            self.x = 2 * self.size - self.x
            self.angle = - self.angle
            self.speed *= elasticity
        if self.y > height - self.size:
            self.y = 2 * (height - self.size) - self.y
            self.angle = math.pi - self.angle
            self.speed *= elasticity
        elif self.y < self.size:
            self.y = 2 * self.size - self.y
            self.angle = math.pi - self.angle
            self.speed *= elasticity


screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Tutorial 1')  # change title of window

#generate particles
for n in range(number_of_particles):
    size = random.randint(10, 20)
    density = random.randint(1, 20)
    x = random.randint(size, width - size)
    y = random.randint(size, height - size)
    colour = (200 - density * 10, 200 - density * 10, 200 - density * 10)
    particle = Particle((x, y), size, 0, 0, density * size ** 2, color=colour)  # calculate mass from density and size
    # pdb.set_trace()
    particle.speed = 0
    particle.angle = random.uniform(0, math.pi * 2)

    my_particles.append(particle)

# pygame.draw.circle(screen, (0, 0, 255), (150, 50), 15, 1)

running = True
(mouseX, mouseY) = pygame.mouse.get_pos()
selected_particle = None
button_pressesd = 0
my_file_handle = open("debug_log.txt", mode="w", encoding="utf-8")
mouse_position_mem.append((0, 0))
while running:
    if not (mouse_position_mem[-1] == pygame.mouse.get_pos()):
        mouse_position_mem.append(pygame.mouse.get_pos())
    # print(pygame.mouse.get_pos())

    mouse_vector_mem = calculate_vectors(mouse_position_mem)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            (mouseX, mouseY) = pygame.mouse.get_pos()
            selected_particle = findParticle(my_particles, mouseX, mouseY)
            button_pressesd = 1

        if event.type == pygame.MOUSEBUTTONUP:
            button_pressesd = 0
            prev_mouse_X, prev_mouse_Y = pygame.mouse.get_pos()

            # selected_particle = None
    # print((mouseX, mouseY))

    screen.fill(background_colour)

    for i, particle in enumerate(my_particles):
        if particle != selected_particle:
            particle.move()
            particle.bounce()
            for particle2 in my_particles[i + 1:]:
                collide(particle, particle2)
        particle.display()

    if selected_particle and button_pressesd:
        (mouseX, mouseY) = pygame.mouse.get_pos()
        selected_particle.x = mouseX
        selected_particle.y = mouseY

    elif selected_particle and not button_pressesd:
        (mouseX, mouseY) = pygame.mouse.get_pos()
        dx = prev_mouse_X - mouseX
        dy = prev_mouse_Y - mouseY
        selected_particle.angle = mouse_vector_mem[-1][1]  # get angle from tuple
        selected_particle.speed = mouse_vector_mem[-1][0]  # get speed from tuple
        selected_particle = None
    pygame.display.flip()
print(mouse_position_mem)
print(mouse_vector_mem)
