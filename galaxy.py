"""2D galaxy simulation.

Testing out physics simulations using python.

Example:
        $ python galaxy.py

Todo:
    * Make is so as long as mouse button is pressed particle doesn't fly out
"""
import math
import random

import pygame

import PyParticle

(width, height) = (400, 400)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Star formation')

universe = PyParticle.Environment(width, height)
universe.colour = (0, 0, 0)
universe.addFunctions(['move', 'attract', 'combine', 'no_boundry'])


def calculateRadius(mass):
    return 0.5 * mass ** (0.5)


def floatRgb(mag, cmin, cmax):
    """ Return a tuple of floats between 0 and 1 for R, G, and B. """
    # Normalize to 0-1
    try:
        x = float(mag - cmin) / (cmax - cmin)
    except ZeroDivisionError:
        x = 0.5  # cmax == cmin
    blue = min((max((4 * (0.75 - x), 0.)), 1.))
    red = min((max((4 * (x - 0.25), 0.)), 1.))
    green = min((max((4 * math.fabs(x - 0.5) - 1., 0.)), 1.))
    return int(red * 255), int(green * 255), int(blue * 255)


for p in range(200):
    particle_mass = random.randint(1, 10)
    particle_size = calculateRadius(particle_mass)
    universe.addParticles(mass=particle_mass, speed=0.01, size=particle_size, colour=(255, 255, 255))

running = True
mouseX, mouseY = None, None
button_pressed = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN or button_pressed:
            button_pressed = True
            print("mouse pressed")
            (mouseX, mouseY) = pygame.mouse.get_pos()
            selected_particle = universe.findParticle(mouseX, mouseY)
        if event.type == pygame.MOUSEBUTTONUP:
            button_pressed = False

    universe.update(mouseX, mouseY)
    screen.fill(universe.colour)

    particles_to_remove = []
    for p in universe.particles:
        if 'collide_with' in p.__dict__:
            particles_to_remove.append(p.collide_with)
            p.size = calculateRadius(p.mass)
            del p.__dict__['collide_with']
        p.colour = floatRgb(p.size, 0, 10)
        # pdb.set_trace()

        if p.size < 2:
            pygame.draw.rect(screen, p.colour, (int(p.x), int(p.y), 2, 2))
        else:
            pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), int(p.size), 0)

    for p in particles_to_remove:
        try:
            universe.particles.remove(p)
        except ValueError:
            continue

    pygame.display.flip()
